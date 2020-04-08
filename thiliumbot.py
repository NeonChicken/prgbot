#!/usr/bin/env python3
import discord

import command_handlers as commands
from command_handlers import handler_dict
from secrets import token

client = discord.Client()
prefix = '?'

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if '69' in message.content.split():
        await message.channel.send('nice')

    for cmd in handler_dict.keys():
        if message.content.startswith(prefix + cmd):
            response = handler_dict[cmd](message)
            await message.channel.send(response)

client.run(token)
