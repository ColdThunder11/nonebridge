# nonebridge
A adapter event bridge for nonebot2 makes plugins run at different adapter without any modify   
~~一个让你能够在不修改插件的情况下使其运行在不同adapter中的魔法bridge~~
## 还在开发中请勿使用
女生自用插件，目前仅支持让为onebotv11编写的插件运行在自己写的[nonebot-adapter-telegram](https://github.com/ColdThunder11/nonebot-adapter-telegram)上，仅会支持有限的消息类型和API模拟   
## 支持的类型
- [x] 文字
- [ ] 图片

## 支持的额外API
~~还没有~~

## 使用方法
在bot.py紧随nonebot之后导入nonebridge，必须在任何adapter导入之前导入nonebridge