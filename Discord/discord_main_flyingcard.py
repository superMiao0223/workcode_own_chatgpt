import json,discord,requests,yaml,random,openpyxl,pymysql,time,schedule
import os.path
from discord import app_commands
from datetime import datetime,timezone
from datetime import time as dttime
from openpyxl.drawing.image import Image
from FeiShuAPI.feishuapi import feishuApi
import buttonCode
from discord.ext import tasks,commands
from Mymodule.ConnectMysql import Connctmysql as useMysql

configPathGlobal = 'conf/dcFpDev.yaml'
with open(configPathGlobal, "r", encoding="utf-8-sig") as f:
    yaml_config = yaml.safe_load(f)
# MY_GUILD = discord.Object(id=1021963259504504842)  # replace with your guild id
MY_GUILD = discord.Object(id=yaml_config.get("guildID"))
useMysqlC = useMysql(conncetdict = {"database":"ltdcdev"})
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient(intents=discord.Intents.all())

class taskStart():
    def __init__(self):
        with open(configPathGlobal, "r", encoding="utf-8-sig") as f:
            self.yamlConfig = yaml.safe_load(f)
            self.signDict = self.yamlConfig.get("channelInfo")["signChannel"]
            self.redeemDict = self.yamlConfig.get("channelInfo")["redeemChannel"]
            self.hitText = self.yamlConfig.get("hitText")
            self.redeemGoodsInfo = self.yamlConfig.get("redeemGoodsInfo")
            self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
            self.sendCusMessage = self.yamlConfig.get("cusNewMessage")
    @tasks.loop(seconds = 36000)
    async def signTask(self):
        print(f"更新一下签到频道内容{datetime.now()}")
        signChannelIDList = list(self.signDict.keys())
        for channelID in signChannelIDList:
            viewSign = discord.ui.View(timeout=None)
            signButton = buttonCode.signButton(buttonDict={"channelID": int(channelID),"configPath": configPathGlobal})
            checkButton = buttonCode.checkButton(buttonDict={"channelID": int(channelID), "configPath": configPathGlobal})
            bindButton = buttonCode.bindButton(buttonDict={"channelID": int(channelID), "configPath": configPathGlobal})
            viewSign.add_item(signButton)
            viewSign.add_item(checkButton)
            viewSign.add_item(bindButton)
            embedSignTitle = self.hitText["signEmbedTitle"][self.signDict[channelID]["useLanguage"]] #self.signDict[channelID]["signEmbedTitle"]
            embedSignDes = self.hitText["signEmbedDes"][self.signDict[channelID]["useLanguage"]].replace("{0}",f"<#{self.signDict[channelID]['redeemChannelId']}>")
            embedSignColor = self.signDict[channelID]["signEmbedColour"]
            embedSign = discord.Embed(title=embedSignTitle, description=embedSignDes, color=embedSignColor)
            signChannelSend = await client.fetch_channel(int(channelID))
            messageHisDict = {}
            async for messageHis in signChannelSend.history():
                try:
                    ebTitleList = [ebHis.title for ebHis in messageHis.embeds]
                    if len(ebTitleList) > 0:
                        messageHisDict[ebTitleList[-1]] = messageHis
                except:
                    pass
            if embedSignTitle not in list(messageHisDict.keys()):
                await signChannelSend.send(embed=embedSign,view=viewSign)
            else:
                await messageHisDict[embedSignTitle].edit(embed=embedSign,view=viewSign)
        print(f"更新完成签到频道内容{datetime.now()}")

    @tasks.loop(seconds=36000)
    async def redeemTask(self):
        print(f"更新一下兑换频道内容{datetime.now()}")
        redeemChannelIDList = list(self.redeemDict.keys())
        checkTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        checkTime = datetime.fromtimestamp(checkTs / 1000)
        for channelID in redeemChannelIDList:
            redeemSend = await client.fetch_channel(int(channelID))
            messageHisDict = {}
            async for messageHis in redeemSend.history():
                try:
                    ebTitle = [ebHis.title for ebHis in messageHis.embeds][0]
                    messageHisDict[ebTitle] = messageHis
                except:
                    pass
            redeemTypeDict = {}
            for redeemGoodsID in self.redeemDict[channelID]["redeemGoodsList"]:
                try:
                    redeemTypeDict[self.redeemGoodsInfo[int(redeemGoodsID)]["typeInfo"]].append(redeemGoodsID)
                except:
                    redeemTypeDict[self.redeemGoodsInfo[int(redeemGoodsID)]["typeInfo"]] = [redeemGoodsID]
            for redeemType, goodsList in redeemTypeDict.items():
                redeemCodeList = redeemType.split("_")
                viewType = discord.ui.View(timeout=None)
                embedTitle = self.hitText["redeemTitle"+redeemCodeList[0]][self.redeemDict[channelID]["useLanguage"]].replace("{0}",redeemCodeList[1])
                embedType = discord.Embed(
                    title=embedTitle,
                    color=discord.Colour.red()
                )
                for goodsID in goodsList:
                    redeemDateStr = "9999-12-31 23:59:59" if self.redeemGoodsInfo[goodsID]["redeemDate"] == None else self.redeemGoodsInfo[goodsID]["redeemDate"]
                    goodsRedeemDate = datetime.strptime(redeemDateStr, "%Y-%m-%d %H:%M:%S")
                    redeemStatusInfo = self.useMysql.search_data(f"select count(goodsID) from redeem_shop_goods where goodsStatus = 'unUse' and goodsID = {goodsID}")
                    redeemStatus = self.hitText["avText"][self.redeemDict[channelID]["useLanguage"]] if int(redeemStatusInfo[0][0])>0 and goodsRedeemDate > checkTime else self.hitText["unAvText"][self.redeemDict[channelID]["useLanguage"]]
                    embedType.add_field(
                        name=self.redeemGoodsInfo[int(goodsID)]["goodName"][self.redeemDict[channelID]["useLanguage"]],
                        value=self.hitText["priceStatus"][self.redeemDict[channelID]["useLanguage"]].replace("{0}",str(self.redeemGoodsInfo[int(goodsID)]["Price"])).replace("{1}", redeemStatus),
                        inline=True
                    )
                    goodsButton = buttonCode.goodsButton(buttonDict={"channelID": int(channelID), "configPath": configPathGlobal, "goodsID": goodsID})

                    if int(redeemStatusInfo[0][0])>0 and goodsRedeemDate > checkTime:
                        viewType.add_item(goodsButton)
                if messageHisDict.get(embedTitle) == None:
                    await redeemSend.send(embed=embedType,view=viewType)
                else:
                    await messageHisDict[embedTitle].edit(embed=embedType,view=viewType)
        print(f"更新完成兑换频道内容{datetime.now()}")

    async def sendNewMessage(self):
        embedColor = self.sendCusMessage["embedColor"]
        for channelID in list(self.sendCusMessage["channelInfo"].keys()):
            sendChannel = await client.fetch_channel(channelID)
            viewCus = discord.ui.View(timeout=None)
            for buttonName, buttonUrl in self.sendCusMessage["channelInfo"][channelID]["buttonName"].items():
                viewCus.add_item(buttonCode.urlButton(buttonDict={"buttonName":buttonName, "buttonUrl":buttonUrl}))
            embedTit = self.sendCusMessage["channelInfo"][channelID]["embedTit"]
            embedDes = self.sendCusMessage["channelInfo"][channelID]["embedDes"]
            embedCus = discord.Embed(title=embedTit, description=embedDes, color=embedColor)
            messageHisDict = {}
            async for messageHis in sendChannel.history():
                try:
                    ebTitleList = [ebHis.title for ebHis in messageHis.embeds]
                    if len(ebTitleList) > 0:
                        messageHisDict[ebTitleList[-1]] = messageHis
                except:
                    pass
            if embedTit not in list(messageHisDict.keys()):
                await sendChannel.send(embed=embedCus, view=viewCus)
            else:
                await messageHisDict[embedTit].edit(embed=embedCus, view=viewCus)
    # @tasks.loop(time=dttime(hour=10, minute=13, tzinfo=timezone.utc))
    @tasks.loop(seconds=3500)
    async def getGuildMemCount(self):
        guildInfo = client.get_guild(self.yamlConfig.get("guildID"))
        dateInfoTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        dateInfo = datetime.strftime(datetime.fromtimestamp(dateInfoTs / 1000), "%Y-%m-%d")
        whereDict = {
            "date": dateInfo,
            "guildID": guildInfo.id,

        }
        setDict = {
            "guildName": guildInfo.name,
            "memberCount": guildInfo.member_count
        }
        self.useMysql.insert_data(table_name="guildInfo",set_dict=setDict,where_dict=whereDict)
        time.sleep(2)
        guildInfoTable = f"""
            select date_format(a1.`date`,'%Y-%m-%d'),a3.joinusernum,a2.leaveusernum,a1.joinCount,a1.leaveCount,a1.memberCount
            from(
            select `date`,joinCount, leaveCount,memberCount from guildInfo
            where guildID = '{self.yamlConfig.get("guildID")}'
            ) as a1
            left join(
            select DATE_FORMAT(leaveTime,'%Y-%m-%d') as date2,count(DISTINCT dcUserId) as leaveusernum from user_info
            where inGuild = 0
            and guildID = '{self.yamlConfig.get("guildID")}'
            group by date2
            ) as a2
            on a1.`date` = a2.date2
            left join (
            select DATE_FORMAT(joinTime,'%Y-%m-%d') as date1,count(DISTINCT dcUserId) as joinusernum from user_info
            where inGuild = 1
            and guildID = '{self.yamlConfig.get("guildID")}'
            and isbot = '0'
            group by date1
            ) as a3
            on a1.`date` = a3.`date1`"""
        guildInfoAll = self.useMysql.search_data(select_table=guildInfoTable)
        guildInfoAllL = [list(x) for x in guildInfoAll]
        guildInfoAllL.insert(0,["日期","加入人数","离开人数","加入次数","离开次数","服务器人数"])
        tableInfo = {
            "sheetId": self.yamlConfig.get("sheetId"),
            "spreadsheet_token": self.yamlConfig.get("spreadsheet_token"),
            "dataInfo": guildInfoAllL
        }
        print("调用飞书API")
        feishuApi().addDataInExcel(tableInfo=tableInfo)
        print("调用飞书API调用完成")

    async def getGuildMemInfo(self):
        guildInfo = client.get_guild(self.yamlConfig.get("guildID"))
        for memberInfo in guildInfo.members:
            whereDict1 = {
                "dcUserId": memberInfo.id,
                "guildID": guildInfo.id
            }
            setDict1 = {
                "inGuild": 1,
                "joinTime": memberInfo.joined_at,
                "guildName": guildInfo.name,
                "isbot": 1 if memberInfo.bot == True else 0,
                "dcUserName": memberInfo.name
            }
            self.useMysql.insert_data(table_name="user_info", set_dict=setDict1, where_dict=whereDict1)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    # #签到频道发布内容
    # taskStart().signTask.start()
    # #兑换频道发布内容
    # taskStart().redeemTask.start()
    #每日0点统计服务器人数
    # taskStart().getGuildMemCount.start()
    # await taskStart().sendNewMessage()
    # await taskStart().getGuildMemInfo()
