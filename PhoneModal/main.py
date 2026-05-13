from datetime import datetime
import json,os,requests
import openpyxl
from retrying import retry
import pandas as pd

class PhoneModel():
    def __init__(self):
        self.csv_info = 'models.csv'
        self.check_csv = '20250121_053404_20804_mtvbr.csv'
    def phoneinfo_read(self):
        phoneinfo_csv = pd.read_csv(self.csv_info)
        phoneinfo_dict = phoneinfo_csv.transpose().to_dict()
        phoneinfo = {}
        for index,detail_info in phoneinfo_dict.items():
            # print(index,detail_info)
            phoneinfo[detail_info["model"]] = {
                "dtype": detail_info["dtype"],
                "brand": detail_info["brand"],
                "brand_title": detail_info["brand_title"],
                "code": detail_info["code"],
                "code_alias": detail_info["code_alias"],
                "model_name": detail_info["model_name"],
                "ver_name": detail_info["ver_name"]
            }
        # print(phoneinfo)
        return phoneinfo
    def check_info(self):
        phoneinfo = self.phoneinfo_read()
        check_info = pd.read_csv(self.check_csv)
        check_info_reshape = check_info.transpose().to_dict()
        check_info_dict = {}
        for index,check_info in check_info_reshape.items():
            print(index,check_info)
            if phoneinfo.get(check_info["termin_info"], "无信息") == "无信息":
                pass
            else:
                # print(phoneinfo.get(check_info["termin_info"], "无信息")["dtype"])
                check_info_dict[index] = {
                    "termin_info": check_info["termin_info"],
                    "num": check_info["num"],
                    "dtype": phoneinfo.get(check_info["termin_info"],"无信息")["dtype"],
                    "brand": phoneinfo.get(check_info["termin_info"],"无信息")["brand"],
                    "brand_title": phoneinfo.get(check_info["termin_info"],"无信息")["brand_title"],
                    "code": phoneinfo.get(check_info["termin_info"],"无信息")["code"],
                    "code_alias": phoneinfo.get(check_info["termin_info"],"无信息")["code_alias"],
                    "model_name": phoneinfo.get(check_info["termin_info"],"无信息")["model_name"],
                    "ver_name": phoneinfo.get(check_info["termin_info"],"无信息")["ver_name"],
                }
        print(check_info_dict)
        check_info_dict_df = pd.DataFrame.from_dict(check_info_dict)
        check_info_dict_df.transpose().to_csv('termin_info.csv')

    def get_web_modelinfo(self,num):
        url = 'https://imei.org/brands/'+str(num)
        payload = {
            "_token": "TSnQR8RsmJPH3KMJcTYiBB4JaMaqsVCmSqwMRWeb"
        }
        headers = {
            # "accept": "*/*",
            # "accept-language": "zh-CN,zh;q=0.9",
            # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            # "priority": "u=1, i",
            # "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            # "sec-ch-ua-mobile": "?0",
            # "sec-ch-ua-platform": "\"macOS\"",
            # "sec-fetch-dest": "empty",
            # "sec-fetch-mode": "cors",
            # "sec-fetch-site": "same-origin",
            # "x-requested-with": "XMLHttpRequest",
            "cookie": "_ga=GA1.1.569516950.1737446264; fpestid=_GR2rcb7goo5vUC7U10BCMONfUkY7RT-7AwKGvOVPIfHQ0uWuYBOCCojlSsHcb7M5rptKw; _webpushrPageViews=3; XSRF-TOKEN=eyJpdiI6IkMxaHFuN1h2MjZxdW80NkM2WUZ4RlE9PSIsInZhbHVlIjoiWFN6MXI2aVJOZVdZOUNvTlhHRjF0Wk40Qlk2MUdoRXk2dlFcLzBKWTQyQ0FNT2VZblFNczFPaE5vVEJOaTJkVnUiLCJtYWMiOiI3MDM0ZjdhYTViOGFhN2FjYzc4MTE4MGI4YTRmZGI1MGFmZDlhMjE0OWQxZDI3OGJkYTVhYTM5NGY3MDZkMmI0In0%3D; imeiorg_session=eyJpdiI6InFtU1JQMHN0REdMb3RYd1BCKzJqZUE9PSIsInZhbHVlIjoieWQycDBISkU2Um1JXC8xeXRIY0ZZenNNWkExRjFVbjdGdGpOQkthaGVJS3p6cW1KTjJYRVZzM0owQjZndUJNTE0iLCJtYWMiOiIwODcyMDI4MTlhNGVjODVhMDMyYzI2ZGZjZDg5YmY5ODc2Y2Q0NGMzNjQ4NjJmMmNhMGVkYjZkZTJiZGVjZDdlIn0%3D; _ga_JLS5QDR60N=GS1.1.1737508946.5.1.1737508957.49.0.0",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://imei.org/zh/phone-model-lookup",
            # "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        res = requests.post(url=url, headers=headers, json=payload)
        res_json = json.loads(res.text)
        for i in res_json["phones"]:
            print(i)
        # print(res.text)


if __name__ == "__main__":
    PhoneModel().get_web_modelinfo(num=1)
    # device_name = "RMX3800"
    # print(phoneinfo[device_name])

