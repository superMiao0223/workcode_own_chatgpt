# discord_history.py使用方法
## conf文件夹
里面放了info.yaml文件，文件中主要存储了需要用爬取的频道ID、token和guildID

**暂时无需修改里面的token和guildID属性，只需要添加或删除频道ID即可**
目前脚本中使用的是“testGuildInfo”这个属性下的值；如果需要爬取正式环境下的内容，则需要将脚本中 **yamlDictInfo = "testGuildInfo"** 
修改为 **yamlDictInfo = "useGuildInfo"** 且需要修改useGuildInfo这个属性中的值


## image文件夹
此文件夹中内容无需管

## src文件夹
最后生产的文件都会保存在这个文件夹中，请及时查看