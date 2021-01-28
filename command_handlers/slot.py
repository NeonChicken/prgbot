import random
import asyncio
import math
import json
import os
import io

prefix = '!'

timeout_time = 30.0  # message.author response time in seconds
wait_time = 0  # time in between bot messages TO DO --> change to 3 or 2, used for testing
jackpot_multiplier = 5  # multiplier value when three of the same fruit has been rolled
leaderboard_display = 3  # amount of players shown in leaderboard
start_credits = 100  # amount of credits players start with


class fruit:
    def __init__(self, name, value, odds):
        self.name = name
        self.value = value
        self.odds = odds


fruit_list = dict(
    orange=fruit(":tangerine:", 1, .30),
    grape=fruit(":grapes:", 2, .23),
    peach=fruit(":peach:", 2, .23),
    melon=fruit(":watermelon:", 3, .14),
    cherry=fruit(":cherries:", 5, .09),
    pepper=fruit(":hot_pepper:", 10, 0.01)
)
fruits = []
fruits_weight = []
for k in fruit_list:
    fruits.append(fruit_list[k])
    fruits_weight.append(fruit_list[k].odds)

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


# Flip a coin and send the result.
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "slot machine!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**bet** (*credits*) - bet an amount of credits" \
                     "\n**credits** - view credits" \
                     "\n**bum** - use if you have **0** credits" \
                     "\n**leaderboard** - shows the top {} highest level players" \
                     "\n**values** - shows each fruit value"
        return response

    def gen_fruits():
        r_fruit1 = random.choices(fruits, fruits_weight)
        r_fruit2 = random.choices(fruits, fruits_weight)
        r_fruit3 = random.choices(fruits, fruits_weight)
        return [r_fruit1[0], r_fruit2[0], r_fruit3[0]]

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
                            await message.channel.send(
                                '*Created a casino save file for {}.*'.format(message.author))
                    count = count + 1

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
                            p['credit'] = p['credit'] - bet
                            with open('./resources/battle/casino.json', 'w') as f:
                                json.dump(casino_file, f, indent=4)

                            def new_fruit(final):
                                temp_fruits = gen_fruits()
                                temp_msg = "{}".format(message.author.mention)
                                if final == 1:
                                    return [temp_msg + " :white_check_mark:\n" + "".join(
                                        "{} {} {}".format(temp_fruits[0].name, temp_fruits[1].name,
                                                          temp_fruits[2].name)),
                                            temp_fruits[0].name]
                                else:
                                    return temp_msg + "\n" + "".join(
                                        "{} {} {}".format(temp_fruits[0].name, temp_fruits[1].name,
                                                          temp_fruits[2].name))

                            msg = await message.channel.send(new_fruit(0))
                            await asyncio.sleep(wait_time)
                            await msg.edit(content=new_fruit(0))
                            await asyncio.sleep(wait_time)
                            await msg.edit(content=new_fruit(0))
                            await asyncio.sleep(wait_time)
                            await msg.edit(content=new_fruit(0))
                            await asyncio.sleep(wait_time)
                            await msg.edit(content=new_fruit(0))
                            await asyncio.sleep(wait_time)
                            await msg.edit(content=new_fruit(1)[0])
                            fruit_msg = []
                            for msg_content in msg.content.split():
                                for fruit_content in fruits:
                                    if msg_content == fruit_content.name:
                                        fruit_msg.append(msg_content)
                            final_message = "{} has rolled:".format(message.author.mention)

                            total = 0

                            # Pepper check
                            for fruit_content_pepper in fruits:
                                if ":hot_pepper:" == fruit_content_pepper.name:
                                    if ":hot_pepper:" in fruit_msg:
                                        for f in fruit_msg:
                                            if f == ":hot_pepper:":
                                                total = total + bet * math.floor(fruit_content_pepper.value / 2)
                                                final_message = final_message + "\nA **pepper** :hot_pepper:"
                                        break

                            # Rows calculation
                            for fruit_content in fruits:
                                if fruit_msg[0] == fruit_msg[1]:
                                    # rolled two of the same
                                    if fruit_msg[1] == fruit_msg[2]:
                                        # rolled three of the same
                                        if fruit_msg[0] == fruit_content.name:
                                            total = math.floor(total + (bet * fruit_content.value * jackpot_multiplier))
                                            final_message = final_message + "\n:dart:**JACKPOT**:dart:\nWon **{}** :dollar:".format(
                                                total)
                                    else:
                                        if fruit_msg[0] == fruit_content.name:
                                            total = math.floor(total + bet * fruit_content.value)
                                            final_message = final_message + "\n:trophy:*Two in a row!*:trophy:\nWon **{}** :dollar:".format(
                                                total)
                                elif fruit_msg[1] == fruit_msg[2]:
                                    # rolled two of the same in different position
                                    if fruit_msg[1] == fruit_content.name:
                                        total = math.floor(total + (bet * fruit_content.value))
                                        final_message = final_message + "\n:trophy:*Two in a row!*:trophy:\nWon **{}** :dollar:".format(
                                            total)
                                elif fruit_msg[0] is not fruit_msg[1] and fruit_msg[1] is not fruit_msg[2]:
                                    if total == 0:
                                        final_message = final_message + "\n*Nothing!*"
                                        await message.channel.send(final_message)
                                        return
                                    else:
                                        final_message = final_message + "\n*No rows!*\nWon **{}** :dollar:".format(
                                            total)
                                        p['credit'] = p['credit'] + total
                                        with open('./resources/battle/casino.json', 'w') as f:
                                            json.dump(casino_file, f, indent=4)
                                        await message.channel.send(final_message)
                                        return
                            p['credit'] = p['credit'] + total
                            with open('./resources/battle/casino.json', 'w') as f:
                                json.dump(casino_file, f, indent=4)
                            await message.channel.send(final_message)
                            return

        elif 'values' in '{}'.format(message.content.lower()):
            list_values = []
            list_names = []
            for fruit_content in fruits:
                list_names.append(fruit_content.name)
                list_values.append(fruit_content.value)
            sorted_values = [x for _, x in sorted(zip(list_values, list_values))]
            sorted_names = [x for _, x in sorted(zip(list_values, list_names))]
            sorted_list_new = []
            sorted_count = len(sorted_values)
            for l in range(sorted_count):
                sorted_list_new.append([sorted_names[l], sorted_values[l]])
            value_msg = ""
            for s in sorted_list_new:
                value_msg = value_msg + "{}: **{}**\n".format(s[0], s[1])
            value_msg = value_msg + "\n*Jackpot multiplier:* **{}**".format(jackpot_multiplier)
            await message.channel.send(value_msg)

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

        elif 'test' in '{}'.format(message.content.lower()):
            print('')

        else:
            await message.channel.send(help_msg())
            return