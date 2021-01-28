import random
import asyncio
import json
import os
import io

prefix = '!'

wait_time = 0.2
timeout_time = 20


class fish:
    def __init__(self, name, min_weight, max_weight, odds):
        self.name = name
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.odds = odds


fish_list = dict(
    snapper=fish("Snapper", 0, 0, .1),
    mullet=fish("Mullet", 0, 0, .1),
    trout=fish("Trout", 0, 0, .1),
    bass=fish("Bass", 0, 0, .1),
    sardine=fish("Sardine", 0, 0, .1),
    tuna=fish("Tuna", 0, 0, .05),
    salmon=fish("Salmon", 0, 0, .05),
    catfish=fish("Catfish", 0, 0, .02),
    legend=fish("_Seaman_", 0, 0, .01),
)
fishes = []
fishes_weight = []
for k in fish_list:
    fishes.append(fish_list[k])
    fishes_weight.append(fish_list[k].odds)
fish_names = []
for i in fishes:
    name_check = [i.name, 0]  # 0 is for uncaught fish
    fish_names.append(name_check)

data = {}
data['fishers'] = []


def create_json_fisher():
    with io.open(os.path.join('./resources/battle', 'fish.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/fish.json') as file:
        first_file = json.load(file)
        first_file['fishers'].append({'name': 'null'})
        with open('./resources/battle/fish.json', 'w') as f:
            json.dump(first_file, f, indent=4)


# Flip a coin and send the result.
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "fishing game!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**cast** - casts your rod to start fishing" \
                     "\n**collection** - shows your fish collection"
        return response

    # loading save files
    if not os.path.isfile('./resources/battle/fish.json'):
        # if file not found, make fish.json with create_json_player function
        create_json_fisher()
        await message.channel.send('*fish.json has been created. Please try again.*')
        return
    else:
        with open('./resources/battle/fish.json') as file:
            fish_file = json.load(file)
            if str(fish_file) == '' or str(fish_file) == '[]' or str(fish_file) == '{}':
                create_json_fisher()
                await message.channel.send('*fish.json was empty. Please try again.*')
                return
            else:
                count = 1
                do_not_create_save = 0
                for p in fish_file['fishers']:
                    if str(message.author.id) == str(p['name']):
                        do_not_create_save = 1
                        print("Found {}".format(message.author) + " in players!")
                    elif str(message.author.id) is not str(p['name']) and do_not_create_save is not 1:
                        if count is int(len(fish_file['fishers'])):
                            fish_file['fishers'].append({
                                'name': '{}'.format(message.author.id),
                                'name_at_save': '{}'.format(message.author.name),
                                'collection': fish_names
                            })
                            with open('./resources/battle/fish.json', 'w') as f:
                                json.dump(fish_file, f, indent=4)
                            await message.channel.send('*Created a fish save file for {}.*'.format(message.author))
                    count = count + 1

    if len(message.content.split()) < 2:
        await message.channel.send(help_msg())
        return

    if len(message.content.split()) >= 2:
        if 'cast' in '{}'.format(message.content.lower()):
            msg = await message.channel.send("Fishing.")
            await asyncio.sleep(wait_time)
            await msg.edit(content="Fishing..")
            await asyncio.sleep(wait_time)
            await msg.edit(content="Fishing...")
            await asyncio.sleep(wait_time)
            r_fish = random.choices(fishes, fishes_weight)
            message_content = "{} caught a {}!".format(message.author.mention, r_fish[0].name)
            await msg.edit(content=message_content)
            for p in fish_file['fishers']:
                if str(message.author.id) == str(p['name']):
                    for i in fish_names:
                        if i[0].lower() in r_fish[0].name.lower():
                            for c in p['collection']:
                                if c[0].lower() == i[0].lower():
                                    if c[1] == 0:
                                        await asyncio.sleep(wait_time)
                                        c[1] = 1
                                        with open('./resources/battle/fish.json', 'w') as f:
                                            json.dump(fish_file, f, indent=4)
                                        message_content = message_content + "\nAdded {} to your collection! :fish:".format(
                                            c[0])
                                        collection = []
                                        collection_all = []
                                        for i in fish_names:
                                            collection_all.append(i[0])
                                            collection_all.sort()
                                        for i in fish_names:
                                            for c in p['collection']:
                                                if c[0].lower() == i[0].lower():
                                                    if c[1] == 1:
                                                        collection.append(c[0])
                                            await asyncio.sleep(wait_time)
                                        if len(collection) == len(collection_all):
                                            message_content = message_content + "\n:dart:*Congratulations! You've caught every fish!*:dart:"

                                        await msg.edit(content=message_content)
                                        return
                                    else:
                                        await asyncio.sleep(wait_time)
                                        message_content = message_content + "\nBut you've already caught one before!" \
                                                                            "\nThrowing it back in the water...".format(
                                            c[0])
                                        await msg.edit(content=message_content)
                                        return

        elif 'collection' in '{}'.format(message.content.lower()):
            for p in fish_file['fishers']:
                if str(message.author.id) == str(p['name']):
                    collection = []
                    collection_all = []
                    for i in fish_names:
                        collection_all.append(i[0])
                        collection_all.sort()
                    for i in fish_names:
                        for c in p['collection']:
                            if c[0].lower() == i[0].lower():
                                if c[1] == 1:
                                    collection.append(c[0])
                    col_msg = " ".join(map(str, collection_all))
                    col_msg_split = col_msg.split()
                    for o in range(len(collection)):
                        for s in col_msg_split:
                            if collection[o] in s:
                                new = '**' + s + '** :white_check_mark:'
                                col_msg_split.remove(s)
                                col_msg_split.append(new)
                                col_msg_split.sort()
                    col_msg = "\n".join(map(str, col_msg_split))
                    # if all fish caught
                    if len(collection) == len(collection_all):
                        col_msg = col_msg + "\n:dart:*Congratulations! You've caught every fish!*:dart:"
                    await message.channel.send(col_msg)
                    return

        elif 'test' in '{}'.format(message.content.lower()):
            print('test')

        else:
            await message.channel.send(help_msg())
            return

#  sell fish for coins
#  buy bait
#  fishing rods (can break)
#  fish counter in json, apart from collection check (with fish limit)

#  rummage for rusty cans, anchors, spoons, plastics 5 times a day /
#  (log in json) to sell, so you can buy fishing rod at the start
