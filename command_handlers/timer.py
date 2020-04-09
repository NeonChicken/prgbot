import asyncio
from functools import partial

async def run(message):
    minute_duration = int(message.content.split()[1])
    duration = minute_duration * 60
    await message.channel.send("{} minute timer started".format(minute_duration))

    notification_breaks = [(60, 'one minute'), (300, '5 minutes'), (600 , '10 minutes'), (1800, 'half an hour')]

    notification_breaks.sort(reverse=True, key=lambda mark: mark[0])
    for time_mark in notification_breaks:
        if duration > time_mark[0]:
            await asyncio.sleep(duration - time_mark[0])
            duration = time_mark[0]
            await message.channel.send(time_mark[1].capitalize() + ' remaining')

    await asyncio.sleep(duration)
    await message.channel.send("Time's up!")
