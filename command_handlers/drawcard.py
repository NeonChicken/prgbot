import random

async def run(message):
    if len(message.content.split()) < 2:

        value_list = list(range(2,11)) + ['Jack', 'Queen', 'King', 'Ace']
        suit_list = ['Hearts', 'Diamonds', 'Spades', 'Clubs']

        response = "Your card is the {} of {}".format(value, suit)
        await message.channel.send(response)
        return