@client.event
async def on_member_join(member:discord.Member):
    useMysql1 = useMysql(conncetdict = {"database":"ltdcdev"})
    dateInfoTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
    dateInfo = datetime.strftime(datetime.fromtimestamp(dateInfoTs / 1000), "%Y-%m-%d")
    addTable = f"select `joinCount` from `guildInfo` where `date` = '{dateInfo}' and `guildID`= {yaml_config.get('guildID')}"
    addCount = useMysql1.search_data(select_table=addTable)
    addCountNum = 0 if len(addCount) == 0 or addCount[0][0] == None else addCount[0][0]
    whereDict = {
        "date": dateInfo,
        "guildID": member.guild.id
    }
    setDict = {
        "guildName": member.guild.name,
        "joinCount": addCountNum + 1
    }
    useMysql1.insert_data(table_name="guildInfo", set_dict=setDict, where_dict=whereDict)
    whereDict1 = {
        "dcUserId": member.id,
        "guildID": member.guild.id
    }
    setDict1 = {
        "inGuild": 1,
        "joinTime": datetime.fromtimestamp(dateInfoTs / 1000),
        "guildName": member.guild.name,
        "isbot": 1 if member.bot == True else 0,
        "dcUserName": member.name
    }
    useMysql1.insert_data(table_name="user_info", set_dict=setDict1, where_dict=whereDict1)
    whereDict2 = {
        "dcUserId": member.id,
        "guildID": member.guild.id,
        "changeReason": "加入服务器",
        "changeTs": dateInfoTs
    }
    setDict2 = {
        "changeTime": datetime.fromtimestamp(dateInfoTs / 1000),
        "guildName": member.guild.name
    }
    useMysql1.insert_data(table_name="user_data_change_log", set_dict=setDict2, where_dict=whereDict2)
