import asyncio, os
from os.path import exists
from telethon import TelegramClient, events
from .. import client, jdbot, chat_id, _JdDir, logger
from ..bot.utils import V4, press_event, row, split_list
import json, os, re, sys, time, requests, traceback
from asyncio import exceptions
from telethon import events, Button


userfile = "/jd/jbot/diy/user.py" if V4 else "/ql/jbot/diy/user.py"


def restart():
    text = "if [ -d '/jd' ]; then cd /jd/jbot; pm2 start ecosystem.config.js; cd /jd; pm2 restart jbot; else " \
           "ps -ef | grep 'python3 -m jbot' | grep -v grep | awk '{print $1}' | xargs kill -9 2>/dev/null; " \
           "nohup python3 -m jbot >/ql/log/bot/bot.log 2>&1 & fi "
    os.system(text)


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/user$'))
async def user_login(event):
    try:
        if not os.path.exists(userfile):
            await jdbot.send_message(chat_id, f'user.py不存在\n请先执行以下命令\n再执行：/user\n\n```/cmd cd {_JdDir}/jbot/diy && wget https://ghproxy.com/https://raw.githubusercontent.com/Annyoo2021/mybot/main/jbot/diy/user.py```')
            return
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
                await jdbot.delete_messages(chat_id, msg)
                login = True
        if login:
            await client.connect()
            async with jdbot.conversation(sender, timeout=100) as conv:
                msg = await conv.send_message('请输入手机号：\n例如：`+8618888888888`\n前面一定带上区号、中国为+86')
                phone = await conv.get_response()
                await client.send_code_request(phone.raw_text, force_sms=True)
                msg = await conv.send_message('请输入手机验证码:\n例如：`code12345code`\n两边的**code**必须有！')
                code = await conv.get_response()
                await client.sign_in(phone.raw_text, code.raw_text.replace('code', ''))
                await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            restart()
    except asyncio.exceptions.TimeoutError:
        await jdbot.edit_message(msg, '登录已超时，对话已停止')
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")
    finally:
        await client.disconnect()
