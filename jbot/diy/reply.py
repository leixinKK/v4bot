from telethon import events

from .. import client

@client.on(events.NewMessage(pattern=r'^-re?\s?[0-9]*$', outgoing=True))
async def reply(event):
    num = event.raw_text.split(' ')
    if isinstance(num, list) and len(num) == 2:
        num = int(num[-1])
    else:
        num = 1
    reply = await event.get_reply_message()
    await event.delete()
    for _ in range(0, num):
        await reply.forward_to(int(event.chat_id))