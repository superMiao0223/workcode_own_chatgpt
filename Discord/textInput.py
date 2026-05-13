import random,discord,yaml
from Mymodule.ConnectMysql import Connctmysql as useMysql
from datetime import datetime


class bindUID(discord.ui.Modal):
    def __init__(self, buttonDict: dict):
        """
            buttonDict = {
            "configPath": "",
                "channelID": "", ->int
            }
        """
        with open(buttonDict["configPath"], "r", encoding="utf-8-sig") as f:
            yaml_config = yaml.safe_load(f)
        self.hitText = yaml_config.get("hitText")
        self.label_dict = yaml_config.get("channelInfo", {})["signChannel"]
        self.delete_after_seconds = yaml_config.get("messageDeleteAfterSec")
        self.useMysql = useMysql(conncetdict = {"database":"ltdcdev"})
        self.textInputTitle = self.hitText["bindTitle"][self.label_dict[buttonDict["channelID"]]["useLanguage"]]
        super().__init__(title=self.textInputTitle,timeout=None)
        UID = discord.ui.TextInput(
            label=self.hitText["bindLabelName"][self.label_dict[buttonDict["channelID"]]["useLanguage"]],
            style=discord.TextStyle(value=int(self.label_dict[buttonDict["channelID"]]["bindTextStyle"])),
            min_length=int(self.label_dict[buttonDict["channelID"]]["bindUIDLen"]),
            max_length=int(self.label_dict[buttonDict["channelID"]]["bindUIDLen"]),
            custom_id='UID'
        )
        self.add_item(UID)
    async def on_submit(self,interaction:discord.Interaction):
        lastChangeTs = round((datetime.timestamp(datetime.utcnow()) + 8 * 60 * 60) * 1000)
        lastChangeT = datetime.fromtimestamp(lastChangeTs / 1000)
        userInfoTable= f"select dcMoney from user_info where dcUserId = '{interaction.user.id}'"
        userInfo = self.useMysql.search_data(select_table=userInfoTable)
        dcMoneyB = 0 if len(userInfo) == 0 or userInfo[0][0] == None else userInfo[0][0]
        #更新用户信息
        setDict = {
            "gameUID": self.children[0].value,
            "dcMoney": 1 + dcMoneyB,
            "lastChangeTs": lastChangeTs,
            "lastChangeT": lastChangeT,
            "guildName": interaction.guild.name,
            "isbot": 1 if interaction.user.bot == True else 0,
            "dcUserName": interaction.user.name
        }
        whereDict = {"dcUserId": interaction.user.id,"guildID": interaction.guild.id}
        self.useMysql.insert_data(table_name='user_info',set_dict=setDict,where_dict=whereDict)
        #插入log日志
        setDict2 = {
            'changeTime': lastChangeT,
            'dcMoneyChange': 1,
            'dcMoneyChangeBefore': dcMoneyB,
            'dcMoneyChangeAfter': 1 + dcMoneyB,
            "guildName": interaction.guild.name
        }
        whereDict1 = {
            'dcUserId': interaction.user.id,
            'changeReason': f"{interaction.channel.name}：{interaction.channel.id}频道进行绑定。UID：{self.children[0].value}",
            'changeTs': lastChangeTs,
            "guildID": interaction.guild.id

        }
        self.useMysql.insert_data(table_name="user_data_change_log",set_dict=setDict2,where_dict=whereDict1)
        sendMessage = self.hitText["bindSuccess"][self.label_dict[int(interaction.channel.id)]["useLanguage"]].replace("{0}",str(self.children[0].value))
        await interaction.response.send_message(sendMessage,ephemeral=True,delete_after=3600)
