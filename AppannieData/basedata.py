import random
import time

from Mymodule.ConnectMysql import ConnectMysql as useMysql
import json,yaml,requests
from datetime import datetime
from retrying import retry



class getAppAnnieBaseData(object):
    def __init__(self):
        self.apiconf_path = 'headers.yaml'
        with open(self.apiconf_path, "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        with open('cookie.txt','r',encoding='utf-8') as cookiefp:
            yaml_config["headers"]['Cookie'] = cookiefp.readline()
        self.headers = yaml_config["headers"]
        self.resUrl = 'https://www.data.ai/ajax/v2/query?query_identifier=app_intelligence_chart%24country'
        self.payload = yaml_config["payload"]
        self.resInfo = yaml_config["resInfo"]["getdataY"]

    def payload_rebulid(self):
        countryCodeList = list(self.getCountryCodeList().keys())
        for productInfo in self.resInfo:
            for factsType in productInfo["typeInfo"]:
                for shopType,shopInfo in productInfo["shopInfo"].items():
                    for product_id in shopInfo["product_id"]:
                        for countryCodeRange in range(0,len(countryCodeList),15):
                            # print(countryCodeRange)
                            self.payload["facets"] = [factsType]
                            self.payload["filters"]["date"]["between"] = productInfo["dateInfo"]
                            self.payload["filters"]["product_id"]["in"] = [int(product_id)]
                            self.payload["filters"]["country_code"]["in"] = countryCodeList[countryCodeRange:countryCodeRange+15]
                            self.payload["filters"]["device_code"]["equal"] = shopInfo["equal"]
                            self.payload["breakdowns"]["country_code"] = {}
                            self.payload["breakdowns"]["date"] = {}
                            # print(self.payload)
                            self.requests_to_appannie(payloadNew=self.payload,customer_name = productInfo["customerName"])
                            time.sleep(random.randint(2,5))


    @retry()
    def requests_to_appannie(self,payloadNew,customer_name):
        print(customer_name,payloadNew)
        res = requests.post(url=self.resUrl,headers=self.headers,json=payloadNew)
        # print(res.text)
        if res.status_code == 200:
            res_json = json.loads(res.text)
            for facts in res_json["data"]["facets"]:
                if facts.get("est_download__sum", facts.get("est_revenue__sum", None)) == None:
                    pass
                else:
                    whereDict = {
                        "date": datetime.strftime(datetime.fromtimestamp(facts["date"] / 1000), '%Y-%m-%d'),
                        "product_id": payloadNew["filters"]["product_id"]["in"][0],
                        "date_type": "day",
                        "device_code": payloadNew["filters"]["device_code"]["equal"],
                        "country_code": facts["country_code"],
                        "data_type": payloadNew["facets"][0].replace("est_download__sum","download").replace("est_revenue__sum","revenue")
                    }
                    setDict = {
                        "customer_name": customer_name,
                        "num": facts.get("est_download__sum", facts.get("est_revenue__sum", None))
                    }
                    useMysql(conncetdict={"database":"leiting"}).insert_data(
                        table_name="appanniebasedata",
                        where_dict=whereDict,
                        set_dict=setDict
                    )
        else:
            raise "运行出现错误"

    def test(self):
        countryCodeDict =self.getCountryCodeList()
        print(list(countryCodeDict.keys())[11:18])
        print(self.payload)

    def getCountryCodeList(self):
        jsonPath = 'countryCode.json'
        countryCodeDict = {}
        with open(jsonPath,'r',encoding='utf-8') as fp:
            countryCodeJson = json.loads(fp.read())
        for countryCode,countryCodeInfo in countryCodeJson["data"]["dimensions"]["country_code"].items():
            countryCodeDict[countryCode] = countryCodeInfo["name"]
        return countryCodeDict

if __name__ == "__main__":
    getAppAnnieBaseData().payload_rebulid()