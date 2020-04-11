import random

# Take any number of arguments and return one of them randomly.
async def run(message):
    with open('./resources/insults/insults.txt') as insults:
        with open('./resources/insults/adjectives.txt') as adjectives:
            if len(message.content.split()) < 2:
                six = random.randint(1, 6)
                response = "Rolling six-sided die: {}".format(six)
                await message.channel.send(response)
                return
            if len(message.content.split()) == 2:
                sides = message.content.split()[1]
                try:
                    fsides = round(float(sides))
                    if fsides > 0:
                        ranside = random.randint(1, int(fsides))
                        response = "Rolling {}-sided die: {}".format(fsides, ranside)
                        await message.channel.send(response)
                        return
                    elif fsides == 0:
                        curse = random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults))
                        response = "The die can't have 0 sides, you {}".format(curse)
                        await message.channel.send(response)
                        return
                    elif fsides < 0:
                        curse = random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults))
                        response = "You can't roll a die with negative sides, you {}".format(curse)
                        await message.channel.send(response)
                        return
                    else:
                        response = "Something went wrong!"
                        await message.channel.send(response)
                        return
                except (ValueError, IndexError):
                    curse = random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults))
                    response = "That's not an integer or float, you {}".format(curse)
                    await message.channel.send(response)
                    return
            if len(message.content.split()) > 2:
                response = "Please give me an integer after ?roll."
                await message.channel.send(response)
                return
