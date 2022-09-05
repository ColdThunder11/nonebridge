# nonebridge
A adapter event bridge for nonebot2 makes plugins run at different adapter without any modify   
~~一个让你能够在不修改插件的情况下使其运行在不同adapter中的魔法bridge~~
## 还在开发中请勿使用
女生自用插件，目前仅支持让为onebotv11编写的插件运行在自己写的[nonebot-adapter-telegram](https://github.com/ColdThunder11/nonebot-adapter-telegram)上，仅会支持有限的消息类型和API模拟   
目前仅支持群聊消息触发，不支持私聊和主动发送消息
## 支持的接收类型
- [x] 纯文字(MessageSegment.text)
- [ ] 图片

## 支持的发送类型
- [x] 文字(MessageSegment.text)
- [x] 图片(MessageSegment.image)

## 支持的额外API
~~还没有~~

## 使用方法
同时安装并两个adapter，在bot.py紧随nonebot之后导入nonebridge，必须在任何adapter导入之前导入nonebridge，需要同时注册两个Adapter才能正常运行   
### Example bot.py
```python
import nonebot
import nonebridge
from nonebot.adapters.onebot.v11 import Adapter as OneBot_V11_Adapter
from nonebot.adapters.telegram.adapter import Adapter as Telegram_Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(OneBot_V11_Adapter)
driver.register_adapter(Telegram_Adapter)
nonebot.load_plugin("your_onebotv11_plugin")

if __name__ == "__main__":
    nonebot.run()   
```