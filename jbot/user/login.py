
import asyncio, os
from os.path import exists

from telethon import TelegramClient, events

from .. import api_hash, api_id, proxy, proxystart, bot, jdbot, chat_id, _ConfigDir, proxyType, connectionType
from ..bot.utils import V4, press_event, row, split_list, backfile
import json, os, re, sys, time, requests
from asyncio import exceptions
from telethon import events, Button



if bot.get('proxy_user') and bot['proxy_user'] != "代理的username,有则填写，无则不用动":
    proxy = {
        'proxy_type': bot['proxy_type'],
        'addr':  bot['proxy_add'],
        'port': bot['proxy_port'],
        'username': bot['proxy_user'],
        'password': bot['proxy_password']}
elif proxyType == "MTProxy":
    proxy = (bot['proxy_add'], bot['proxy_port'], bot['proxy_secret'])
else:
    proxy = (bot['proxy_type'], bot['proxy_add'], bot['proxy_port'])

# 开启tg对话
if proxystart and bot.get('noretry') and bot['noretry']:
    client = TelegramClient(f'{_ConfigDir}/user', api_id, api_hash, connection=connectionType,
                           proxy=proxy)
elif proxystart:
    client = TelegramClient(f'{_ConfigDir}/user', api_id, api_hash, connection=connectionType,
                           proxy=proxy, connection_retries=None)
elif bot.get('noretry') and bot['noretry']:
    client = TelegramClient(f'{_ConfigDir}/user', api_id, api_hash)
else:
    client = TelegramClient(f'{_ConfigDir}/user', api_id, api_hash,
                           connection_retries=None)


def restart():
    text = "if [ -d '/jd' ]; then cd /jd/jbot; pm2 start ecosystem.config.js; cd /jd; pm2 restart jbot; else " \
           "ps -ef | grep 'python3 -m jbot' | grep -v grep | awk '{print $1}' | xargs kill -9 2>/dev/null; " \
           "nohup python3 -m jbot >/ql/log/bot/bot.log 2>&1 & fi "
    os.system(text)

def start():
    file = "/jd/config/botset.json" if V4 else "/ql/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    botset = botset.replace('user": "False"', 'user": "True"')
    with open(file, "w", encoding="utf-8") as f2:
        f2.write(botset)
    restart()


def close():
    file = "/jd/config/botset.json" if V4 else "/ql/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    botset = botset.replace('user": "True"', 'user": "False"')
    with open(file, "w", encoding="utf-8") as f2:
        f2.write(botset)
    restart()


def state():
    file = "/jd/config/botset.json" if V4 else "/ql/config/botset.json"
    with open(file, "r", encoding="utf-8") as f1:
        botset = f1.read()
    if 'user": "True"' in botset:
        return True
    else:
        return False


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
                Button.inline("关闭user", data="close") if state() else Button.inline("开启user", data="start"),
                Button.inline('取消会话', data='cancel')
            ]
            msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=split_list(buttons, row))
            convdata = await conv.wait_event(press_event(sender))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                await jdbot.edit_message(msg, '对话已取消')
                return
            elif res == 'close':
                await jdbot.edit_message(msg, "关闭成功，准备重启机器人！")
                close()
            elif res == 'start':
                await jdbot.edit_message(msg, "开启成功，请确保session可用，否则请进入容器修改botset.json并删除user.session！\n现准备重启机器人！")
                start()
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
                msg = await conv.send_message('请输入手机验证码:\n例如：`12345`\n不要有其他任何字符')
                code = await conv.get_response()
                await client.sign_in(phone.raw_text, code.raw_text)
                await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            start()
    except asyncio.exceptions.TimeoutError:
        await jdbot.edit_message(msg, '登录已超时，对话已停止')
    except Exception as e:
        await jdbot.send_message(chat_id, '登录失败\n 再重新登录\n' + str(e))
    finally:
        await client.disconnect()
