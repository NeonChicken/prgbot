import random

async def run(message):
    with open('./resources/insults/insults-nl.txt') as insults:
        with open('./resources/insults/adjectives-nl.txt') as adjectives:
            response = random.choice(list(adjectives)).capitalize().rstrip() + ' ' + random.choice(list(insults))
            await message.channel.send(response)
