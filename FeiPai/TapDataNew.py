import yaml,requests,json
from typing import Dict
from Mymodule.ConnectMysqlNew import ConnectMysql as useMysql



class TapDataGet:

    def __init__(self):
        # 加载配置和Cookie
        tap_conf_path = "conf/Tap.yaml"
        tap_cookie_path = "conf/TapCookie.txt"
        with open(tap_conf_path, "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)

        with open(tap_cookie_path, "r", encoding="utf-8") as fcookie:
            yaml_config["headers"]["cookie"] = fcookie.readline()
        self.headers = yaml_config["headers"]
        self.payload = yaml_config["payload"]
        self.db = None  # 延迟初始化

    def __enter__(self):
        """进入上下文时创建连接"""
        self.db = useMysql(connect_dict={"database": "leiting"})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时由ConnectMysql自动关闭连接"""
        pass  # 不要在此处关闭连接

    #抓取预约量
    def get_reserve(self, platform: str) -> None:
        """抓取预约数据并存入数据库"""
        base_url = (
            f"https://developer.taptap.cn/api/dashboard/v2/stats-by-day/reserve/cn?"
            f"developer_id={self.payload['developer_id']}&"
            f"app_id={self.payload['app_id']}&"
            f"start_date={self.payload['start_date']}&"
            f"end_date={self.payload['end_date']}&"
            f"platform={platform}"
        )
        try:
            res = requests.get(url=base_url,headers=self.headers)
            res.raise_for_status()  # 自动处理HTTP错误

            res_json = res.json()
            for day_data in res_json["data"]["list"]:
                # 构造数据字典
                where: Dict = {
                    "date": day_data["date"],
                    "platform": day_data["platform"],
                    "game": self.payload["game"]
                }

                set_data: Dict = {
                    "canceled_reserve": day_data["canceled_reserve"],
                    "canceled_reserve_dry": day_data["canceled_reserve_dry"],
                    "reserve": day_data["reserve"],
                    "reserve_dry": day_data["reserve_dry"],
                }

                # 使用新的insert_or_update方法
                with self.db:  # 通过上下文管理器管理事务
                    self.db.insert_or_update(
                        table="tapdata",
                        set_data=set_data,
                        where=where
                    )

            total = res_json["data"]["total"]
            print(f'{total["platform"]}：{total["reserve_dry"]}')



        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

        except json.JSONDecodeError:
            print("响应解析失败，原始内容:\n", res.text)

        except KeyError as e:
            print(f"数据字段缺失: {e}")

        except Exception as e:
            print(f"未知错误: {e}")

        # 新增上下文管理器支持 ----------------------------------



if __name__ == "__main__":
    platform_list = ["","ios","android","other"]
    for platform in platform_list:
        # 使用上下文管理器确保数据库连接关闭
        with TapDataGet() as tdg:  # 要求类必须实现 __enter__ 和 __exit__
            tdg.get_reserve(platform=platform)
