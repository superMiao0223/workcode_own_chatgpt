import json,requests
import pandas as pd

df = pd.read_excel('飞牌-激活未注册对应设备.xlsx',sheet_name='加设备2')
# print(df)

for extendInfo in df['extend_info']:
    extendInfo = json.loads(extendInfo)
    print(extendInfo['ip'])
    # res = requests.get(f'https://nordvpn.com/wp-admin/admin-ajax.php?action=get_user_info_data&ip={extendInfo["ip"]}')
    # res_json = json.loads(res.text)
    # print(res_json["country"])
    # break