@client.event
async def on_raw_member_remove(payload: discord.RawMemberRemoveEvent):
    useMysql2 = useMysql(conncetdict={"database": "ltdcdev"})
    dateInfoTs2 = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
    dateInfo2 = datetime.strftime(datetime.fromtimestamp(dateInfoTs2 / 1000), "%Y-%m-%d")
    leaveTable = f"select `leaveCount` from `guildInfo` where `date` = '{dateInfo2}' and `guildID`= {yaml_config.get('guildID')}"
    leaveCount = useMysql2.search_data(select_table=leaveTable)
    leaveCountNum = 0 if len(leaveCount) == 0 or leaveCount[0][0] == None else leaveCount[0][0]
    guildInfo = client.get_guild(payload.guild_id)
    whereDict = {
        "date": dateInfo2,
        "guildID": payload.guild_id
    }
    setDict = {
        "guildName": guildInfo.name,
        "leaveCount": leaveCountNum + 1
    }
    useMysql2.insert_data(table_name="guildInfo", set_dict=setDict, where_dict=whereDict)
    whereDict1 = {
        "dcUserId": payload.user.id,
        "guildID": payload.guild_id
    }
    setDict1 = {
        "inGuild": 0,
        "leaveTime": datetime.fromtimestamp(dateInfoTs2 / 1000),
        "guildName": guildInfo.name,
        "isbot": 1 if payload.user.bot == True else 0,
        "dcUserName": payload.user.name
    }
    useMysql2.insert_data(table_name="user_info", set_dict=setDict1, where_dict=whereDict1)
    whereDict2 = {
        "dcUserId": payload.user.id,
        "guildID": payload.guild_id,
        "changeReason": "离开服务器",
        "changeTs": dateInfoTs2
    }
    setDict2 = {
        "changeTime": datetime.fromtimestamp(dateInfoTs2 / 1000),
        "guildName": guildInfo.name
    }
    useMysql2.insert_data(table_name="user_data_change_log", set_dict=setDict2, where_dict=whereDict2)

