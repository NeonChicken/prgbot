#!/usr/bin/env python3
import importlib

import discord

from secrets import token

client = discord.Client()
prefix = '!'

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if '69' in message.content.split():
        await message.channel.send('nice')

    if message.content.startswith(prefix):
        command = message.content.split()[0][1:]
        try:
            module = importlib.import_module('.' + command, 'command_handlers')
        except ModuleNotFoundError:
            print('Command "{}" not implemented'.format(command))
            return
        
        await module.run(message)

client.run(token)