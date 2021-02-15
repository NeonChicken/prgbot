import random


# Flip a coin and send the result.
async def run(client, message):
    if len(message.content.split()) < 2:
        await message.channel.send("{}, **PRG** bot commands:\n*(Enter the commands below to find out more!)*\n\n"
                                   "***Commands:***\n"
                                   "**!teams** - Create teams\n\n"
                                   "**!vcteams** - Create teams from your voicechat channel\n\n"
                                   "***Random Games:***\n"
                                   "**!rp** - Roleplaying Game\n"
                                   "*Fight monsters, level up, earn gems, visit the shop and craft new swords!*\n"
                                   "**!fish** - Fishing Game\n"
                                   "*Collect every fish!*"
                                   "\n\n"
                                   "***Casino:***\n"
                                   "**!rl** - Roulette\n"
                                   "*Bet credits on a roulette table!*\n"
                                   "**!slot** - Slot machine\n"
                                   "*Bet credits into a slot machine!*\n"
                                   "**!bj** - Blackjack\n"
                                   "*Bet credits and play blackjack!*".format(message.author.mention))