@client.tree.command(name="updateuserdata", description="修改用户数据,目前积分采用加的模式，uid是直接修改",guild=discord.Object(id=yaml_config.get("guildID")))
async def updateUserData(interaction: discord.Interaction, dcmember: discord.Member, money: int = None,uid:str = None):
    """
    修改用户信息，可选修改；
    money：用户可兑换道具的货币
    uid：用户的游戏内UID
    """
    with open(configPathGlobal, "r", encoding="utf-8-sig") as f:
        yaml_config = yaml.safe_load(f)
    roles_id = [str(roles_id.id) for roles_id in interaction.user.roles]
    dcuserid = dcmember.id
    """
    获取身份组信息，若没有在对应身份组，则提示没有权限。
    """
    if str(yaml_config.get("ManageUserid")) not in roles_id:
        await interaction.response.send_message('您没有权限操作，请联系管理员添加权限', ephemeral=True,delete_after=60)
    else:
        changeTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        changeTime = datetime.fromtimestamp(changeTs / 1000)
        # 获取用户之前的数据，uid，money，积分，等级
        userInfoTable = f"""select gameUID,dcMoney,dcScore,dcLevel from user_info where dcUserId = '{dcuserid}' and `guildID` = '{yaml_config.get('guildID')}'"""
        userInfo = useMysqlC.search_data(select_table=userInfoTable)
        # 若没有用户数据或用户数据为空则为0
        moneyB = 0 if len(userInfo) ==0 or userInfo[0][1] == None else userInfo[0][1]
        uidB = None if len(userInfo) == 0 or userInfo[0][0] == None else userInfo[0][0]
        moneyE = 0 if money == None else money
        uidE = uidB if uid == None else uid
        setDict = {
            "gameUID": uidE,
            "dcMoney": moneyE + moneyB,
            "lastChangeTs": changeTs,
            "lastChangeT": changeTime,
            "guildName": dcmember.guild.name,
            "isbot": 1 if dcmember.bot == True else 0,
            "dcUserName": dcmember.name
        }
        whereDict = {
            "dcUserId": dcuserid,
            "guildID": dcmember.guild.id
        }

        setDict1 = {
            "dcMoneyChange": moneyE,
            "dcMoneyChangeBefore": moneyB,
            "dcMoneyChangeAfter": moneyE + moneyB,
            "changeTime": changeTime,
            "guildName": dcmember.guild.name
        }
        whereDict1 = {
            "dcUserId": dcuserid,
            "changeReason": f"管理员：{interaction.user.name}[{interaction.user.id}]进行修改，\n修改前：货币：{moneyB}\n目前此人的货币：{moneyE + moneyB}\n修改前UID：{uidB}\n修改后UID：{uidE}",
            "changeTs": changeTs,
            "guildID": dcmember.guild.id
        }
        useMysqlC.insert_data(table_name="user_info",set_dict=setDict,where_dict=whereDict)
        useMysqlC.insert_data(table_name="user_data_change_log", set_dict=setDict1, where_dict=whereDict1)
        await interaction.response.send_message(f'修改成功，修改前：货币：{moneyB}\n目前此人的货币：{moneyE + moneyB}\n修改前UID：{uidB}\n修改后UID：{uidE}', ephemeral=True, delete_after=60)


