import random

async def run(client, message):
    response = generate_insult().capitalize()
    await message.channel.send(response)

def generate_insult():
    with open('./resources/insults/insults-eng.txt') as insults:
        with open('./resources/insults/adjectives-eng.txt') as adjectives:
            return random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults)).rstrip()
