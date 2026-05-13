import base64
import json,requests,yaml,io
import math,datetime
import os.path
from requests_toolbelt import MultipartEncoder
from PIL import Image as pilImage
import numpy as np
import array
import lark_oapi
from retrying import retry


class feishuApi(object):
    def __init__(self):
        self.yamlPath = 'conf/info.yaml'
        with open(self.yamlPath,'r',encoding='utf-8') as fr:
            self.yaml_config = yaml.safe_load(fr)
        self.feishuAppId = self.yaml_config.get("FeiShuAppId")
        self.feishuAppSecret = self.yaml_config.get("FeiShuAppSecret")
        self.dcFolderToken = self.yaml_config.get("dcFolderToken")
    def getAppAccessToken(self):
        """
        获取app_access_token或tenant_access_token
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "app_id":self.feishuAppId,
            "app_secret":self.feishuAppSecret
        }
        res = requests.post(url = url,headers=headers,json=payload)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            return res_json
    def getStateCode(self):
        """
        只有在yaml文件中没有feishuUserRefreshToken的时候才会需要用到
        下面的权限给的是操作云文档的权限
        """
        Scope = "drive:drive"
        Redirect_Uri = "https://open.feishu.cn/api-explorer/loading"
        state = "RANDOMSTATE"
        url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={self.feishuAppId}&redirect_uri={Redirect_Uri}&scope={Scope}&state={state}"
        print(url)

    def getUserAccessToken(self):
        """
        获取用户的useraccesstoken，如果yaml文件中没有就需要用到了
        :return:
        """
        self.getStateCode()
        url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
        headers = {
            "Authorization":"Bearer " + self.getAppAccessToken()["app_access_token"],
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "grant_type":"authorization_code",
            "code":input("请输入code")
        }
        res = requests.post(url=url,headers=headers,json=payload)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            self.feishuUserAccessToken = res_json["data"]["access_token"]
            self.feishuUserRefreshToken = res_json["data"]["refresh_token"]
            self.yaml_config["userAccessToken"] = self.feishuUserAccessToken
            self.yaml_config["userRefreshToken"] = self.feishuUserRefreshToken
            with open(self.yamlPath,'w',encoding='utf-8') as fw:
                yaml.dump(self.yaml_config,fw , default_flow_style=False)

    # @retry
    def refreshUserAccessToken(self):
        """
        当useraccesstoken失效后，会请求一次，去刷新一下token，并存储在yaml文件中
        """
        with open(self.yamlPath,'r',encoding='utf-8') as fr:
            yaml_config = yaml.safe_load(fr)
        if yaml_config.get("userAccessToken") == None:
            return self.getUserAccessToken()
        else:
            feishuUserRefreshToken = yaml_config.get("userRefreshToken")
            url = "https://open.feishu.cn/open-apis/authen/v1/refresh_access_token"
            headers = {
                "Authorization": "Bearer " + self.getAppAccessToken()["app_access_token"],
                "Content-Type": "application/json; charset=utf-8"
            }
            payload = {
                "grant_type":"refresh_token",
                "refresh_token":feishuUserRefreshToken
            }
            res = requests.post(url=url,headers=headers,json=payload)
            res_json = json.loads(res.text)
            if res_json["code"] == 0:
                feishuUserAccessToken = res_json["data"]["access_token"]
                feishuUserRefreshToken = res_json["data"]["refresh_token"]
                self.yaml_config["userAccessToken"] = feishuUserAccessToken
                self.yaml_config["userRefreshToken"] = feishuUserRefreshToken
                with open(self.yamlPath,'w',encoding='utf-8') as fw:
                    yaml.dump(self.yaml_config,fw , default_flow_style=False)
                return feishuUserAccessToken
    def getRootFolderInfo(self):
        """
        获取文件夹中的信息
        :return:
        """
        url = f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={self.dcFolderToken}"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}"
        }
        fileInfo = {}
        res = requests.get(url=url, headers=headers)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            for data in res_json["data"]["files"]:
                # print(data)
                fileInfo[data["name"]] = data["token"]
            return fileInfo


    def createExcel(self):
        url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "title": "testExcel",
            "folder_token": self.dcFolderToken
        }
        res = requests.post(url=url,headers=headers,json=payload)
        print(res.text)

    def getExcelSheetInfo(self):
        spreadsheet_token = self.getRootFolderInfo()["testExcel"]
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}"
        }
        res = requests.get(url=url,headers=headers)
        sheetInfo = {}
        if res.status_code == 200:
            res_json = json.loads(res.text)
            for data in res_json["data"]["sheets"]:
                sheetInfo[data["title"]] = data["sheet_id"]
        return sheetInfo

    def addExcelSheet(self,sheetName):
        spreadsheet_token = self.getRootFolderInfo()["testExcel"]
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "requests":[
                {
                    "addSheet": {
                        "properties": {
                            "title": sheetName,
                            "index": 1
                        }
                    }
                }
            ]
        }
        res = requests.post(url=url, headers=headers,json=payload)
        sheetInfo = {}
        if res.status_code == 200:
            res_json = json.loads(res.text)
            for data in res_json["data"]["replies"]:
                sheetInfo[data["addSheet"]["properties"]["title"]] = data["addSheet"]["properties"]["sheetId"]
        return sheetInfo

    def addDataInExcel(self,tableInfo):
        """
        tableInfo = {
            'sheetId':,
            'spreadsheet_token':
            'dataInfo': [list]
        }
        """
        self.getRootFolderInfo()
        self.deleteSheetRow(tableInfo=tableInfo)
        self.addSheetRow(tableInfo=tableInfo)
        sheetId = tableInfo["sheetId"]
        spreadsheet_token = tableInfo["spreadsheet_token"]
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        rowNum = len(tableInfo["dataInfo"])
        colcode = len(tableInfo["dataInfo"][0])
        colcodeStr = chr(64+colcode) if colcode<=26 else chr(64+math.floor(colcode/26))+chr(64+(colcode-26*math.floor(colcode/26)))
        payload = {
            "valueRange": {
                "range": f"{sheetId}!A1:{colcodeStr}{rowNum+1}",
                "values":tableInfo["dataInfo"]
            }
        }
        res = requests.post(url=url, headers=headers, json=payload)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            return True

    def addImageInExcel(self,imageArray):
        """
        dataInfo应是字典格式，包含文字和图片两部分，或为标准列表格式，方便插入图片
        :param dataInfo:
        :return:
        """
        sheetId = "1uHspq"
        path = "image/20240615-164920.jpeg"
        """
        行不通
        imageArray = np.reshape(np.asarray(pilImage.open(path)),-1)
        """
        # with open(path,'rb') as imagefile:
        #     imageArray = list(imagefile.read())
        # print(imageArray.tolist())
        spreadsheet_token = self.getRootFolderInfo()["testExcel"]
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_image"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "range": f"{sheetId}!C1:C1",
            "image": imageArray,
            "name": "223.png"
        }
        res = requests.post(url=url, headers=headers, json=payload)
        print(res.text)
        if res.status_code == 200:
            return True

    def uploadImageFile(self):
        """
        上传image到飞书
        :return:
        """
        filePath = "image/20240615-164920.jpeg"
        fileSize = os.path.getsize(filePath)
        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}"
        }
        payload = {
            "file_name": "123.png",
            "parent_type": "sheet_image",
            "parent_node": "Np2Ss7Qh3hySHGt3cK3cPb78nWh",
            "size": str(fileSize),
            "file": (open(filePath, 'rb'))
        }
        multi_form = MultipartEncoder(payload)
        headers['Content-Type'] = multi_form.content_type
        res = requests.post(url=url,headers=headers,data=multi_form)
        print(res.text)
    # def get
    def getFilebtyes(self):
        file_token = "Jgtbb6AohoezrHx54HUcjwBSnXe"
        url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}"
        }
        res = requests.get(url=url,headers=headers)
        image_bytes = io.BytesIO(res.text.encode())
        image = pilImage.open(image_bytes)

        # 保存图片
        image.save('output_image.png', 'PNG')
        # return res_json

    def readCellValue(self):
        spreadsheetToken = "Np2Ss7Qh3hySHGt3cK3cPb78nWh"
        cellRange = "1uHspq!C1:C1"
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/values/{cellRange}"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        res = requests.get(url=url,headers=headers)
        print(res.text)

    def addSheetRow(self, tableInfo):
        """
                        tableInfo = {
                            'sheetId':,
                            'spreadsheet_token':
                            'dataInfo': [list]
                        }
                        """
        self.getRootFolderInfo()
        sheetId = tableInfo["sheetId"]
        spreadsheet_token = tableInfo["spreadsheet_token"]
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "dimension": {
                "sheetId": sheetId,
                "majorDimension": "ROWS",
                "length": len(tableInfo["dataInfo"])
            }
        }
        res = requests.post(url=url, headers=headers, json=payload)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            return True

    def deleteSheetRow(self,tableInfo):
        """
                tableInfo = {
                    'sheetId':,
                    'spreadsheet_token':
                    'dataInfo': [list]
                }
                """
        self.getRootFolderInfo()
        endIndex = self.getSheetInfo(tableInfo=tableInfo)
        sheetId = tableInfo["sheetId"]
        spreadsheet_token = tableInfo["spreadsheet_token"]
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "dimension":{
                "sheetId": sheetId,
                "majorDimension": "ROWS",
                "startIndex": 2,
                "endIndex": int(endIndex)
            }
        }
        res = requests.delete(url=url, headers=headers, json=payload)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            return True

    def getSheetInfo(self,tableInfo):
        """
                tableInfo = {
                    'sheetId':,
                    'spreadsheet_token':
                    'dataInfo': [list]
                }
                """
        self.getRootFolderInfo()
        sheetId = tableInfo["sheetId"]
        spreadsheet_token = tableInfo["spreadsheet_token"]
        url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/{sheetId}"
        headers = {
            "Authorization": f"Bearer {self.refreshUserAccessToken()}"
        }
        res = requests.get(url=url, headers=headers)
        res_json = json.loads(res.text)
        if res_json["code"] == 0:
            maxRow = res_json["data"]["sheet"]["grid_properties"]["row_count"]
            return maxRow

# if __name__ == "__main__":
#     tableInfo = {
#         "sheetId": "6161fa",
#         "spreadsheet_token": "MKPWsGyTrhpEYYt9jxZcxEEtnZd",
#         "dataInfo": [["2024-08-03", None, None, None, 1, 17], ["2024-08-14", None, 1, 5, 5, 17]]
#     }
#     print("调用飞书API")
#     feishuApi().addDataInExcel(tableInfo=tableInfo)
#     # feishuApi().getRootFolderInfo()