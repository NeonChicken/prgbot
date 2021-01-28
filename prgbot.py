#!/usr/bin/env python3
import importlib
import random

import discord
import asyncio

from secrets import token

from discord.ext import commands

client = discord.Client()
prefix = '!'
playing = ['Random Games']


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    while True:
        await client.change_presence(activity=discord.Game(random.choice(playing)))
        await asyncio.sleep(60 * 15)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix):
        command = message.content.split()[0][1:]
        try:
            module = importlib.import_module('.' + command, 'command_handlers')
        except ModuleNotFoundError:
            print('Command "{}" not implemented'.format(command))
            return

        await module.run(client, message)


client.run(token)
