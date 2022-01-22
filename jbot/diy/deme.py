
from telethon import events
from .. import client, chat_id, jdbot, logger, mybot
import os, asyncio, traceback

@client.on(events.NewMessage(from_users=chat_id, pattern=r'^-d\s?[0-9]*$', outgoing=True))
async def del_msg(event):
    try:
        if mybot['开启人形'].lower() == 'false':
            return
        num = event.raw_text.replace(' ', '').split('d')
        if len(num) == 2 and num[-1]:
            count = int(num[-1])
        else:
            count = 10
        await event.delete()
        count_buffer = 0
        async for message in client.iter_messages(event.chat_id, from_user="me"):
            if count_buffer == count:
                break
            await message.delete()
            count_buffer += 1
        notification = await client.send_message(event.chat_id, f'已删除{count_buffer}/{count}')
        await asyncio.sleep(0.5)
        await notification.delete()
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")