@client.event
async def on_message(message):
    print(message)
    setDict = {
        # "activity": message.activity,
        # "application": message.application,
        # "application_id": message.application_id,
        "attachments": str([b.url for b in message.attachments]),
        "userID": message.author.id,
        "userName": message.author.name,
        "userBot": str(message.author.bot),
        "channelName": message.channel.name,
        "channelType": str(message.channel.type),
        # "channel_mentions": message.channel_mentions,
        "clean_content": message.clean_content,
        # "components": message.components,
        "content": message.content,
        "created_at": message.created_at,
        "edited_at": message.edited_at,
        "embeds": str([[c.title,c.description] for c in message.embeds]),
        # "flags": message.flags,
        "guildName": message.guild.name,
        # "interaction": message.interaction,
        # "interaction_metadata": message.interaction_metadata,
        # "jump_url": message.jump_url,
        # "mention_everyone": message.mention_everyone,
        # "mentions": message.mentions,
        # "nonce": message.nonce,
        # "pinned": message.pinned,
        # "poll": message.poll,
        # "position": message.position,
        # "raw_channel_mentions": message.raw_channel_mentions,
        # "raw_mentions": message.raw_mentions,
        # "raw_role_mentions": message.raw_role_mentions,
        # "reactions": message.reactions,
        # "reference": message.reference,
        # "role_mentions": message.role_mentions,
        # "role_subscription": message.role_subscription,
        "stickers": str([a.url for a in message.stickers]),
        # "system_content": message.system_content,
        # "thread": message.thread,
        # "tts": message.tts,
        # "type": message.type,
        # "webhook_id": message.webhook_id
    }
    whereDict = {
        "guildID": message.guild.id,
        "messageId": message.id,
        "channelID": message.channel.id
    }
    useMysqlC.insert_data(table_name='chat_history',set_dict=setDict,where_dict=whereDict)
    # print(whereDict)
    # print(setDict)
    keyWordsList = ["儲值", "折扣", "官網", "購買", "優惠"]
    for keyWord in keyWordsList:
        if keyWord in message.content and message.author.bot == False:
            await message.reply("主公大人安安╰(○'◡'○)╮塔妹好像聽到了什麼關鍵詞？ ！前往官網儲值有更多優惠唷！儲值優惠傳送門：https://bit.ly/ttkdcgamepay")
    if message.content == "主公大人安安╰(○'◡'○)╮塔妹好像聽到了什麼關鍵詞？ ！前往官網儲值有更多優惠唷！儲值優惠傳送門：https://bit.ly/ttkdcgamepay":
        await message.delete(delay = 10)
#自己机器人
client.run(yaml_config.get("token"))
