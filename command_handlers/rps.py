import random
import asyncio


prefix = '!'

wait_time = 0.5
timeout_time = 20

# RPS
async def run(client, message):

    if len(message.content.split()) < 2:
        print('help')

    if len(message.content.split()) >= 2:
        def gen_rps():
            rps = ['rock', 'paper', 'scissors']
            r_rps = random.choice(rps)
            return r_rps

        temp_rps = gen_rps()
        temp_msg = "{} drew **{}**\nI drew **{}**".format(message.author.mention, message.content.split()[1], temp_rps)
        if 'scissors' in '{}'.format(message.content.lower()):
            if temp_rps == 'scissors':
                temp_msg = temp_msg + "\nIt's a draw!:balloon:"
            elif temp_rps == 'paper':
                temp_msg = temp_msg + "\nYou won!:trophy:"
            else:
                temp_msg = temp_msg + "\nYou lose!:skull:"
            await message.channel.send(temp_msg)
        elif 'rock' in '{}'.format(message.content.lower()):
            if temp_rps == 'scissors':
                temp_msg = temp_msg + "\nYou won!:trophy:"
            elif temp_rps == 'paper':
                temp_msg = temp_msg + "\nYou lose!:skull:"
            else:
                temp_msg = temp_msg + "\nIt's a draw!:balloon:"
            await message.channel.send(temp_msg)
        elif 'paper' in '{}'.format(message.content.lower()):
            if temp_rps == 'scissors':
                temp_msg = temp_msg + "\nYou lose!:skull:"
            elif temp_rps == 'paper':
                temp_msg = temp_msg + "\nIt's a draw!:balloon:"
            else:
                temp_msg = temp_msg + "\nYou won!:trophy:"
            await message.channel.send(temp_msg)
        else:
            await message.channel.send("{}, enter **rock**/**paper**/**scissors**".format(message.author.mention))
