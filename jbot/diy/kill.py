#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import traceback
import re

from telethon import events
from .. import chat_id, jdbot, logger


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/kill$'))
async def kill(event):
    try:
        info = ""
        msg = await jdbot.send_message(chat_id, '正在查询进程，请稍后')
        cmd = "ps -ef | grep -E '(node|python).*.(js|py)' | grep -Ev 'grep|timeout|build' | awk '{print $1,$5}'"
        output = os.popen(cmd).readlines()
        for x in output:
            x = x.replace('\n', '').split(' ')
            pid = x[0].ljust(10, ' ')
            pid_name = x[1]
            if pid_name != '-c':
                info += f"/kill{pid}\t`{pid_name}`\n"
        if info:
            await jdbot.edit_message(msg, info)
        else:
            await jdbot.edit_message(msg, '当前系统未执行任何脚本')
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


@jdbot.on(events.NewMessage(chats=chat_id, from_users=chat_id, pattern=r'^/kill\d+$'))
async def killOne(event):
    try:
        info = ""
        theid = event.message.text.replace("/kill", "")
        msg = await jdbot.send_message(chat_id, '开始执行，请稍后')
        cmd = "ps -ef | grep -E '(node|python).*.(js|py)' | grep -Ev 'grep|timeout|build' | awk '{print $1,$5}'"
        output = os.popen(cmd).readlines()
        for x in output:
            x = x.replace('\n', '').split(' ')
            pid = x[0].ljust(10, ' ')
            pid_name = x[1]
            if pid_name != '-c':
                info = info + "/kill" + pid + '' + pid_name + '\n'
        if info:
            if theid in info:
                pid_name = re.findall(f"{theid}\s*([^\n]+)", info)[0]
                os.system('kill -9 ' + theid)
                await jdbot.edit_message(msg, f'成功结束进程：`{pid_name}`')
            else:
                await jdbot.edit_message(msg, '该进程不存在')
        else:
            await jdbot.edit_message(msg, '当前系统未执行任何脚本')
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")
