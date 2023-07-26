# nonebridge
A adapter event bridge for nonebot2 makes plugins running on different adapters without any modify   
一个让你能够在不修改插件的情况下使其运行在不同adapter中的魔法bridge，开发目的是为了给[Yuki Clanbattle](https://github.com/ColdThunder11/yuki_clanbattle)提供Telegram支持
## 还在开发中请勿生产环境使用
女生自用插件，目前仅支持让为onebotv11编写的插件运行在自己写的[nonebot-adapter-telegram](https://github.com/ColdThunder11/nonebot-adapter-telegram)上，仅会支持有限的消息类型和API模拟   
目前不支持~~主动发送消息和~~向非事件触发的聊天发送消息，支持主动向群聊使用send_group_msg发送群组消息了(必须在tg端收到任意消息后虚假的obv11 bot连接才会被注册)
## 支持的接收类型
- [x] 纯文字(MessageSegment.text)
- [x] 图片(MessageSegment.image)

## 支持的发送类型
- [x] 文字(MessageSegment.text)
- [x] 图片(MessageSegment.image)
- [x] AT(MessageSegment.at)
- [x] 语音(MessageSegment.record)

## 支持的额外API
| Onebot v11 API        | 对应的Telegarm API                                                       |
| --------------------- | ------------------------------------------------------------------------ |
| get_group_info        | getChat和getChatMemberCount                                              |
| get_group_member_list | getChatAdministrators(由于tg并没有提供相关API，仅能够直接获取管理员信息) |
| get_group_member_info | getChatMember                                                            |
| send_group_msg        | ---                                                                      |
## 配置
nonebridge所需的配置直接写入到nonebot2的.env文件内即可
```
nonebridge_ob11_caption_ahead_photo: 将从telegram收到的带文字描述的图片消息中文字部分作为文字消息在ob11的消息段中前置以配合ob11中大部分插件的习惯写法，默认为True
nonebridge_httpx_hook: 安装httpx钩子以拦截获取qq头像的http api，默认为False
ob11_plugin_list: [] 需要强制处理为ob11消息的插件，该插件内的matcer将不会被tg消息触发
```

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