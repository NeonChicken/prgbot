import random

async def run(client, message):
    if len(message.content.split()) < 2:

        value_list = list(range(2,11)) + ['jack', 'queen', 'king', 'ace']
        suit_list = ['hearts', 'diamonds', 'spades', 'clubs']

        value = random.choice(value_list)
        suit = random.choice(suit_list)

        response = "Your card is the {} of {}".format(value, suit)
        await message.channel.send(response)
        return
