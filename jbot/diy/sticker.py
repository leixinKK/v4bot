#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import traceback
from asyncio import sleep
import httpx
from os import remove
from random import random
from math import floor
from redis import StrictRedis
from PIL import Image, ImageOps
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto, MessageMediaWebPage, MessageMediaDice, MessageMediaUnsupported
from io import BytesIO
from telethon.errors.common import AlreadyInConversationError
from telethon.tl.functions.contacts import UnblockRequest

from .. import client, jdbot, chat_id, logger, bot, mybot
from telethon import events


# 依赖
# pip install 'httpx[socks]' redis

#=====================================================
# 💥错误💥】
# 错误原因：cannot identify image file <_io.BytesIO object at 0x7f7b23a35180>
# 有这个错误的 先卸载模块 再重装
# 1.卸载模块 pip uninstall pillow 
# 2.再重装 pip install Pillow

#=====================================================
silent = False # 是否静默模式

#=====================================================
redis = StrictRedis(host="localhost", port="6379", db="15", password="")
# 使用自定义 UA
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
}
# 如果用户提供代理则设置代理
proxies = None
try:
    if bot.get('proxy_user') and bot['proxy_user'] != "代理的username,有则填写，无则不用动":
        proxies = f"{bot['proxy_type']}://{bot['proxy_user']}:{bot['proxy_password']}@{bot['proxy_add']}:{bot['proxy_port']}"
    elif bot['proxy_type'] == "MTProxy":
        proxies = None
    else:
        proxies = f"{bot['proxy_type']}://{bot['proxy_add']}:{bot['proxy_port']}"
except:
    pass
# logger.info(proxies)
_http = httpx.AsyncClient(proxies=proxies, timeout=10.0, headers=headers)
#=====================================================




@client.on(events.NewMessage(from_users=chat_id, pattern=r"^-pic$"))
@client.on(events.MessageEdited(from_users=chat_id, pattern=r"^-pic$"))
async def stickertopic(event):
    """ 获取贴纸转换为图片 """
    try:
        if not event.is_reply or mybot['开启人形'].lower() == 'false':
            return
        try:
            try:
                parameter = event.pattern_match.group(1).split(' ')
                if parameter == ['']:
                    parameter = []
            except BaseException:
                parameter = []
            if len(parameter) >= 1:
                if parameter[0][0].lower() == "n":
                    as_file = True
                elif parameter[0][0].lower() == "y":
                    as_file = False
                elif not parameter[0]:
                    as_file = False
                else:
                    raise IndexError
            else:
                as_file = False
        except:
            await event.edit("出错了呜呜呜 ~ 无效的参数。")
            return
        user = await client.get_me()
        if not user.username:
            user.username = user.first_name
        message = await event.get_reply_message()
        custom_emoji = False
        animated = False
        await event.edit("开始转换...\n0%")
        if message and message.media:
            if isinstance(message.media, MessageMediaPhoto):
                photo = BytesIO()
                photo = await client.download_media(message.photo, photo)
            elif "image" in message.media.document.mime_type.split('/'):
                photo = BytesIO()
                await event.edit("正在转换...\n████40%")
                await client.download_file(message.media.document, photo)
                if (DocumentAttributeFilename(file_name='sticker.webp') in
                        message.media.document.attributes):
                    custom_emoji = True
            elif (DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in
                message.media.document.attributes):
                photo = BytesIO()
                await client.download_file(message.media.document, "AnimatedSticker.tgs")
                for _ in range(len(message.media.document.attributes)):
                    try:
                        break
                    except:
                        pass
                custom_emoji = True
                animated = True
                photo = 1
            else:
                await event.edit("出错了呜呜呜 ~ 目标不是贴纸 。")
                await sleep(2)
                await event.delete()
                return
        else:
            await event.edit("出错了呜呜呜 ~ 目标不是贴纸 。")
            await sleep(2)
            await event.delete()
            return

        if photo:
            if not custom_emoji:
                await event.edit("出错了呜呜呜 ~ 目标不是贴纸 。")
                await sleep(2)
                await event.delete()
                return

            if not animated:
                await event.edit("正在转换...\n███████70%")
                image = Image.open(photo)
                filename = "sticker"+str(random())[2:]+".png"
                image.save(filename, "PNG")
            else:
                await event.edit("出错了呜呜呜 ~ 目标不是**静态**贴纸 。")
                await sleep(2)
                await event.delete()
                return
            await event.edit("正在上传...\n██████████99%")
            await client.send_file(event.chat_id, filename, force_document=as_file)
            try:
                await event.delete()
            except:
                pass
            try:
                remove(filename)
            except:
                pass
            try:
                remove("AnimatedSticker.tgs")
            except:
                pass
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


