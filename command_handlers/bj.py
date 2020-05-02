import random
import asyncio
import math
import json
import os
import io

prefix = '!'
timeout_time = 30.0  # message.author response time in seconds
wait_time = 0  # time in between bot messages TO DO --> change to 3 or 2, used for testing
leaderboard_display = 3  # amount of players shown in leaderboard
start_credits = 100  # amount of credits players start with

suit = ["Hearts:hearts:", "Clubs:clubs:", "Spades:spades:", "Diamonds:diamonds:"]

card = [['Ace', 1], ['2', 2], ['3', 3], ['4', 4], ['5', 5], ['6', 6], ['7', 7], ['8', 8], ['9', 9], ['10', 10],
        ['Jack', 10],
        ['Queen', 10], ['King', 10]]

data = {}
data['gamblers'] = []


def create_json_gambler():
    with io.open(os.path.join('./resources/battle', 'casino.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/casino.json') as file:
        first_file = json.load(file)
        first_file['gamblers'].append({'name': 'null'})
        with open('./resources/battle/casino.json', 'w') as f:
            json.dump(first_file, f, indent=4)


def gen_card():
    new_card = []
    r_card = random.choice(card)
    r_suit = random.choice(suit)
    new_card.append(r_card[0])
    new_card.append(r_suit)
    value = '{}'.format(r_card[1])
    return [new_card[0], new_card[1], value]


# Blackjack
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "blackjack!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**bet** (*credits*) - bet an amount of credits" \
                     "\n**credits** - view credits" \
                     "\n**bum** - use if you have **0** credits" \
                     "\n**leaderboard** - shows the top {} highest level players.".format(leaderboard_display)
        return response

    # loading save files
    if not os.path.isfile('./resources/battle/casino.json'):
        # if file not found, make casino.json with create_json_player function
        create_json_gambler()
        await message.channel.send('*casino.json has been created. Please try again.*')
        return
    else:
        with open('./resources/battle/casino.json') as file:
            casino_file = json.load(file)
            if str(casino_file) == '' or str(casino_file) == '[]':
                create_json_gambler()
                await message.channel.send('*casino.json was empty. Please try again.*')
                return
            else:
                count = 1
                do_not_create_save = 0
                for p in casino_file['gamblers']:
                    if str(message.author.id) == str(p['name']):
                        do_not_create_save = 1
                        print("Found {}".format(message.author) + " in players!")
                    elif str(message.author.id) is not str(p['name']) and do_not_create_save is not 1:
                        if count is int(len(casino_file['gamblers'])):
                            casino_file['gamblers'].append({
                                'name': '{}'.format(message.author.id),
                                'name_at_save': '{}'.format(message.author.name),
                                'credit': start_credits,
                                'bum': 0
                            })
                            with open('./resources/battle/casino.json', 'w') as f:
                                json.dump(casino_file, f, indent=4)
                            await message.channel.send('*Created a casino save for {}.*'.format(message.author))
                    count = count + 1

    # game logic
    if len(message.content.split()) < 2:
        await message.channel.send(help_msg())
        return

    if len(message.content.split()) >= 2:
        if 'bet' in '{}'.format(message.content.lower()):
            if len(message.content.split()) == 2:
                await message.channel.send(help_msg())
                return
            else:
                for p in casino_file['gamblers']:
                    if str(message.author.id) == str(p['name']):
                        bet = int(message.content.split()[2].lower())
                        if bet > p['credit']:
                            await message.channel.send(
                                "{} you don't have **{}** :dollar:".format(message.author.mention, bet))
                        else:
                            first_card = gen_card()
                            second_card = gen_card()
                            total_value = int(first_card[2]) + int(second_card[2])
                            first_card_D = gen_card()
                            second_card_D = gen_card()
                            total_value_D = int(first_card_D[2]) + int(second_card_D[2])
                            await message.channel.send(
                                "{} bet **{}** :dollar:\nYour cards:\n{}\n{}\nTotal value: **{}**".format(
                                    message.author.mention,
                                    bet,
                                    '**{}** of ***{}***'.format(
                                        first_card[0],
                                        first_card[1]),
                                    '**{}** of ***{}***'.format(
                                        second_card[0],
                                        second_card[1]),
                                    total_value))
                            p['credit'] = p['credit'] - bet
                            print(p['credit'])
                            with open('./resources/battle/casino.json', 'w') as f:
                                json.dump(casino_file, f, indent=4)
                            await asyncio.sleep(wait_time)
                            await message.channel.send("{}\n*Dealer* has a {}".format(message.author.mention,
                                                                                      '**{}** of ***{}***\n*Dealer* total: **{}**'.format(
                                                                                          first_card_D[0],
                                                                                          first_card_D[1],
                                                                                          first_card_D[
                                                                                              2])))
                            await asyncio.sleep(wait_time)
                            while total_value <= 21:
                                await message.channel.send(
                                    "{}, you can **hit** or **stand**".format(message.author.mention))

                                def check(msg):
                                    return msg.author == message.author

                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send(
                                        "{} didn't respond in time!:zzz:".format(message.author.mention))
                                    return
                                else:
                                    if msg.content.lower() == 'hit' or msg.content.lower() == prefix + 'hit':
                                        extra_card = gen_card()
                                        total_value = total_value + int(extra_card[2])
                                        await message.channel.send(
                                            "{} drew the {}\nTotal value: **{}**".format(message.author.mention,
                                                                                         '**{}** of ***{}***'.format(
                                                                                             extra_card[0],
                                                                                             extra_card[1]),
                                                                                         total_value))
                                        await asyncio.sleep(wait_time)
                                    elif msg.content.lower() == 'stand' or msg.content.lower() == prefix + 'stand':
                                        await message.channel.send("{} decides to stand".format(message.author.mention))
                                        await asyncio.sleep(wait_time)
                                        await message.channel.send(
                                            "\n\n{} \n*Dealer* has:\n{}\n{}\nTotal: **{}**".format(
                                                message.author.mention,
                                                '**{}** of ***{}***'.format(
                                                    first_card_D[0],
                                                    first_card_D[1]),
                                                '**{}** of ***{}***'.format(
                                                    second_card_D[0],
                                                    second_card_D[1]),
                                                total_value_D))
                                        await asyncio.sleep(wait_time)
                                        while total_value_D:
                                            if total_value_D > 21:
                                                await message.channel.send(
                                                    "*Dealer* busted!\n:trophy:{} won!:trophy:\nEarned **{}** :dollar:".format(
                                                        message.author.mention, (bet * 2)))
                                                p['credit'] = p['credit'] + (bet * 2)
                                                with open('./resources/battle/casino.json', 'w') as f:
                                                    json.dump(casino_file, f, indent=4)
                                                return
                                            elif total_value_D < 17:
                                                extra_card_D = gen_card()
                                                total_value_D = total_value_D + int(extra_card_D[2])
                                                await message.channel.send(
                                                    "{}\n*Dealer* drew the {}\n*Dealer* total: **{}**".format(
                                                        message.author.mention,
                                                        '**{}** of ***{}***'.format(
                                                            extra_card_D[0],
                                                            extra_card_D[1]),
                                                        total_value_D))
                                                await asyncio.sleep(wait_time)
                                            else:
                                                await message.channel.send(
                                                    "{}\n*Dealer* stands at **{}**".format(message.author.mention,
                                                                                           total_value_D))
                                                await asyncio.sleep(wait_time)
                                                if total_value_D < total_value:
                                                    await message.channel.send(
                                                        ":trophy:{} won!:trophy:\nEarned **{}** :dollar:".format(
                                                            message.author.mention, (bet * 2)))
                                                    p['credit'] = p['credit'] + (bet * 2)
                                                    with open('./resources/battle/casino.json', 'w') as f:
                                                        json.dump(casino_file, f, indent=4)
                                                    return
                                                elif total_value_D == total_value:
                                                    await message.channel.send(
                                                        "{}\nIt's a draw!:balloon:\nReclaimed **{}** :dollar:".format(
                                                            message.author.mention, bet))
                                                    p['credit'] = p['credit'] + bet
                                                    with open('./resources/battle/casino.json', 'w') as f:
                                                        json.dump(casino_file, f, indent=4)
                                                    return
                                                else:
                                                    await message.channel.send(
                                                        ":skull:{} lost!:skull:\nLost **{}** :dollar:".format(
                                                            message.author.mention, bet))
                                                    return
                                    else:
                                        await message.channel.send(
                                            "{} did not hit, stand or split!".format(message.author.mention))
                                        return
                                    '''elif msg.content.lower() == 'split' or msg.content.lower() == prefix + 'split':
                                        if int(first_card[2]) == int(second_card[2]):
                                            await message.channel.send(
                                                "{} split their **{}'s**!".format(message.author.mention, math.floor(total_value / 2)))
                    
                                            return
                                        else:
                                            await message.channel.send(
                                                "{}, you can't split a **{}** and a **{}**!\nYou lost the hand...".format(
                                                    message.author.mention,
                                                    first_card[2],
                                                    second_card[2]))
                                            return'''

                            else:
                                await message.channel.send(
                                    "{} busted! Lost **{}** :dollar:!".format(message.author.mention, bet))
                                return

        # Check player credits
        elif 'credits' in '{}'.format(message.content.lower()):
            for p in casino_file['gamblers']:
                if str(message.author.id) == str(p['name']):
                    await message.channel.send(
                        '{} has **{}** :dollar:'.format(message.author.mention, p['credit']))

        # Bum credits if you're out
        elif 'bum' in '{}'.format(message.content.lower()):
            for p in casino_file['gamblers']:
                if str(message.author.id) == str(p['name']):
                    if p['credit'] <= 0:
                        p['credit'] = p['credit'] + start_credits
                        p['bum'] = p['bum'] + 1
                        with open('./resources/battle/casino.json', 'w') as f:
                            json.dump(casino_file, f, indent=4)
                        await message.channel.send(
                            "{} has bummed **{}** :dollar:\nYou're at {} bums!".format(message.author.mention,
                                                                                       start_credits, p['bum']))
                    else:
                        await message.channel.send("{}, you still have credits!".format(message.author.mention))
                        return


        # Leaderboard
        elif 'leaderboard' in '{}'.format(message.content.lower()):
            for p in casino_file['gamblers']:
                if str(p['name']) == str("null"):
                    pass
                else:
                    for i in range(leaderboard_display):
                        # - 1 because of the first null object in the json
                        if i < (len(casino_file['gamblers']) - 1):
                            leader_name = []
                            leader_credit = []
                            leader_bum = []
                            for p in casino_file['gamblers']:
                                if str(p['name']) == str("null"):
                                    pass
                                else:
                                    leader_name.append(p['name'])
                                    leader_credit.append(p['credit'])
                                    leader_bum.append(p['bum'])
                    leader_name_sorted = [x for _, x in sorted(zip(leader_credit, leader_name), reverse=True)]
                    leader_credit_sorted = [x for _, x in sorted(zip(leader_credit, leader_credit), reverse=True)]
                    leader_bum_sorted = [x for _, x in sorted(zip(leader_credit, leader_bum), reverse=True)]
                    leader_msg_final = []
                    leader_count = len(leader_credit)
                    for l in range(leader_count):
                        if l < leaderboard_display:
                            leader_msg_final.append("**{}.** ".format(l + 1))
                            leader_msg_final.append("<@{}> - ".format(leader_name_sorted[l]))
                            leader_msg_final.append("**{}** :dollar:".format(leader_credit_sorted[l]))
                            leader_msg_final.append(" *[**{}** bums!]*\n".format(leader_bum_sorted[l]))
                    leader_msg = "".join(map(str, leader_msg_final))
                    await message.channel.send("{}".format(leader_msg))
                    return

        else:
            await message.channel.send(help_msg())
            return

    else:
        await message.channel.send(help_msg())
        return
