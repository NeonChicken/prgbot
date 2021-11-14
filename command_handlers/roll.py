import random
from .insultme import generate_insult

#Roll an n-sided die
async def run(message):
    if len(message.content.split()) < 2:
        sides = 6
    elif len(message.content.split()) == 2:
        try:
            str_sides = message.content.split()[1]
            if int(str_sides) != float(str_sides):
                raise ValueError
            else:
                sides = int(str_sides)
        except ValueError:
            response = "That's not an integer, you {}!".format(generate_insult())
            await message.channel.send(response)
            return
    
    if len(message.content.split()) > 2:
        response = "Please give me an integer after ?roll."
        await message.channel.send(response)
        return
    
    if sides > 0:
        ranside = random.randint(1, int(sides))
        response = "Rolling {}-sided die: {}".format(sides, ranside)
    elif sides == 0:
        response = "The die can't have 0 sides, you {}!".format(generate_insult())
    else:
        response = "You can't roll a die with negative sides, you {}!".format(generate_insult())
    await message.channel.send(response)