@client.on(events.NewMessage(from_users=chat_id, pattern=r'^-[sS](?: |$)([\s\S]*)'))
@client.on(events.MessageEdited(from_users=chat_id, pattern=r'^-[sS](?: |$)([\s\S]*)'))
async def sticker(event):
    """ 获取图像/贴纸并将其添加到贴纸中。 """
    # 首先解封 sticker Bot
    try:
        if not event.is_reply or mybot['开启人形'].lower() == 'false':
            return
        try:
            event.parameter = event.pattern_match.group(1).split(' ')
            event.arguments = event.pattern_match.group(1)
            if event.parameter == ['']:
                event.parameter = []
        except BaseException:
            event.parameter = None
            event.arguments = None
        try:
            await event.client(UnblockRequest(id=429000))
        except:
            pass
        pic_round = False
        is_batch = False
        to_sticker_set = False
        package_name = ""
        if redis_status():
            if redis.get("sticker.round"):
                pic_round = True
            if len(event.parameter) >= 1:
                # s merge
                if event.parameter[0] == "merge" or event.parameter[0] == "m":
                    is_batch = True
                    # s merge png <package_name> <number>
                    try:
                        if event.parameter[3].isnumeric():
                            if "png" in event.parameter[1]:
                                pic_round = False
                            else:
                                pic_round = True
                            package_name = event.parameter[2]
                    except:
                        # 异常，多半是数组越界，不处理，继续参数校验
                        pass
                    try:
                        # s merge <package_name> <number>
                        if event.parameter[2].isnumeric():
                            if "png" in event.parameter[1]:
                                pic_round = False
                                package_name = event.parameter[2]
                            else:
                                package_name = event.parameter[1]
                        # s merge png <package_name>
                        elif "png" in event.parameter[1]:
                            pic_round = False
                            package_name = event.parameter[2]
                        # s merge <package_name> <number>
                        else:
                            package_name = event.parameter[1]

                    except:
                        # 异常，多半是数组越界
                        # s merge <package_name>
                        try:
                            if "png" in event.parameter[1]:
                                raise Exception()
                            package_name = event.parameter[1]
                        except:
                            # 命令错误
                            try:
                                await event.edit("命令参数错误！")
                            except:
                                pass
                            return

                elif event.parameter[0] == "to":
                    pass
                # s <png | number> | error
                else:
                    if event.parameter[0] == "set_round":
                        if pic_round:
                            redis.delete("sticker.round")
                            try:
                                await event.edit("已关闭贴纸自动转换圆角功能")
                            except:
                                pass
                        else:
                            redis.set("sticker.round", "true")
                            try:
                                await event.edit("已开启贴纸自动转换圆角功能")
                            except:
                                pass
                        return
                    elif "png" in event.parameter[0]:
                        pic_round = False
                        # s <number>
                    elif event.parameter[0].isnumeric():
                        pass
                    elif isEmoji(event.parameter[0]) or len(event.parameter[0]) == 1:
                        pass
                    else:
                        try:
                            await event.edit("命令参数错误！")
                        except:
                            pass
                        return

        # 是否添加到指定贴纸包
        if len(event.parameter) >= 1:
            if "to" in event.parameter:
                if len(event.parameter) == 3:  # <emoji> to <sticker_pack>
                    to_sticker_set = event.parameter[2]
                    if redis_status():
                        redis.set("sticker.to", to_sticker_set)
                if len(event.parameter) == 2:
                    to_sticker_set = event.parameter[1]
                    if redis_status():
                        redis.set("sticker.to", to_sticker_set)
                else:
                    if redis_status():
                        if redis.get("sticker.to"):
                            to_sticker_set = redis.get("sticker.to").decode()
                        else:
                            await event.edit("出错了，没有指定贴纸包")
                            return
                    else:
                        await event.edit("出错了，没有指定贴纸包")
                        return

        user = await client.get_me()
        if not user.username:
            user.username = user.first_name

        custom_emoji = False
        animated = False
        emoji = ""

        if is_batch:
            # 多张
            """ 在回复消息后合并每个贴纸。 """
            if not event.reply_to_msg_id:
                await event.edit("出错了，您好像没有回复一条消息。")
                return
            input_chat = await event.get_input_chat()
            count = 0
            scount = 0
            result = ""
            if event.parameter[0] == "m":
                message = await event.get_reply_message()
                await single_sticker(animated, event, custom_emoji, emoji, message, pic_round, user,
                                    package_name, to_sticker_set)
            else:
                async for message in event.client.iter_messages(input_chat, min_id=event.reply_to_msg_id):
                    count += 1
                    if message and message.media:
                        scount += 1
                        try:
                            if not silent:
                                await event.edit(f"正在处理第【{count}】条消息。")
                        except:
                            pass
                        result = await single_sticker(animated, event, custom_emoji, emoji, message, pic_round, user,
                                                    package_name, to_sticker_set)
                        await sleep(.5)
                try:
                    await event.edit(f"{result}\n共处理了【{scount}】张贴纸。", parse_mode='md')
                except:
                    pass
            await sleep(9)
            try:
                await event.delete()
            except:
                pass
        else:
            # 单张收集图片
            message = await event.get_reply_message()
            try:
                await single_sticker(animated, event, custom_emoji, emoji, message, pic_round, user, "", to_sticker_set)
            except FileExistsError:
                await event.edit("出错了呜呜呜 ~ 这个贴纸包已满")
                pass
    except Exception as e:
        title = "★错误★"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + e.__traceback__.tb_frame.f_code.co_name
        details = "错误详情：第 " + str(e.__traceback__.tb_lineno) + " 行"
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n{details}\n{traceback.format_exc()}\n{tip}")
        logger.error(f"错误--->{str(e)}")


