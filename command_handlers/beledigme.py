import random

async def run(client, message):
    with open('./resources/insults/insults-nl.txt') as insults:
        with open('./resources/insults/adjectives-nl.txt') as adjectives:
            response = random.choice(list(adjectives)).capitalize().rstrip() + ' ' + random.choice(list(insults)).rstrip()
            await message.channel.send(response)
