import random
from collections import namedtuple

async def run(message):
    if len(message.content.split()) < 2:

        card = namedtuple('Card', ['value', 'suit'])
        suits = ['Spades', 'Hearts', 'Clubs', 'Diamonds']
        cards = [card(value, suit) for value in range(2, 14) for suit in suits]
        random.shuffle(cards)

        if cards[0].value <= 10:
            newvalue = cards[0].value
        elif cards[0].value == 11:
            newvalue = "Jack"
        elif cards[0].value == 12:
            newvalue = "Queen"
        elif cards[0].value == 13:
            newvalue = "King"
        elif cards[0].value == 14:
            newvalue = "Ace"
        else:
            response = "Something went wrong!"
            await message.channel.send(response)
            return
        newsuit = cards[0].suit

        response = "Your card is the {} of {}".format(newvalue, newsuit)
        await message.channel.send(response)
        return
