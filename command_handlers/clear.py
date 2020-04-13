from .insultme import generate_insult
import discord
#
async def run(message):
    if ('Administrator' in str(message.author.roles)):
        if len(message.content.split()) < 2:
            response = "How many messages do you want to clear?"
            await message.channel.send(response)
        elif len(message.content.split()) == 2:
            amount = message.content.split()[1]
            clear_amount = int(amount)
            await message.channel.purge(limit=(clear_amount + 1))
            # clear_amount + 1 to delete the command itself as well
            response = "{} messages have been cleared {}!".format(clear_amount, message.author.mention)
            await message.channel.send(response)
        else:
            response = "Don't put anything after the command, you {}".format(generate_insult())
            await message.channel.send(response)
    else:
        response = "You don't have access to this command"
        await message.channel.send(response)