async def single_sticker(animated, context, custom_emoji, emoji, message, pic_round, user, package_name,
                         to_sticker_set):
    try:
        if not silent:
            await context.edit("收集图像/贴纸中 . . .")
    except:
        pass
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            photo = BytesIO()
            photo = await client.download_media(message.photo, photo)
        elif isinstance(message.media, MessageMediaWebPage):
            try:
                await context.edit("出错了，不支持此文件类型。")
            except:
                pass
            return
        elif isinstance(message.media, MessageMediaDice):
            try:
                await context.edit("出错了，不支持此文件类型。")
            except:
                pass
            return
        elif isinstance(message.media, MessageMediaUnsupported):
            try:
                await context.edit("出错了，不支持此文件类型。")
            except:
                pass
            return
        elif "image" in message.media.document.mime_type.split('/'):
            photo = BytesIO()
            try:
                if not silent:
                    await context.edit("下载图片中 . . .")
            except:
                pass
            await client.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                emoji = message.media.document.attributes[1].alt
                custom_emoji = True
                if not emoji:
                    custom_emoji = False
        elif (DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in
              message.media.document.attributes):
            photo = BytesIO()
            await client.download_file(message.media.document, "AnimatedSticker.tgs")
            for index in range(len(message.media.document.attributes)):
                try:
                    emoji = message.media.document.attributes[index].alt
                    break
                except:
                    pass
            custom_emoji = True
            if not emoji:
                custom_emoji = False
            animated = True
            photo = 1
        else:
            try:
                await context.edit("出错了，不支持此文件类型。")
            except:
                pass
            return
    else:
        try:
            await context.edit("出错了，请回复带有图片/贴纸的消息。")
        except:
            pass
        return

    if photo:
        split_strings = context.text.split()
        if not custom_emoji:
            emoji = "👀"
        pack = 1
        sticker_already = False
        if to_sticker_set:
            # 指定贴纸包 + emoji
            if split_strings[1].isnumeric():
                pack = int(split_strings[1])
            else:
                if split_strings[1].replace("png", "").replace("to", "") != "":
                    emoji = split_strings[1].replace("png", "").replace("to", "")
        elif package_name:
            # 批量处理贴纸无法指定emoji，只获取第几个pack
            # s merge png <package_name> <number>
            if len(split_strings) == 5:
                pack = split_strings[4]
            # s merge <package_name> <number>
            elif len(split_strings) == 4:
                pack = split_strings[3]
        else:
            if len(split_strings) == 3:
                # s png <number|emoji>
                pack = split_strings[2]
                if split_strings[1].replace("png", "") != "":
                    emoji = split_strings[1].replace("png", "")
            elif len(split_strings) == 2:
                # s <number|emoji>
                if split_strings[1].isnumeric():
                    pack = int(split_strings[1])
                else:
                    if split_strings[1].replace("png", "") != "":
                        emoji = split_strings[1].replace("png", "")

        if not isinstance(pack, int):
            pack = 1

        if package_name:
            # merge指定package_name
            pack_name = f"{user.username}_{package_name}_{pack}"
            pack_title = f"@{user.username} 的私藏 ({package_name}) ({pack})"
        elif to_sticker_set:
            pack_name = to_sticker_set
            pack_title = f"@{user.username} 的私藏 ({package_name}) ({pack})"
        else:
            pack_name = f"{user.username}_{pack}"
            pack_title = f"@{user.username} 的私藏 ({pack})"
        command = '/newpack'
        file = BytesIO()

        if not animated:
            try:
                if not silent:
                    await context.edit("调整图像大小中 . . .")
            except:
                pass
            image = await resize_image(photo)
            if pic_round:
                try:
                    if not silent:
                        await context.edit("图片圆角处理中 . . .")
                except:
                    pass
                image = await rounded_image(image)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            if not to_sticker_set:
                pack_name += "_animated"
                pack_title += " (animated)"
                command = '/newanimated'

        try:
            response = await _http.get(f'https://t.me/addstickers/{pack_name}')
        except UnicodeEncodeError:
            pack_name = 's' + hex(context.sender_id)[2:]
            if animated:
                pack_name = 's' + hex(context.sender_id)[2:] + '_animated'
            response = await _http.get(f'https://t.me/addstickers/{pack_name}')
        if not response.status_code == 200:
            try:
                await context.edit("连接到 Telegram 服务器失败 . . .")
            except:
                pass
            return
        http_response = response.text.split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in \
                http_response:
            for _ in range(20):  # 最多重试20次
                try:
                    async with client.conversation('Stickers') as conversation:
                        await conversation.send_message('/cancel')
                        await conversation.get_response()
                        await client.send_read_acknowledge(conversation.chat_id)
                        await conversation.send_message('/addsticker')
                        await conversation.get_response()
                        await client.send_read_acknowledge(conversation.chat_id)
                        await conversation.send_message(pack_name)
                        chat_response = await conversation.get_response()
                        while chat_response.text == "Whoa! That's probably enough stickers for one set, " \
                                                    "give it a break. " \
                                                    "A set can't have more than 120 stickers at the moment.":
                            pack += 1

                            # 指定贴纸包已满时直接报错
                            if to_sticker_set:
                                raise FileExistsError
                            if package_name:
                                # merge指定package_name
                                pack_name = f"{user.username}_{package_name}_{pack}"
                                pack_title = f"@{user.username} 的私藏 ({package_name}) ({pack})"
                            else:
                                pack_name = f"{user.username}_{pack}"
                                pack_title = f"@{user.username} 的私藏 ({pack})"
                            try:
                                if not silent:
                                    if package_name:
                                        await context.edit(
                                            "切换到私藏 " + str(package_name) + str(pack) + "上一个贴纸包已满 . . .")
                                    else:
                                        await context.edit(
                                            "切换到私藏 " + str(pack) + "上一个贴纸包已满 . . .")
                            except:
                                pass
                            await conversation.send_message(pack_name)
                            chat_response = await conversation.get_response()
                            if chat_response.text == "Invalid set selected.":
                                await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                                  context, file, emoji)
                                try:
                                    await context.edit(
                                        f"这张图片/贴纸已经被添加到 [这个](t.me/addstickers/{pack_name}) 贴纸包",
                                        parse_mode='md')
                                except:
                                    pass
                                return
                        try:
                            await upload_sticker(animated, message, context, file, conversation)
                        except ValueError:
                            try:
                                await context.edit("出错了，请回复带有图片/贴纸的消息。")
                            except:
                                pass
                            return
                        await conversation.get_response()
                        await conversation.send_message(emoji)
                        await client.send_read_acknowledge(conversation.chat_id)
                        await conversation.get_response()
                        await conversation.send_message('/done')
                        await conversation.get_response()
                        await client.send_read_acknowledge(conversation.chat_id)
                        break
                except AlreadyInConversationError:
                    if not sticker_already and not silent:
                        try:
                            await context.edit("另一个命令正在添加贴纸, 重新尝试中")
                        except:
                            pass
                        sticker_already = True
                    else:
                        pass
                    await sleep(.5)
                except Exception:
                    raise
        else:
            if not silent:
                try:
                    await context.edit("贴纸包不存在，正在创建 . . .")
                except:
                    pass
            async with client.conversation('Stickers') as conversation:
                await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                  context, file, emoji)

        try:
            await context.edit(
                f"这张图片/贴纸已经被添加到 [这个](t.me/addstickers/{pack_name}) 贴纸包",
                parse_mode='md')
        except:
            pass
        if package_name:
            return f"这张图片/贴纸已经被添加到 [这个](t.me/addstickers/{pack_name}) 贴纸包"
        else:
            await sleep(5)
            try:
                await context.delete()
            except:
                pass


