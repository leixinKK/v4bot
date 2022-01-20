#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .. import chat_id, jdbot, client, logger, api_id, api_hash, proxystart, proxy, _ConfigDir, _ScriptsDir, _JdbotDir, _JdDir, TOKEN, traceback
from ..bot.utils import cmd, backfile, jdcmd, V4, QL, _ConfigFile, myck
from ..diy.utils import getbean, my_chat_id
from telethon import events, TelegramClient
import re, asyncio, time, datetime, os, sys, requests, json

bot_id = int(TOKEN.split(":")[0])

@client.on(events.NewMessage(chats=[bot_id, my_chat_id], from_users=chat_id, pattern=r"^-u$"))
async def user(event):
    try:
        await event.edit(r'**监控已正常启动**')
        await sleep(5)
        await event.delete()
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")
