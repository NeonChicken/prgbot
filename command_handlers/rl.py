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

data = {}
data['gamblers'] = []

red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
green = [0, 37]
# black is not red & not green

odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
# 0 & 37 is neither

first = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
second = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
# third is not first, second or fourth
fourth = [0, 37]


def create_json_gambler():
    with io.open(os.path.join('./resources/battle', 'casino.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/casino.json') as file:
        first_file = json.load(file)
        first_file['gamblers'].append({'name': 'null'})
        with open('./resources/battle/casino.json', 'w') as f:
            json.dump(first_file, f, indent=4)


def roll():
    value = random.randint(0, 37)  # 36+1 for 0 & 00

    if value in red:
        color = 'red! :red_circle:'
    elif value in green:
        color = 'green! :green_circle:'
    else:
        color = 'black! :black_circle:'

    if value in odd:
        parity = 'odd!'
    elif value in even:
        parity = 'even!'
    else:
        parity = 'neither!'

    if value in range(1, 19):
        divide_seconds = '1-18'
    elif value in range(19, 37):
        divide_seconds = '19-36'
    else:
        divide_seconds = 'neither!'

    if value in range(1, 13):
        divide_thirds = '1-12'
    elif value in range(13, 25):
        divide_thirds = '13-24'
    elif value in range(25, 37):
        divide_thirds = '25-36'
    else:
        divide_thirds = 'neither'

    if value in first:
        row = '1st!'
    elif value in second:
        row = '2nd!'
    elif value in fourth:
        row = 'neither!'
    else:
        row = '3rd!'

    return [value, color, parity, divide_seconds, divide_thirds, row]


# Roulette
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "roulette!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**bet** (*credits*) (*place*) - bet an amount of credits some*place* on the table" \
                     "\n**credits** - view credits" \
                     "\n**bum** - use if you have **0** credits" \
                     "\n**leaderboard** - shows the top {} highest level players" \
                     "\n**table** - shows the table" \
                     "\n\nYou can (*place*) a bet on ***red**/**black** - **even**/**odd** - **1-18**/**19-36** - **1-12**/**13-24**/**25-36** - **1st**/**2nd**/**3rd** - or the numbers **0**, **00** & **1-36***" \
                       .format(leaderboard_display)
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
            if str(casino_file) == '' or str(casino_file) == '[]' or str(casino_file) == '{}':
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
                            await message.channel.send('*Created a casino save file for {}.*'.format(message.author))
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
                if len(message.content.split()) == 3:
                    await message.channel.send(help_msg())
                    return
                else:
                    for p in casino_file['gamblers']:
                        if str(message.author.id) == str(p['name']):
                            bet = int(message.content.split()[2].lower())
                            place = message.content.split()[3].lower()
                            if bet > p['credit']:
                                await message.channel.send(
                                    "{} you don't have **{}** :dollar:".format(message.author.mention, bet))
                            else:
                                p['credit'] = p['credit'] - bet
                                with open('./resources/battle/casino.json', 'w') as f:
                                    json.dump(casino_file, f, indent=4)

                                def roll_msg(int, multiplier):
                                    rolled = roll()
                                    if rolled[0] == 37:
                                        first_msg = "{} rolled a **00**, it's {}".format(message.author.mention,
                                                                                         rolled[int])
                                    else:
                                        first_msg = "{} rolled a **{}**, it's {}".format(message.author.mention,
                                                                                         rolled[0], rolled[int])
                                    if place in rolled[int]:
                                        first_msg = first_msg + "\nYou won **{}** :dollar:" \
                                            .format((bet * multiplier))
                                        p['credit'] = p['credit'] + (bet * multiplier)
                                        with open('./resources/battle/casino.json', 'w') as f:
                                            json.dump(casino_file, f, indent=4)
                                    else:
                                        first_msg = first_msg + "\nYou lost **{}** :dollar:".format(bet)
                                    return first_msg

                                if place == 'red':
                                    await message.channel.send(roll_msg(1, 2))
                                    return
                                elif place == 'black':
                                    await message.channel.send(roll_msg(1, 2))
                                    return
                                elif place == 'green':
                                    await message.channel.send(roll_msg(1, 2))
                                    return
                                elif place == 'odd':
                                    await message.channel.send(roll_msg(2, 2))
                                    return
                                elif place == 'even':
                                    await message.channel.send(roll_msg(2, 2))
                                    return
                                elif place == '1-18':
                                    await message.channel.send(roll_msg(3, 2))
                                    return
                                elif place == '19-36':
                                    await message.channel.send(roll_msg(3, 2))
                                    return
                                elif place == '1-12':
                                    await message.channel.send(roll_msg(4, 3))
                                    return
                                elif place == '13-24':
                                    await message.channel.send(roll_msg(4, 3))
                                    return
                                elif place == '25-36':
                                    await message.channel.send(roll_msg(4, 3))
                                    return
                                elif place == '1st':
                                    await message.channel.send(roll_msg(5, 3))
                                    return
                                elif place == '2nd':
                                    await message.channel.send(roll_msg(5, 3))
                                    return
                                elif place == '3rd':
                                    await message.channel.send(roll_msg(5, 3))
                                    return
                                elif place == '0':
                                    rolled = roll()
                                    if rolled[0] == 0:
                                        first_msg = "{} rolled a **0**!".format(message.author.mention)
                                        first_msg = first_msg + "\nYou won **{}** :dollar:".format((bet * 35))
                                        p['credit'] = p['credit'] + (bet * 35)
                                        with open('./resources/battle/casino.json', 'w') as f:
                                            json.dump(casino_file, f, indent=4)
                                    else:
                                        first_msg = "{} rolled a **{}**!".format(message.author.mention, rolled[0])
                                        first_msg = first_msg + "\nYou lost **{}** :dollar:".format(bet)
                                    await message.channel.send(first_msg)
                                    return
                                elif place == '00':
                                    rolled = roll()
                                    if rolled[0] == 37:
                                        first_msg = "{} rolled a **00**!".format(message.author.mention)
                                        first_msg = first_msg + "\nYou won **{}** :dollar:".format((bet * 35))
                                        p['credit'] = p['credit'] + (bet * 35)
                                        with open('./resources/battle/casino.json', 'w') as f:
                                            json.dump(casino_file, f, indent=4)
                                    else:
                                        first_msg = "{} rolled a **{}**!".format(message.author.mention, rolled[0])
                                        first_msg = first_msg + "\nYou lost **{}** :dollar:".format(bet)
                                    await message.channel.send(first_msg)
                                    return
                                elif place.isdigit():
                                    if int(place) in range(0, 37):
                                        rolled = roll()
                                        if rolled[0] == 37:
                                            first_msg = "{} rolled a **00**!".format(message.author.mention, rolled[0])
                                        else:
                                            first_msg = "{} rolled a **{}**!".format(message.author.mention, rolled[0],
                                                                                     rolled[0])
                                        if rolled[0] == int(place):
                                            first_msg = first_msg + "\nYou won **{}** :dollar:".format((bet * 35))
                                            p['credit'] = p['credit'] + (bet * 35)
                                            with open('./resources/battle/casino.json', 'w') as f:
                                                json.dump(casino_file, f, indent=4)
                                        else:
                                            first_msg = first_msg + "\nYou lost **{}** :dollar:".format(bet)
                                        await message.channel.send(first_msg)
                                        return
                                    else:
                                        await message.channel.send(
                                            "{}, that number isn't on the table!".format(message.author.mention))
                                else:
                                    await message.channel.send(help_msg())
                                    return

        # Check player credits
        elif 'credits' in '{}'.format(message.content.lower()):
            for p in casino_file['gamblers']:
                if str(message.author.id) == str(p['name']):
                    await message.channel.send(
                        '{} has **{}** :dollar:'.format(message.author.mention, p['credit']))

        elif 'reset' in '{}'.format(message.content.lower()):
            if 'Administrator' in str(message.author.roles):
                for p in casino_file['gamblers']:
                    del (casino_file['gamblers'])
                    with open('./resources/battle/casino.json', 'w') as f:
                        json.dump(casino_file, f, indent=4)
                    await message.channel.send("Save file has been reset!")
                    return
            else:
                await message.channel.send("{} is not an admin!".format(message.author.mention))
                return

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
                            "{} has bummed **{}** :dollar:\nYou're at **{}** bums!".format(message.author.mention,
                                                                                           start_credits, p['bum']))
                    else:
                        await message.channel.send("{}, you still have credits!".format(message.author.mention))
                        return


        # Table
        elif 'table' in '{}'.format(message.content.lower()):
            await message.channel.send("https://i.imgur.com/wXmJenM.png")
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

# todo roulette history
