import random

# Flip a coin and send the result.
async def run(client, message):
    if len(message.content.split()) < 2:
        print(message.author.name)