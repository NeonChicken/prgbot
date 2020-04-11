import random

# Take any number of arguments and return one of them randomly.
async def run(message):
    with open('./resources/insults/insults.txt') as insults:
        with open('./resources/insults/adjectives.txt') as adjectives:
            if len(message.content.split()) < 2:
                coinint = random.randint(1, 2)
                if coinint == 1:
                    coin = "heads."
                elif coinint == 2:
                    coin = "tails."
                response = "It's {}".format(coin)
                await message.channel.send(response)
                return
            if len(message.content.split()) >= 2:
                curse = random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults))
                response = "Don't put anything after the command, you {}".format(curse)
                await message.channel.send(response)
                return