async def add_sticker(conversation, command, pack_title, pack_name, animated, message, context, file, emoji):
    await conversation.send_message("/cancel")
    await conversation.get_response()
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message(command)
    await conversation.get_response()
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message(pack_title)
    await conversation.get_response()
    await client.send_read_acknowledge(conversation.chat_id)
    try:
        await upload_sticker(animated, message, context, file, conversation)
    except ValueError:
        try:
            await context.edit("出错了，请回复带有图片/贴纸的消息。")
        except:
            pass
        return
    await conversation.get_response()
    await conversation.send_message(emoji)
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message("/publish")
    if animated:
        await conversation.get_response()
        await conversation.send_message(f"<{pack_title}>")
    await conversation.get_response()
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message("/skip")
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message(pack_name)
    await client.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await client.send_read_acknowledge(conversation.chat_id)


async def upload_sticker(animated, message, context, file, conversation):
    if animated:
        if not silent:
            try:
                await context.edit("上传动图中 . . .")
            except:
                pass
        await conversation.send_file("AnimatedSticker.tgs", force_document=True)
        remove("AnimatedSticker.tgs")
    else:
        file.seek(0)
        if not silent:
            try:
                await context.edit("上传图片中 . . .")
            except:
                pass
        await conversation.send_file(file, force_document=True)


