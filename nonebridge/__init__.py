import json
import inspect
import time
from typing import Any, List
from collections.abc import Callable
import nonebot.message
from nonebot.adapters import Bot, Event, Adapter
from nonebot.drivers import Driver
from nonebot.message import run_preprocessor
from nonebot.matcher import Matcher
from nonebot.exception import IgnoredException

loaded_adapter_names: List = []
loaded_adapter: List = []


async def run_handle_event_func_async(*a, **b):
    b["origin_func"] = orig_handle_event_func
    await NonebotHooks.handle_event_hook(*a, **b)
orig_handle_event_func = nonebot.message.handle_event
nonebot.message.handle_event = run_handle_event_func_async

try:
    from nonebot.adapters.telegram.bot import Bot as TgBot
    from nonebot.adapters.telegram.adapter import Adapter as TgAdapter
    from nonebot.adapters.telegram.message import Message as TgMessage
    from nonebot.adapters.telegram.message import MessageSegment as TgMessageSegment
    from nonebot.adapters.telegram.event import MessageEvent as TgMessageEvent
    from nonebot.adapters.telegram.event import PrivateMessageEvent as TgPrivateMessageEvent
    from nonebot.adapters.telegram.event import GroupMessageEvent as TgGroupMessageEvent
    loaded_adapter_names.append("Telegram")
except:
    print("Failed to load nonebot.adapters.telegram.adapter, please ensure nonebot-adapter-antelegram installed")

try:
    from nonebot.adapters.onebot.v11.bot import Bot as Ob11Bot
    from nonebot.adapters.onebot.v11.adapter import Adapter as Ob11Adapter
    from nonebot.adapters.onebot.v11.message import Message as Ob11Message
    from nonebot.adapters.onebot.v11.message import MessageSegment as Ob11MessageSegment
    from nonebot.adapters.onebot.v11.event import MessageEvent as Ob11MessageEvent
    from nonebot.adapters.onebot.v11.event import PrivateMessageEvent as Ob11PrivateMessageEvent
    from nonebot.adapters.onebot.v11.event import GroupMessageEvent as Ob11GroupMessageEvent
    from nonebot.adapters.onebot.v11.event import Sender as Ob11Sender
    loaded_adapter_names.append("Onebot11")
except:
    print("Failed to load nonebot.adapters.telegram.adapter, please ensure nonebot-adapter-onebot installed")


@run_preprocessor
async def before_run_matcher(matcher: Matcher, bot: Bot, event: Event):
    if not matcher.__class__ in bot._alread_run_matcher:
        bot._alread_run_matcher.append(matcher.__class__)
    else:
        raise IgnoredException("Matcher has already been run")


def get_adapter(name: str) -> Adapter:
    for adapter in loaded_adapter:
        if adapter.get_name() == name:
            return adapter
    return None


def Ob11Message2Tg(ob_message: Ob11Message) -> TgMessage:
    tg_msg_seg_list = []
    for msg_seg in ob_message:
        if msg_seg.type == "text":
            tg_msg_seg_list.append(TgMessageSegment.text(msg_seg.data["text"]))
        elif msg_seg.type == "image":
            tg_msg_seg_list.append(
                TgMessageSegment.photo(msg_seg.data["file"]))
    if len(tg_msg_seg_list) > 0:
        return TgMessage(tg_msg_seg_list)
    else:
        return None


def TgMessage2Ob11(tg_message: TgMessage) -> Ob11Message:
    ob11_msg_seg_list = []
    for msg_seg in tg_message:
        if msg_seg.type == "text":
            ob11_msg_seg_list.append(
                Ob11MessageSegment.text(msg_seg.data["text"]))
        elif msg_seg.type == "photo":
            # Todo
            pass
            # ob11_msg_seg_list.append(Ob11MessageSegment.image(msg_seg.data["text"]))
    if len(ob11_msg_seg_list) > 0:
        return Ob11Message(ob11_msg_seg_list)
    else:
        return None


def TgEvent2Ob11(tg_event: TgMessageEvent) -> Ob11MessageEvent:
    sender_json = {
        "user_id": tg_event.message.from_.id,
        "nickname": tg_event.message.from_.first_name if not tg_event.message.from_.last_name else tg_event.message.from_.first_name + tg_event.message.from_.last_name,
    }
    if isinstance(tg_event, TgGroupMessageEvent):
        msg: Ob11Message = TgMessage2Ob11(tg_event.get_message())
        if not msg:
            return None
        return Ob11GroupMessageEvent(message=msg, group_id=tg_event.message.chat.id, user_id=tg_event.message.from_.id,
                                     self_id=0, message_id=tg_event.message.message_id, time=int(time.time()), post_type="message", sub_type="1",
                                     message_type="group", raw_message=msg.extract_plain_text(), font=0, sender=Ob11Sender.parse_obj(sender_json))
    elif isinstance(tg_event, TgPrivateMessageEvent):
        msg: Ob11Message = TgMessage2Ob11(tg_event.get_message())
        if not msg:
            return None
        return Ob11PrivateMessageEvent(message=msg, group_id=tg_event.message.chat.id, user_id=tg_event.message.from_.id,
                                       self_id=0, message_id=tg_event.message.message_id, time=int(time.time()), post_type="message", sub_type="1",
                                       message_type="private", raw_message=msg.extract_plain_text(), font=0, sender=Ob11Sender.parse_obj(sender_json))


