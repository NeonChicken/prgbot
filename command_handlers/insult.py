from .insultme import generate_insult

async def run(message):
    if len(message.content.split()) < 2:
        response = "Who do you want to insult? You can @ them or just type their regular name."
        await message.channel.send(response)
    elif len(message.content.split()) == 2:
        mention = message.content.split()[1]
        response = "{}, you {}!".format(mention, generate_insult())
        await message.channel.send(response)
    else:
        response = "Don't put anything after the command, you {}!".format(generate_insult())
        await message.channel.send(response)
