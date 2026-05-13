import pymysql
from retrying import retry
from typing import Dict, Any, Optional


class ConnectMysql:
    """MySQL数据库操作封装类，支持插入、更新、查询及错误重试"""

    def __init__(self, connect_dict: Optional[Dict] = None, **kwargs):
        """
        初始化数据库连接
        :param connect_dict: 连接参数字典，可覆盖默认参数
        :param kwargs: 关键字参数，优先级高于connect_dict
        """
        # 合并连接参数，优先级：kwargs > connect_dict > 默认值
        self.connect_params = {
            "host": "localhost",
            "user": "root",
            "password": "Zqlmm0223!",
            "database": "ninjamustdie_global",
            "port": 3306,
            "charset": "utf8mb4",  # 新增默认字符集
        }
        if connect_dict:
            self.connect_params.update(connect_dict)
        self.connect_params.update(kwargs)  # 允许通过kwargs动态覆盖

        # 使用retrying装饰器实现连接重试
        self.db = self._connect_with_retry()

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def _connect_with_retry(self) -> pymysql.connections.Connection:
        """带重试机制的数据库连接方法"""
        return pymysql.connect(**self.connect_params)

    def _execute_sql(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        执行SQL语句的通用方法
        :param sql: 参数化SQL语句
        :param params: 参数元组
        :return: 影响的行数
        """
        with self.db.cursor() as cursor:
            try:
                affected_rows = cursor.execute(sql, params or ())
                self.db.commit()
                return affected_rows
            except Exception as e:
                self.db.rollback()
                raise RuntimeError(f"SQL执行失败: {e}") from e

    def insert_or_update(self, table: str, set_data: Dict, where: Dict) -> None:
        """
        插入或更新数据（UPSERT）
        当主键冲突时自动转为更新操作
        :param table: 表名
        :param set_data: 需要设置的数据字典
        :param where: 条件字典
        """
        # 构造INSERT部分
        merged_data = where.copy()
        merged_data.update(set_data)
        columns = [f"`{k}`" for k in merged_data.keys()]
        placeholders = ", ".join(["%s"] * len(merged_data))

        # 构造ON DUPLICATE KEY UPDATE部分
        update_clause = ", ".join([f"`{k}` = VALUES(`{k}`)" for k in set_data.keys()])

        sql = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """
        self._execute_sql(sql, tuple(merged_data.values()))

    def update(self, table: str, set_data: Dict, where: Dict) -> int:
        """
        安全的参数化更新方法
        :param table: 表名
        :param set_data: 设置字段字典
        :param where: 条件字段字典
        :return: 影响的行数
        """
        # 构造SET子句
        set_clause = ", ".join([f"`{k}` = %s" for k in set_data.keys()])
        set_values = tuple(set_data.values())

        # 构造WHERE子句
        where_clause = " AND ".join([f"`{k}` = %s" for k in where.keys()])
        where_values = tuple(where.values())

        sql = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
        return self._execute_sql(sql, set_values + where_values)

    def query(self, sql: str, params: Optional[tuple] = None) -> tuple:
        """
        通用查询方法
        :param sql: 参数化查询语句
        :param params: 参数元组
        :return: 查询结果元组
        """
        with self.db.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭连接"""
        if self.db:
            self.db.close()
            self.db = None  # 防止重复关闭

