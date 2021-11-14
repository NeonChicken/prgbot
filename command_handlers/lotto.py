import random

# Take any number of arguments and return one of them randomly.
async def run(client, message):
    if len(message.content.split()) < 2:
        response = "I can't choose anything if you don't give me any options!"
    else:
        options = message.content.split()[1:]
        response = random.choice(options)
    await message.channel.send(response)