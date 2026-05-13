import random,discord,yaml,textInput,time,calendar,math
from Mymodule.ConnectMysql import Connctmysql as useMysql
from datetime import datetime,timedelta


class checkButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
        buttonDict = {
            "configPath": ""
            "channelID": "", ->int

        }
        """
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["signChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.labelName = self.hitText["checkLabelName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        self.useMysql = useMysql(conncetdict={"database": "ltdcdev"})
        super().__init__(label=self.labelName,style=discord.ButtonStyle(value=self.label_dict[buttonDict["channelID"]]["checkLabelStyle"]))

    async def callback(self, interaction: discord.Interaction):
        #获取用户之前的数据
        userInfoTable = f"select dcUserId,gameUID,dcMoney,dcScore,dcLevel,lastSignTs,lastSignT from user_info where dcuserid = '{interaction.user.id}' and `guildID` = '{interaction.guild_id}'"
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        if len(userInfo)==0:
            sendM1 = self.hitText["noData"][self.label_dict[int(interaction.channel_id)]['useLanguage']]
            await interaction.response.send_message(sendM1,ephemeral=True, delete_after=self.delete_after_seconds)
        else:
            dcMoney = 0 if userInfo[0][2] == None else userInfo[0][2]
            if userInfo[0][5] == None and userInfo[0][1] == None:
                sendM2 = self.hitText["notSignNotBind"][self.label_dict[int(interaction.channel_id)]['useLanguage']].replace("{0}",str(dcMoney))
                await interaction.response.send_message(sendM2,ephemeral=True, delete_after=self.delete_after_seconds)

            elif userInfo[0][5] == None and userInfo[0][1] != None:
                sendM3 = self.hitText["notSignBind"][self.label_dict[int(interaction.channel_id)]['useLanguage']].replace("{0}",str(dcMoney)).replace("{1}",str(userInfo[0][1]))
                await interaction.response.send_message(sendM3, ephemeral=True,delete_after=self.delete_after_seconds)

            elif userInfo[0][5] != None and userInfo[0][1] == None:
                sendM4 = self.hitText["signNotBind"][self.label_dict[int(interaction.channel_id)]['useLanguage']].replace("{0}",str(dcMoney)).replace("{1}",str(userInfo[0][5][:-3]))
                await interaction.response.send_message(sendM4, ephemeral=True,delete_after=self.delete_after_seconds)

            else:
                sendM5 = self.hitText["signBind"][self.label_dict[int(interaction.channel_id)]['useLanguage']].replace("{0}",str(dcMoney)).replace("{1}", str(userInfo[0][5][:-3])).replace("{2}",str(userInfo[0][1]))
                await interaction.response.send_message(sendM5, ephemeral=True,delete_after=self.delete_after_seconds)


class signButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "configPath": ""
                "channelID": "", ->int
            }
        """
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["signChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.labelName = self.hitText["signLabelName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        self.signEarnList = yaml_config.get("signEarn")
        self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
        self.signIntervalEarn = yaml_config.get("signIntervalEarn")
        super().__init__(label=self.labelName, style=discord.ButtonStyle(value=self.label_dict[buttonDict["channelID"]]["signLabelStyle"]))

    async def callback(self, interaction: discord.Interaction):
        delete_after_seconds = self.delete_after_seconds
        #获取当前签到时间(UTC+8)的时间
        signTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        signTime = datetime.fromtimestamp(signTs / 1000)
        #用户获取积分
        signEarn = random.randint(self.signEarnList[0],self.signEarnList[1])
        #获取用户信息
        userInfoTable = f"""select dcMoney, dcScore, dcLevel, lastSignTs, lastSignT, conSign, allSign from user_info where dcUserId = '{interaction.user.id}' and `guildID` = '{interaction.guild.id}'"""
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        lastSignTs = '0000' if len(userInfo) == 0 or userInfo[0][3] == None else userInfo[0][3]
        whereDict = {
            "dcUserId": interaction.user.id,
            "guildID": interaction.guild.id
        }
        dcMoneyB = 0 if len(userInfo) == 0 or userInfo[0][0] == None else userInfo[0][0]
        signInterval = int(signTs / 1000) - int(lastSignTs[:-3])
        # 判断距上次签到是否超过24小时,如果超过则
        if signInterval >= 86400:
            """
            连续签到判断逻辑：若用户无数据或没有进行连续签到则为0
            累计签到逻辑：用户无数据时为0否则根据累计签到天数进行发放
            """

            conSign = 0 if len(userInfo) == 0 or userInfo[0][5] == None or math.floor(signInterval / 86400) >1 else userInfo[0][5]
            conSignDay = conSign + 1
            allSign = 0 if len(userInfo) == 0 or userInfo[0][6] == None else userInfo[0][6]
            allSignDay = allSign + 1
            setDict1 = {
                "dcMoney": signEarn + dcMoneyB + self.signIntervalEarn["conSign"].get(int(conSignDay),0) + self.signIntervalEarn["allSign"].get(int(allSignDay),0),
                "lastChangeTs": signTs,
                "lastChangeT": signTime,
                "lastSignTs": signTs,
                "lastSignT": signTime,
                "conSign": conSignDay,
                "allSign": allSignDay,
                "guildName": interaction.guild.name,
                "isbot": 1 if interaction.user.bot == True else 0,
                "dcUserName": interaction.user.name
            }
            self.useMysql.insert_data(table_name="user_info", set_dict=setDict1, where_dict=whereDict)
            #插入变更日志
            setDict2 = {
                'changeTime': signTime,
                'dcMoneyChange': signEarn + self.signIntervalEarn["conSign"].get(int(conSignDay),0),
                'dcMoneyChangeBefore': dcMoneyB,
                'dcMoneyChangeAfter': signEarn + dcMoneyB + self.signIntervalEarn["conSign"].get(int(conSignDay),0),
                "guildName": interaction.guild.name
            }
            whereDict1 = {
                'dcUserId': interaction.user.id,
                'changeReason': f"{interaction.channel.name}：{interaction.channel.id}频道进行签到",
                'changeTs': signTs,
                "guildID": interaction.guild.id
            }
            self.useMysql.insert_data(table_name="user_data_change_log",set_dict=setDict2,where_dict=whereDict1)
            sendM1S = self.hitText["signEarn"][self.label_dict[interaction.channel.id]["useLanguage"]].replace("{0}",str(signEarn))
            await interaction.response.send_message(sendM1S,ephemeral=True,delete_after=delete_after_seconds)
        else:
            #提示需再xx时间后签到
            sendM2S = self.hitText["signFalse"][self.label_dict[interaction.channel.id]["useLanguage"]].replace("{0}",str(int(userInfo[0][3][:-3]) + 86400))
            await interaction.response.send_message(sendM2S,ephemeral=True,delete_after=delete_after_seconds)


class bindButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "configPath": ""
                "channelID": "", ->int
            }
        """

        self.buttonDict = buttonDict
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["signChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.labelName = self.hitText["bindLabelName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
        super().__init__(label=self.labelName, style=discord.ButtonStyle(value=self.label_dict[buttonDict["channelID"]]["bindLabelStyle"]))
    async def callback(self, interaction: discord.Interaction):
        #弹form按钮
        userInfoTable =  f"""select gameUID from user_info where dcUserId = '{interaction.user.id}' and `guildID` = '{interaction.guild.id}'"""
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        if len(userInfo) == 0 or userInfo[0][0] == None:
            textInputModal = textInput.bindUID(buttonDict=self.buttonDict)
            await interaction.response.send_modal(textInputModal)
        else:
            sendMessage = self.hitText["bindFalse"][self.label_dict[int(interaction.channel.id)]["useLanguage"]].replace("{0}",userInfo[0][0])
            await interaction.response.send_message(sendMessage,ephemeral=True,delete_after=self.delete_after_seconds)


class goodsButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "configPath": ""
            "channelID": channelID ->int,
            "goodsID": goodsID ->int
            }
        """

        self.buttonDict = buttonDict
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["redeemChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.redeemGoodsInfo = yaml_config.get("redeemGoodsInfo")
        self.labelName = self.redeemGoodsInfo[buttonDict["goodsID"]]["goodName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
        super().__init__(label=self.labelName, style=discord.ButtonStyle(value=self.redeemGoodsInfo[buttonDict["goodsID"]]["labelStyle"]))
    async def callback(self, interaction: discord.Interaction):
        checkTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        checkTime = datetime.fromtimestamp(checkTs / 1000)
        goodsRedeemDateStr = "9999-12-31 23:59:59" if self.redeemGoodsInfo[self.buttonDict["goodsID"]]["redeemDate"] == None else self.redeemGoodsInfo[self.buttonDict["goodsID"]]["redeemDate"]
        goodsRedeemDate = datetime.strptime(goodsRedeemDateStr,"%Y-%m-%d %H:%M:%S")
        goodsPrice = self.redeemGoodsInfo[self.buttonDict["goodsID"]]["Price"]
        goodsTypeList = self.redeemGoodsInfo[self.buttonDict["goodsID"]]["typeInfo"].split("_")
        userInfoTable = f"""select dcMoney from user_info where dcUserId = '{interaction.user.id}' and `guildID` = '{interaction.guild.id}'"""
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        removeOnlyGroupBy = f"SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY,',''))"
        self.useMysql.cursor_update(tableInfo=removeOnlyGroupBy)
        goodsRemainTable = f"select count(goodsID) from redeem_shop_goods where goodsStatus='unUse' and goodsID={self.buttonDict['goodsID']}"
        goodsRemain = self.useMysql.search_data(select_table=goodsRemainTable)
        goodsDetTable = f"select * from redeem_shop_goods where goodsStatus='unUse' and goodsID={self.buttonDict['goodsID']}"
        goodsDet = self.useMysql.search_data(select_table=goodsDetTable)
        checkTableBase = f"select count(dcUserId) from redeem_shop_goods where dcUserId = '{interaction.user.id}' and goodsID = '{self.buttonDict['goodsID']}'"
        wd = calendar.weekday(checkTime.year, checkTime.month, checkTime.day)
        bgtsw = int(time.mktime(time.strptime(str(checkTime.date() - timedelta(wd)) + ' 00:00:00', '%Y-%m-%d %H:%M:%S')))
        edtsw = int(time.mktime(time.strptime(str(checkTime.date() + timedelta(7 - wd)) + ' 00:00:00', '%Y-%m-%d %H:%M:%S')))
        bgtsm = int(time.mktime(time.strptime(str(checkTime.year) + '-' + str(checkTime.month) + '-' + '01 00:00:00', '%Y-%m-%d %H:%M:%S')))
        edtsm = int(time.mktime(time.strptime(str(checkTime.year) + '-' + str(checkTime.month + 1) + '-' + '01 00:00:00','%Y-%m-%d %H:%M:%S')))
        if goodsTypeList[0] == 'W':
            checkTable = checkTableBase + f" and used_timestamp between {bgtsw} and {edtsw}"
        elif goodsTypeList[0] == 'M':
            checkTable = checkTableBase + f" and used_timestamp between {bgtsm} and {edtsm}"
        elif goodsTypeList[0] == 'L':
            checkTable = checkTableBase
        redeemLimitCheck = self.useMysql.search_data(select_table=checkTable)
        redeemLimitNum = 99999 if goodsTypeList[0] == 'U' else redeemLimitCheck[0][0]
        sendM1 = self.hitText["noCoin"][self.label_dict[interaction.channel.id]["useLanguage"]].replace("{0}","0")
        sendM2 = self.hitText["noCoin"][self.label_dict[interaction.channel.id]["useLanguage"]].replace("{0}",str(userInfo[0][0]))
        sendM3 = self.hitText["noGoods"][self.label_dict[interaction.channel.id]["useLanguage"]]
        sendM4 = self.hitText["redeemLimit"][self.label_dict[interaction.channel.id]["useLanguage"]]
        sendM6 = self.hitText["redeemDate"][self.label_dict[interaction.channel.id]["useLanguage"]]
        if len(userInfo) == 0 or userInfo[0][0] == None or int(userInfo[0][0])<=0:
            await interaction.response.send_message(sendM1,ephemeral=True, delete_after=self.delete_after_seconds)
        elif int(userInfo[0][0]) < int(goodsPrice):
            await interaction.response.send_message(sendM2, ephemeral=True, delete_after=self.delete_after_seconds)
        elif goodsRemain[0][0] < self.redeemGoodsInfo[self.buttonDict["goodsID"]]["codeNum"] or goodsRemain[0][0] == None or goodsRemain[0][0] ==0:
            await interaction.response.send_message(sendM3, ephemeral=True, delete_after=self.delete_after_seconds)
        elif redeemLimitNum >= int(goodsTypeList[1]):
            await interaction.response.send_message(sendM4, ephemeral=True, delete_after=self.delete_after_seconds)
        elif goodsRedeemDate <  checkTime:
            await interaction.response.send_message(sendM6, ephemeral=True, delete_after=self.delete_after_seconds)
        else:
            setDict1 = {
                "dcMoney": int(userInfo[0][0]) - int(goodsPrice),
                "lastChangeTs": checkTs,
                "lastChangeT": checkTime,
                "guildName": interaction.guild.name,
                "isbot": 1 if interaction.user.bot == True else 0,
                "dcUserName": interaction.user.name
            }
            whereDict1 = {
                'dcUserId': interaction.user.id,
                "guildID": interaction.guild.id
            }
            self.useMysql.insert_data(table_name="user_info", set_dict=setDict1, where_dict=whereDict1)
            # 插入变更日志
            setDict2 = {
                'changeTime': checkTime,
                'dcMoneyChange': - int(goodsPrice),
                'dcMoneyChangeBefore': int(userInfo[0][0]),
                'dcMoneyChangeAfter': int(userInfo[0][0]) - int(goodsPrice),
                "guildName": interaction.guild.name
            }
            whereDict2 = {
                'dcUserId': interaction.user.id,
                'changeReason': f"{interaction.channel.name}：[{interaction.channel.id}]在[{interaction.channel.name}]兑换商品",
                'changeTs': checkTs,
                "guildID": interaction.guild.id
            }
            self.useMysql.insert_data(table_name="user_data_change_log", set_dict=setDict2, where_dict=whereDict2)
            goodsCodeStr = ""
            for codeNum in range(0,self.redeemGoodsInfo[self.buttonDict["goodsID"]]["codeNum"]):
                setDict3 = {
                    "goodsStatus": "used",
                    "dcUserId": interaction.user.id,
                    "dcUserName": interaction.user.name,
                    "used_dcmoney": int(goodsPrice),
                    "used_time": checkTime,
                    "used_timestamp": checkTs,
                    "charge_before": int(userInfo[0][0]),
                    "charge_after": int(userInfo[0][0]) - int(goodsPrice),
                    "used_channel": interaction.channel.name,
                    "guildName": interaction.guild.name,
                    "guildID": interaction.guild.id
                }
                whereDict3 = {
                    "goodsID": self.buttonDict["goodsID"],
                    "goodsCode": goodsDet[codeNum][1]
                }
                self.useMysql.insert_data(table_name="redeem_shop_goods",set_dict=setDict3,where_dict=whereDict3)
                goodsCodeStr +=  str(goodsDet[codeNum][1]) + "\n"
            sendM5 = self.hitText["redeemSuc"][self.label_dict[interaction.channel.id]["useLanguage"]].replace("{0}",str(goodsPrice)).replace("{1}", str(int(userInfo[0][0]) - int(goodsPrice))).replace("{2}", goodsCodeStr)
            await interaction.response.send_message(sendM5, ephemeral=True, delete_after=self.delete_after_seconds)
            await interaction.user.send(sendM5)

class urlButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "buttonName": ""
            "buttonUrl": ""
            }
        """
        # self.buttonDict = buttonDict
        super().__init__(label=buttonDict["buttonName"], style=discord.ButtonStyle(value=5),url=buttonDict["buttonUrl"])


class addRoleButton(discord.ui.Button):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "configPath": ""
                "channelID": "", ->int
            }
        """

        self.buttonDict = buttonDict
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["signChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.labelName = self.hitText["bindLabelName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
        super().__init__(label=self.labelName, style=discord.ButtonStyle(value=self.label_dict[buttonDict["channelID"]]["bindLabelStyle"]))
    async def callback(self, interaction: discord.Interaction):
        #弹form按钮
        userInfoTable =  f"""select gameUID from user_info where dcUserId = '{interaction.user.id}'"""
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        if len(userInfo) == 0 or userInfo[0][0] == None:
            textInputModal = textInput.bindUID(buttonDict=self.buttonDict)
            await interaction.response.send_modal(textInputModal)
        else:
            sendMessage = self.hitText["bindFalse"][self.label_dict[int(interaction.channel.id)]["useLanguage"]].replace("{0}",userInfo[0][0])
            await interaction.response.send_message(sendMessage,ephemeral=True,delete_after=self.delete_after_seconds)



class testButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='123',style=discord.ButtonStyle(value=3))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('dianjichengg',ephemeral=True,delete_after=10)