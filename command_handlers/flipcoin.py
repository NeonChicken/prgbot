import random

# Flip a coin and send the result.
async def run(message):
    with open('./resources/insults/insults-eng.txt') as insults:
        with open('./resources/insults/adjectives-eng.txt') as adjectives:
            if len(message.content.split()) < 2:
                response = "It's {}!".format(random.choice(['heads','tails']))
                await message.channel.send(response)
                return
            else:
                curse = random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults))
                response = "Don't put anything after the command, you {}".format(curse)
                await message.channel.send(response)
                return
