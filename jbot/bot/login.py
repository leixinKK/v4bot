
import asyncio, os
from os.path import exists

from telethon import TelegramClient, events

from .. import api_hash, api_id, proxy, proxystart, jdbot, chat_id, _ConfigDir
from ..bot.utils import V4, press_event, row, split_list, backfile
import json, os, re, sys, time, requests
from asyncio import exceptions
from telethon import events, Button



if proxystart:
    client = TelegramClient(f"{_ConfigDir}/user", api_id, api_hash, proxy=proxy, connection_retries=None).start()
else:
    client = TelegramClient(f"{_ConfigDir}/user", api_id, api_hash, connection_retries=None).start()


def restart():
    text = "if [ -d '/jd' ]; then cd /jd/jbot; pm2 start ecosystem.config.js; cd /jd; pm2 restart jbot; else " \
           "ps -ef | grep 'python3 -m jbot' | grep -v grep | awk '{print $1}' | xargs kill -9 2>/dev/null; " \
           "nohup python3 -m jbot >/ql/log/bot/bot.log 2>&1 & fi "
    os.system(text)



@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/user$'))
async def user_login(event):
    try:
        login = False
        sender = event.sender_id
        session = "/jd/config/user.session" if V4 else "/ql/config/user.session"
        async with jdbot.conversation(sender, timeout=120) as conv:
            msg = await conv.send_message("请做出你的选择")
            buttons = [
                Button.inline("重新登录", data="relogin") if os.path.exists(session) else Button.inline("我要登录", data="login"),
                Button.inline('取消会话', data='cancel')
            ]
            msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=split_list(buttons, row))
            convdata = await conv.wait_event(press_event(sender))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                await jdbot.edit_message(msg, '对话已取消')
                return
            else:
                if res == 'relogin':
                    backfile(session)
                await jdbot.delete_messages(chat_id, msg)
                login = True
        if login:
            await client.connect()
            async with jdbot.conversation(sender, timeout=100) as conv:
                msg = await conv.send_message('请输入手机号：\n例如：`+8618888888888`\n前面一定带上区号、中国为+86')
                phone = await conv.get_response()
                await client.send_code_request(phone.raw_text, force_sms=True)
                msg = await conv.send_message('请输入手机验证码:\n例如`12345`\n不要有其他任何字符')
                code = await conv.get_response()
                await client.sign_in(phone.raw_text, code.raw_text)
                await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            restart()
    except asyncio.exceptions.TimeoutError:
        await jdbot.edit_message(msg, '登录已超时，对话已停止')
    except Exception as e:
        await jdbot.send_message(chat_id, '登录失败\n 再重新登录\n' + str(e))
    finally:
        await client.disconnect()