def check_in_in_hook(check_func_name: str = None):
    stack = inspect.stack()
    self_func_name = stack[1].function if not check_func_name else check_func_name
    call_count = 0
    for frame in stack:
        if frame.function == self_func_name:
            call_count += 1
            if call_count >= 2:
                return True
    return False


class NonebotHooks:

    @staticmethod
    async def handle_event_hook(bot: "Bot", event: "Event", origin_func: Callable):
        if check_in_in_hook():
            return await origin_func(bot, event)
        if isinstance(bot, TgBot):
            if "Onebot11" in loaded_adapter_names:
                if isinstance(event, TgGroupMessageEvent) or isinstance(event, TgPrivateMessageEvent):
                    ob11_event = TgEvent2Ob11(event)
                    if ob11_event:
                        # build bot
                        if adapter := get_adapter("OneBot V11"):
                            ob11_bot = Ob11Bot(adapter, "0")
                            ob11_bot.raw_event = event  # pass origin event to make adapter process easily
                            ob11_bot._alread_run_matcher = []
                            await nonebot.message.handle_event(ob11_bot, ob11_event)
                            bot._alread_run_matcher = ob11_bot._alread_run_matcher
        await origin_func(bot, event)


class TgHooks:

    @staticmethod
    async def call_api_hook(self,
                            api: str,
                            origin_func: Callable,
                            ** data) -> Any:
        return await origin_func(self, api, **data)

    @staticmethod
    def adapter_init(self, driver: Driver, origin_func: Callable, **kwargs: Any):
        loaded_adapter.append(self)
        return origin_func(self, driver, **kwargs)


class Ob11Hooks:

    @staticmethod
    async def call_api_hook(self,
                            api: str,
                            origin_func: Callable,
                            ** data) -> Any:
        if self.self_id == "0":
            if api == "send_msg":
                if data["message_type"] == "group":
                    if adapter := get_adapter("Telegram"):
                        tg_bot = TgBot(adapter, "nonebridge")
                        if hasattr(self, "raw_event"):
                            await tg_bot._process_send_message(self.raw_event, Ob11Message2Tg(data["message"]), False, False)
                        return
                elif data["message_type"] == "private":
                    if adapter := get_adapter("Telegram"):
                        tg_bot = TgBot(adapter, "nonebridge")
                        if hasattr(self, "raw_event"):
                            await tg_bot._process_send_message(self.raw_event, Ob11Message2Tg(data["message"]), False, False)
                        return
            elif api == "get_group_member_info":
                if adapter := get_adapter("Telegram"):
                    tg_bot = TgBot(adapter, "nonebridge")
                    member = await tg_bot.call_api("getChatMember", chat_id=data["group_id"], user_id=data["user_id"])
                    return json.loads(json.dumps({
                        "nickname": member["user"]["first_name"],
                        "card": member["user"]["first_name"],
                        "sex": 0
                    }))
        return await origin_func(self, api, **data)

    @staticmethod
    async def handle_event_hook(bot: "Bot", event: "Event", origin_func: Callable):
        return await origin_func(bot, event)

    @staticmethod
    def adapter_init(self, driver: Driver, origin_func: Callable, **kwargs: Any):
        loaded_adapter.append(self)
        return origin_func(self, driver, **kwargs)


def install_hook(orig_func: Callable, hook_func: Callable):
    async def run_hook_async(*a, **b):
        b["origin_func"] = backup_func
        await hook_func(*a, **b)

    def run_hook(*a, **b):
        b["origin_func"] = backup_func
        hook_func(*a, **b)

    backup_func = orig_func
    if inspect.iscoroutinefunction(backup_func):
        orig_func = run_hook_async
    else:
        orig_func = run_hook


#install_hook(handle_event, NonebotHooks.handle_event_hook)
if "Telegram" in loaded_adapter_names:
    async def run_tg_call_api_func_async(*a, **b):
        b["origin_func"] = orig_tg_call_api_func
        await TgHooks.call_api_hook(*a, **b)
    orig_tg_call_api_func = TgBot.call_api
    TgBot.call_api = run_tg_call_api_func_async

    def run_tg_adapter_init_func_async(*a, **b):
        b["origin_func"] = orig_tg_adapter_init_func
        TgHooks.adapter_init(*a, **b)
    orig_tg_adapter_init_func = TgAdapter.__init__
    TgAdapter.__init__ = run_tg_adapter_init_func_async
    #install_hook(TgAdapter.__init__, TgHooks.adapter_init)
if "Onebot11" in loaded_adapter_names:
    async def run_ob11_call_api_func_async(*a, **b):
        b["origin_func"] = orig_ob11_call_api_func
        await Ob11Hooks.call_api_hook(*a, **b)
    orig_ob11_call_api_func = Ob11Bot.call_api
    Ob11Bot.call_api = run_ob11_call_api_func_async
    #install_hook(Ob11Bot.call_api, Ob11Hooks.call_api_hook)

    def run_ob11_adapter_init_func_async(*a, **b):
        b["origin_func"] = orig_ob11_adapter_init_func
        Ob11Hooks.adapter_init(*a, **b)
    orig_ob11_adapter_init_func = Ob11Adapter.__init__
    Ob11Adapter.__init__ = run_ob11_adapter_init_func_async

    #install_hook(Ob11Adapter.__init__, Ob11Hooks.adapter_init)
print("Nonebridge hooks install success")
