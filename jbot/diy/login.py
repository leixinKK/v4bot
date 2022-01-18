
import asyncio, os, json, os, re, sys, time, requests, traceback, qrcode
from telethon import TelegramClient, events
from .. import client, jdbot, chat_id, _JdDir, logger, QR_IMG_FILE
from ..bot.utils import V4, press_event, row, split_list
from asyncio import exceptions
from telethon import events, Button

userfile = "/jd/jbot/diy/user.py" if V4 else "/ql/jbot/diy/user.py"

def restart():
    text = "if [ -d '/jd' ]; then cd /jd/jbot; pm2 start ecosystem.config.js; cd /jd; pm2 restart jbot; else " \
           "ps -ef | grep 'python3 -m jbot' | grep -v grep | awk '{print $1}' | xargs kill -9 2>/dev/null; " \
           "nohup python3 -m jbot >/ql/log/bot/bot.log 2>&1 & fi "
    os.system(text)

def creat_qr(text):
    """实例化QRCode生成qr对象"""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.clear()
    # 传入数据
    qr.add_data(text)
    qr.make(fit=True)
    # 生成二维码
    img = qr.make_image()
    # 保存二维码
    img.save(QR_IMG_FILE)

@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/user$'))
async def user_login(event):
    try:
        if not os.path.exists(userfile):
            await jdbot.send_message(chat_id, f'user.py不存在\n请先执行以下命令\n再执行：/user\n\n```/cmd cd {_JdDir}/jbot/diy && wget https://ghproxy.com/https://raw.githubusercontent.com/Annyoo2021/mybot/main/jbot/diy/user.py```')
            return
        tellogin, qrlogin = False, False
        sender = event.sender_id
        session = "/jd/config/user.session" if V4 else "/ql/config/user.session"
        async with jdbot.conversation(sender, timeout=120) as conv:
            while True:
                msg = await conv.send_message("请做出你的选择")
                buttons = [
                    Button.inline("重新登录", data="relogin") if os.path.exists(session) else Button.inline("我要登录", data="login"),
                    Button.inline('取消会话', data='cancel')
                ]
                opt_btns = [
                    Button.inline('上级目录', data='upper menu'),
                    Button.inline('取消会话', data='cancel')
                ]
                msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=split_list(buttons, row))
                convdata = await conv.wait_event(press_event(sender))
                res = bytes.decode(convdata.data)
                if res == 'cancel':
                    await jdbot.edit_message(msg, '对话已取消')
                    return
                else:
                    btns = [
                        Button.inline('手机登录', data='tellogin'),
                        Button.inline('扫码登录', data='qrlogin')
                    ]
                    newbtns = split_list(btns, row)
                    newbtns.append(opt_btns)
                    msg = await jdbot.edit_message(msg, '请做出你的选择：', buttons=newbtns)
                    convdata = await conv.wait_event(press_event(sender))
                    res2 = bytes.decode(convdata.data)
                    if res2 == 'cancel':
                        await jdbot.edit_message(msg, '对话已取消')
                        conv.cancel()
                        return
                    elif res2 == 'upper menu':
                        await jdbot.delete_messages(chat_id, msg)
                        continue
                    elif res2 == 'tellogin':
                        tellogin = True
                        break
                    else:
                        qrlogin = True
                        break
        if tellogin:
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
        elif qrlogin:
            await client.connect()
            qr_login = await client.qr_login()
            creat_qr(qr_login.url)
            await jdbot.send_message(chat_id, '请使用TG扫描二维码以开启USER', file=QR_IMG_FILE)
            await qr_login.wait(timeout=100)
            await jdbot.send_message(chat_id, '恭喜您已登录成功！\n自动重启中！')
            os.remove(QR_IMG_FILE)
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
