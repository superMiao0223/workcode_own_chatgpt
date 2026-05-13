import yaml,requests,json,os,math
from datetime import date,datetime
from typing import Dict
from Mymodule.ConnectMysqlNew import ConnectMysql as useMysql
import pandas as pd



class shushuData:

    def __init__(self):
        self.src_path = "src/shushu"
        self.product_name = "FlyingCard"
        self.default_date = datetime.strftime(datetime.today(),"%Y-%m-%d")
        with os.scandir(self.src_path) as entries:
            self.base_data_path = [entry.name for entry in entries if entry.is_file() and "base_data" in entry.name]

    def __enter__(self):
        """进入上下文时创建连接"""
        self.db = useMysql(connect_dict={"database": "leiting"})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时由ConnectMysql自动关闭连接"""
        pass
    def safe_convert(self, value, convert_type):
        """安全转换函数，处理带逗号的数字字符串"""
        try:
            if isinstance(value, str):
                value = value.replace(",", "")
            return convert_type(value) if value not in [None, "", "nan", "NaN"] else 0
        except (ValueError, TypeError, AttributeError):
            return 0  # 或者根据业务需求返回None或其他默认值

    def safe_divide(self, numerator, denominator):
        """安全除法，处理分母为零和NaN的情况"""
        try:
            if denominator == 0:
                return None
            result = numerator / denominator
            return None if math.isnan(result) else result
        except:
            return None

    def clean_data_for_mysql(self, data_dict):
        """清理字典中的NaN/None值，确保MySQL兼容"""
        cleaned = {}
        for k, v in data_dict.items():
            if isinstance(v, float) and math.isnan(v):
                cleaned[k] = None
            elif v is None:
                cleaned[k] = None
            else:
                cleaned[k] = v
        return cleaned

    # 基础数据入库
    def get_base_data(self):
        #获得文件夹中的文件
        for base_data_file in self.base_data_path:
            # print(base_data_file)
            df = pd.read_csv(self.src_path + "/" + base_data_file)
            df_dict = df.transpose().to_dict()
            # df_dict = df.to_dict()
            # print(df_dict)
            for index,df_data in df_dict.items():
                print(index,df_data)
                print(self.default_date)
                where: Dict = {
                    "productName": self.product_name,
                    "date": df_data.get("date", self.default_date),
                    "dateType": "day",  # month/week/day
                    "country": "中国",
                    "area": "0",
                    "timezone": "+08:00",
                    "tzType": 1,
                    "os": "GooglePlay",  # AppStore/GooglePlay/OneStore
                    "dataSort": "userID"  # account/device/userID等
                }
                set_data_base: Dict = {
                    "newUser": self.safe_convert(df_data.get("newUser", 0), int),
                    "activeUser": self.safe_convert(df_data.get("activeUser", 0), int),
                    "payUser": self.safe_convert(df_data.get("payUser", 0), int),
                    "activePayUser": self.safe_convert(df_data.get("activePayUser", 0), int),
                    "payNum": self.safe_convert(df_data.get("payNum", 0), float),
                    "payNumWeb": self.safe_convert(df_data.get("payNumWeb", 0), float),
                    "payUserNew": self.safe_convert(df_data.get("payUserNew", 0), int),
                    "payNumNew": self.safe_convert(df_data.get("payNumNew", 0), float),
                    "payUserNew2": self.safe_convert(df_data.get("payUserNew2", 0), int),
                    "payNum2": self.safe_convert(df_data.get("payNum2", 0), float),
                    "onlineTimeMin": self.safe_convert(df_data.get("onlineTimeMin", 0), float),
                    "onlineTimeMinNewUser": self.safe_convert(df_data.get("onlineTimeMinNewUser", 0), float),
                }
                set_data_base["oldUser"] = set_data_base["activeUser"] - set_data_base["newUser"]
                set_data_base["payUserOld"] = set_data_base["payUser"] - set_data_base["payUserNew"]
                set_data_base["payNumOld"] = set_data_base["payNum"] - set_data_base["payNumNew"]


                # set_data_metrics = set_data_base.copy()
                set_data_metrics = {
                    "payRate": self.safe_divide(set_data_base["payUser"], set_data_base["activeUser"]),
                    "ARPU": self.safe_divide(set_data_base["payNum"], set_data_base["activeUser"]),
                    "ARPPU": self.safe_divide(set_data_base["payNum"], set_data_base["payUser"]),
                    "payRateNew": self.safe_divide(set_data_base["payUserNew"], set_data_base["newUser"]),
                    "ARPUNew": self.safe_divide(set_data_base["payNumNew"], set_data_base["newUser"]),
                    "ARPPUNew": self.safe_divide(set_data_base["payNumNew"], set_data_base["payUserNew"]),
                    "payRateOld": self.safe_divide(set_data_base["payUserOld"], set_data_base["oldUser"]),
                    "ARPUOld": self.safe_divide(set_data_base["payNumOld"], set_data_base["oldUser"]),
                    "ARPPUOld": self.safe_divide(set_data_base["payNumOld"], set_data_base["payUserOld"]),
                }

                # 合并数据并清理
                set_data = {**set_data_base, **set_data_metrics}
                set_data = self.clean_data_for_mysql(set_data)
                # print(set_data)
                # 使用新的insert_or_update方法
                self.db.insert_or_update(
                    table="basedata",
                    set_data=set_data,
                    where=where
                )


    # def get_reserve(self, platform: str) -> None:
    #     """基础数据获取并入库"""
    #
    #     # 扫描文件夹中的文件
    #     base_url = (
    #         f"https://developer.taptap.cn/api/dashboard/v2/stats-by-day/reserve/cn?"
    #         f"developer_id={self.payload['developer_id']}&"
    #         f"app_id={self.payload['app_id']}&"
    #         f"start_date={self.payload['start_date']}&"
    #         f"end_date={self.payload['end_date']}&"
    #         f"platform={platform}"
    #     )
    #     try:
    #         res = requests.get(url=base_url,headers=self.headers)
    #         res.raise_for_status()  # 自动处理HTTP错误
    #
    #         res_json = res.json()
    #         for day_data in res_json["data"]["list"]:
    #             # 构造数据字典
    #             where: Dict = {
    #                 "date": day_data["date"],
    #                 "platform": day_data["platform"],
    #                 "game": self.payload["game"]
    #             }
    #
    #             set_data: Dict = {
    #                 "canceled_reserve": day_data["canceled_reserve"],
    #                 "canceled_reserve_dry": day_data["canceled_reserve_dry"],
    #                 "reserve": day_data["reserve"],
    #                 "reserve_dry": day_data["reserve_dry"],
    #             }
    #
    #             # 使用新的insert_or_update方法
    #             with self.db:  # 通过上下文管理器管理事务
    #                 self.db.insert_or_update(
    #                     table="tapdata",
    #                     set_data=set_data,
    #                     where=where
    #                 )
    #
    #         total = res_json["data"]["total"]
    #         print(f'{total["platform"]}：{total["reserve_dry"]}')
    #
    #
    #
    #     except requests.exceptions.RequestException as e:
    #         print(f"请求失败: {e}")
    #
    #     except json.JSONDecodeError:
    #         print("响应解析失败，原始内容:\n", res.text)
    #
    #     except KeyError as e:
    #         print(f"数据字段缺失: {e}")
    #
    #     except Exception as e:
    #         print(f"未知错误: {e}")



if __name__ == "__main__":
    with shushuData() as sd:
        sd.get_base_data()
    # platform_list = ["","ios","android","other"]
    # for platform in platform_list:
    #     # 使用上下文管理器确保数据库连接关闭
    #     with TapDataGet() as tdg:  # 要求类必须实现 __enter__ 和 __exit__
    #         tdg.get_reserve(platform=platform)
