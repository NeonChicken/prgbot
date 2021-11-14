import random

# Take a list of arguments and respond with a random string from the list
async def run(client, message):
    await message.channel.send(random.choice(message.content.split()[1:]))
