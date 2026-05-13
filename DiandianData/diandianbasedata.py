import base64
from FeiShuAPI.feishuapi import feishuApi
import requests


url = 'https://diandian-app.oss-cn-hangzhou.aliyuncs.com/export/xls/王者荣耀_下载量_20240703_20240801_y8jtju9pvpvjmuq.xlsx'

res = requests.get(url=url)
with open('src/file1.xlsx','wb') as f:
    f.write(res.content)