async def resize_image(photo):
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)
    return image


async def rounded_image(image):
    w = image.width
    h = image.height
    resize_size = 0
    # 比较长宽
    if w > h:
        resize_size = h
    else:
        resize_size = w
    half_size = floor(resize_size / 2)

    # 获取圆角模版，切割成4个角
    tl = (0, 0, 256, 256)
    tr = (256, 0, 512, 256)
    bl = (0, 256, 256, 512)
    br = (256, 256, 512, 512)
    border = Image.open('pagermaid/static/images/rounded.png').convert('L')
    tlp = border.crop(tl)
    trp = border.crop(tr)
    blp = border.crop(bl)
    brp = border.crop(br)

    # 缩放四个圆角
    tlp = tlp.resize((half_size, half_size))
    trp = trp.resize((half_size, half_size))
    blp = blp.resize((half_size, half_size))
    brp = brp.resize((half_size, half_size))

    # 扩展四个角大小到目标图大小
    # tlp = ImageOps.expand(tlp, (0, 0, w - tlp.width, h - tlp.height))
    # trp = ImageOps.expand(trp, (w - trp.width, 0, 0, h - trp.height))
    # blp = ImageOps.expand(blp, (0, h - blp.height, w - blp.width, 0))
    # brp = ImageOps.expand(brp, (w - brp.width, h - brp.height, 0, 0))

    # 四个角合并到一张新图上
    ni = Image.new('RGB', (w, h), (0, 0, 0)).convert('L')
    ni.paste(tlp, (0, 0))
    ni.paste(trp, (w - trp.width, 0))
    ni.paste(blp, (0, h - blp.height))
    ni.paste(brp, (w - brp.width, h - brp.height))

    # 合并圆角和原图
    image.putalpha(ImageOps.invert(ni))

    return image


def isEmoji(content):
    if not content:
        return False
    if u"\U0001F600" <= content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content <= u"\U0001F1FF":
        return True
    else:
        return False

def redis_status():
    try:
        redis.ping()
        return True
    except BaseException:
        return False