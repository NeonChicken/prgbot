import random
from .insultme import generate_insult

# Flip a coin and send the result.
async def run(message):
    if len(message.content.split()) < 2:
        response = "It's {}!".format(random.choice(['heads','tails']))
        await message.channel.send(response)
        return
    else:
        response = "Don't put anything after the command, you {}!".format(generate_insult())
        await message.channel.send(response)
        return
