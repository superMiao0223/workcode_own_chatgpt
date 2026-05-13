import openpyxl
import pandas as pd
from Mymodule.ConnectMysql import Connctmysql as useMysql
import yaml

class CsvToMysql():
    def __init__(self):
        self.apiconf_path = 'conf/info.yaml'
        with open(self.apiconf_path, "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.csvInfo = yaml_config["csvInfo"]

    def baseData(self, baseDataInfoList, productName):
        for baseDataInfo in baseDataInfoList:
            df = pd.read_csv(baseDataInfo["filePath"]).replace("-",0).to_dict('index')
            ## print(df.info())
            for key,values in df.items():
                setDictBase = {
                    "oldUser": int(str(values["activeUser"]).replace(",","")) - int(str(values["newUser"]).replace(",","")),
                    "newUser": int(str(values["newUser"]).replace(",","")),
                    "activeUser": int(str(values["activeUser"]).replace(",","")),
                    "payUser": int(str(values["payUser"]).replace(",","")),
                    "activePayUser": int(str(values["activePayUser"]).replace(",","")),
                    "payNum": float(str(values["payNum"]).replace(",","")),
                    "payNumWeb": float(str(values["payNumWeb"]).replace(",","")),
                    "payUserNew": int(str(values["payUserNew"]).replace(",","")),
                    "payNumNew": float(str(values["payNumNew"]).replace(",","")),
                    "payUserNew2": int(str(values["payUserNew2"]).replace(",","")),
                    "payNum2": float(str(values["payNum2"]).replace(",","")),
                    "onlineTimeMin": float(str(values["onlineTimeMin"]).replace(",","")),
                    "payUserOld": int(str(values["payUser"]).replace(",","")) - int(str(values["payUserNew"]).replace(",","")),
                    "payNumOld": float(str(values["payNum"]).replace(",","")) - float(str(values["payNumNew"]).replace(",",""))
                }
                setDict = setDictBase.copy()
                setDict["payRate"] = None if setDictBase["activeUser"] <= 0 else setDictBase["payUser"] / setDictBase["activeUser"]
                setDict["ARPU"] = None if setDictBase["activeUser"] <= 0 else setDictBase["payNum"] / setDictBase["activeUser"]
                setDict["ARPPU"] = None if setDictBase["payUser"] <= 0 else setDictBase["payNum"] / setDictBase["payUser"]
                setDict["payRateNew"] = None if setDictBase["newUser"] <= 0 else setDictBase["payUserNew"] / setDictBase["newUser"]
                setDict["ARPUNew"] = None if setDictBase["newUser"] <= 0 else setDictBase["payNumNew"] / setDictBase["newUser"]
                setDict["ARPPUNew"] = None if setDictBase["payUserNew"] <= 0 else setDictBase["payNumNew"] / setDictBase["payUserNew"]
                setDict["payRateOld"] = None if setDictBase["oldUser"] <= 0 else setDictBase["payUserOld"] / setDictBase["oldUser"]
                setDict["ARPUOld"] = None if setDictBase["oldUser"] <= 0 else setDictBase["payNumOld"] / setDictBase["oldUser"]
                setDict["ARPPUOld"] = None if setDictBase["payUserOld"] <= 0 else setDictBase["payNumOld"] / setDictBase["payUserOld"]
                whereDict = {
                    'productName': productName,
                    'date': values["日期"][:10],
                    'dateType': baseDataInfo["dateType"],
                    'country': values["国家地区"],
                    'area': baseDataInfo["area"],
                    'timezone': baseDataInfo["timezone"],
                    'tzType': baseDataInfo["tzType"],
                    'os': values["channel_name"],
                    'dataSort': baseDataInfo["dataSort"]
                }
                useMysql(conncetdict={"database":"leiting"}).insert_data(table_name="basedata",set_dict=setDict,where_dict=whereDict)


    def ltvData(self, ltvInfoList, productName):
        for ltvInfo in ltvInfoList:
            df = pd.read_csv(ltvInfo["filePath"]).replace("-", 0).to_dict('index')
            ## print(df.info())
            for key, values in df.items():
                if values["初始事件的发生时间"] != "阶段值":
                    # print(key,values)
                    setDict = {
                        "newUser": int(str(values["newUsersid数"]).replace(",", "")),
                    }
                    for valuesK,valuesV in values.items():
                        if '日' in valuesK:
                            if valuesK == '当日':
                                setDict["Day1"] = valuesV
                            else:
                                setDictKey = "Day"+str(int(str(valuesK).replace("第","").replace("日",""))+1)
                                setDict[setDictKey] = None if valuesV == 0 else valuesV
                    # print(setDict)
                    # break
                    whereDict = {
                        'productName': productName,
                        'date': values["初始事件的发生时间"][:10],
                        'dateType': ltvInfo["dateType"],
                        'country': values["国家地区"],
                        'area': ltvInfo["area"],
                        'timezone': ltvInfo["timezone"],
                        'tzType': ltvInfo["tzType"],
                        'os': values["channel_name"],
                        'dataSort': ltvInfo["dataSort"],
                        'dataType': "ltv"
                    }

                    useMysql(conncetdict={"database": "leiting"}).insert_data(table_name="ltv_ren", set_dict=setDict,where_dict=whereDict)

    def retention(self, renInfoList, productName):
        for renInfo in renInfoList:
            df = pd.read_csv(renInfo["filePath"]).replace("-", 0).to_dict('index')
            ## print(df.info())
            for key, values in df.items():
                if values["初始事件的发生时间"] != "阶段值" and values["指标"] != '留存率':
                    # print(key, values)
                    setDict = {
                        "newUser": int(str(values["newUsersid数"]).replace(",", "")),
                    }
                    for valuesK, valuesV in values.items():
                        if '日' in valuesK:
                            if valuesK == '当日':
                                setDict["Day1"] = valuesV
                            else:
                                setDictKey = "Day" + str(int(str(valuesK).replace("第", "").replace("日", "")) + 1)
                                setDict[setDictKey] = None if valuesV == 0 else valuesV
                    # print(setDict)
                    # break
                    whereDict = {
                        'productName': productName,
                        'date': values["初始事件的发生时间"][:10],
                        'dateType': renInfo["dateType"],
                        'country': values["国家地区"],
                        'area': renInfo["area"],
                        'timezone': renInfo["timezone"],
                        'tzType': renInfo["tzType"],
                        'os': values["channel_name"],
                        'dataSort': renInfo["dataSort"],
                        'dataType': "retention"
                    }
                    # print(setDict, whereDict)
                    useMysql(conncetdict={"database": "leiting"}).insert_data(table_name="ltv_ren", set_dict=setDict,where_dict=whereDict)

    def main(self):
        for productInfo in self.csvInfo:
            productName = productInfo["productName"]
            baseDataInfo = productInfo.get("basedata", [])
            ltvInfo = productInfo.get("ltv", [])
            retentionInfo = productInfo.get("retention", [])
            self.baseData(baseDataInfoList=baseDataInfo, productName=productName)
            self.ltvData(ltvInfoList=ltvInfo, productName=productName)
            self.retention(renInfoList=retentionInfo, productName=productName)

def cardInfo():
    path = 'conf/卡牌技能.xlsx'
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    cardInfo = {}
    for value in ws.iter_rows(min_row=2):
        cardInfo[value[0].value] = value[1].value
    # print(cardInfo)
    return cardInfo


def battleCards():
    cardDict = cardInfo()
    path = 'src/cardsbattle.csv'
    df = pd.read_csv(path)
    df_dict = df.transpose().to_dict()
    for key_row,value in df_dict.items():
        newList = []
        newListName = []
        cardsList = eval(value["cards"])
        for card in cardsList:
            newList.append(int(card))
        print(newList)
        print(sorted(newList))
        value["newCards"] = str(sorted(newList))
        for newCardid in sorted(newList):
            newListName.append(cardDict[newCardid])
        value["newCardsName"] = str(newListName)
        # print(value)
        # break
    df_new = pd.DataFrame(df_dict)
    df_new.transpose().to_csv('src/newcardsbattle.csv')

def baatleCard():
    cardDict = cardInfo()
    path = 'src/cardsbattle.csv'
    df = pd.read_csv(path)
    df_dict = df.transpose().to_dict()
    newdfdict = {}
    for key_row, value in df_dict.items():
        cardsList = eval(value["cards"])
        for num,card in enumerate(cardsList):
            newdfdict[str(key_row)+str(num)] = {"cardName":cardDict[int(card)],"winnum":value["winnum"],"losenum":value["losenum"]}
        # print(value)
        # break
    # print(newdfdict)
    df_new = pd.DataFrame(newdfdict)
    df_new.transpose().to_csv('src/newcardsbattle1.csv')

if __name__ == "__main__":
    # CsvToMysql().main()
    # a = "_1"
    # print(a.split("_"))
    # battleCards()
    # cardInfo()
    baatleCard()