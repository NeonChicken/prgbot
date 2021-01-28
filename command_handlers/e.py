import random
import asyncio
import discord
from PIL import Image, ImageFont, ImageDraw, ImageOps
from io import BytesIO
import json
import os
import io
import math
import datetime

prefix = '!'

# IMAGE MANIPULATION & PROCESSING!

wait_time = 0.5
timeout_time = 40
min_seed = 0
max_seed = 10000000

# courier new is monospace (even spaced characters)
font = ImageFont.truetype("courbd.ttf", 24)
shadow_font = ImageFont.truetype("courbd.ttf", 24)
# List of emojis in this font > https://en.wikipedia.org/w/index.php?title=Emoji&oldid=557685103
emoji_font = ImageFont.truetype("resources/misc/OpenSansEmoji.ttf", 20)
# amount of pixels to offset shadow in text
shadow_offset = 2

inventory_limit = 8

data = {}
data['players'] = []
data['shop'] = []

# pixels per items, needs to be evenly distributed among img_bg [empty png with dimensions]
px_per_item = 100
# pixels offset, e.g. if smaller pictures are centered in a block
px_item_offset = 5

# Rarity text colors v
col_bad = (255, 50, 50)
col_ok = (255, 255, 50)
col_rare = (50, 255, 50)
col_ultra = (200, 0, 200)
col_unknown = (255, 196, 66)


def create_json_player():
    with io.open(os.path.join('./resources/battle', 'rogue.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/rogue.json') as log:
        first_log = json.load(log)
        first_log['players'].append({'name': 'null'})
        first_log['shop'].append({'name': 'null'})
        with open('./resources/battle/rogue.json', 'w') as f:
            json.dump(first_log, f, indent=4)

# Rarity multiplier. Can be / 2 or ** -2 or ** -3
# to make rarity values 1-4 inverted, and used as a weight
def rarity_multiplier(a):
    return a ** -3

# Generating starter items with rarity of 1
def gen_starter(dict):
    # Add all rarity 1 items to list
    temp_starter = []

    for starters in dict:
        # Check for rarity of 1 in all items
        if dict[starters][2] == 1:
            temp_starter.append(dict[starters])

    return random.choices(temp_starter)

# Generating randomized loot
def gen_loot(dict):
    items_gend = []
    # Get weights based on rarity
    # using Rarity Multiplier function to base weight on rarity
    weigths = []
    for weight_ite in range(len(dict)):
        weigths.append(rarity_multiplier(dict[list(dict.keys())[weight_ite]][2]))
    # Get random item based on rarity
    key_item_r = random.choices(list(dict), weights=weigths, k=1)
    # Grab random key from dict and take its first array value (0. file-loc 1. name 2.RANK-pool)
    items_gend.append(dict[[key_item_r[0]][0]])
    return items_gend

async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(commandname) + "rogue-like!" \
                   "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**loot/sp/ins/gen** - Check Inventory"
        return response

    # loading save files
    if not os.path.isfile('./resources/battle/rogue.json'):
        # if file not found, make rogue.json with create_json_player function
        create_json_player()
        await message.channel.send('Rogue data has been created. Please try again.')
        return
    else:
        with open('./resources/battle/rogue.json') as log:
            contents = json.load(log)
            if str(contents) == '' or str(contents) == '[]':
                create_json_player()
                await message.channel.send('Rogue data did not exist. Please try again.')
                return
            else:
                count = 1
                do_not_create_save = 0
                for s in contents['shop']:
                    if str(s) == "{'name': 'null'}":
                        contents['shop'] = [({
                            'seed': 0,
                            'last_gen': '{}'.format(datetime.date.today()),
                            'money': 1000,
                        })]
                        with open('./resources/battle/rogue.json', 'w') as f:
                            json.dump(contents, f, indent=4)
                for p in contents['players']:
                    if str(message.author.id) == str(p['name']):
                        do_not_create_save = 1
                        print("Found {}".format(message.author) + " in players!")
                    elif str(message.author.id) is not str(p['name']) and do_not_create_save is not 1:
                        if count is int(len(contents['players'])):
                            contents['players'].append({
                                'name': '{}'.format(message.author.id),
                                'name_at_save': '{}'.format(message.author.name),
                                'hp': 10,
                                'max_hp': 10,
                                'lvl': 1,
                                'xp': 0,
                                'gold': 0,
                                "equip": {
                                    "head": [],
                                    "armor": [],
                                    "handL": [],
                                    "handR": [],
                                    "pants": [],
                                    "bootL": [],
                                    "bootR": [],
                                    "ring1": [],
                                    "ring2": [],
                                    "weapon": [],
                                    "belt": [],
                                },
                                "items": []
                            })
                            with open('./resources/battle/rogue.json', 'w') as f:
                                json.dump(contents, f, indent=4)
                            await message.channel.send('*Created a save file for {}.*'.format(message.author))
                    count = count + 1

                # game logic
                if len(message.content.split()) < 2:
                    await message.channel.send(help_msg())
                    return

                if len(message.content.split()) >= 2:
                    # Generating Starter armor (using function gen_starter())
                    if 'gen' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                # Helmet
                                p['equip']['pants'] = gen_starter(img_pants)
                                p['equip']['bootL'] = gen_starter(img_boots)
                                p['equip']['bootR'] = gen_starter(img_boots)
                                p['equip']['head'] = gen_starter(img_helmets)
                                p['equip']['armor'] = gen_starter(img_armor)
                                p['equip']['handL'] = gen_starter(img_gloves)
                                p['equip']['handR'] = gen_starter(img_gloves)
                                p['equip']['ring1'] = gen_starter(img_rings)
                                p['equip']['ring2'] = gen_starter(img_rings)
                                p['equip']['weapon'] = gen_starter(img_swords)
                                p['equip']['belt'] = gen_starter(img_belts)
                                with open('./resources/battle/rogue.json', 'w') as f:
                                    json.dump(contents, f, indent=4)

                    # Armor inspection
                    if 'ins' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                img_bg = Image.open('resources/misc/inv400x400.png')

                                asset = message.author.avatar_url_as(size=128)
                                data = BytesIO(await asset.read())
                                img_author = Image.open(data)
                                img_author = img_author.resize((100, 100))

                                # pixels offset, e.g. if smaller pictures are centered in a block
                                px_item_offset = 5
                                px_text_offset = 3
                                # px_per_item multiplier > width of img_bg
                                px_times_width = 4
                                # px_per_item multiplier > height of img_bg
                                px_times_height = 2

                                # Booleans to see if already checked a piece of armor
                                checked_head = False
                                checked_armor = False
                                checked_handL = False
                                checked_handR = False
                                checked_pants = False
                                checked_bootL = False
                                checked_bootR = False
                                checked_ring1 = False
                                checked_ring2 = False
                                checked_weapon = False
                                checked_belt = False

                                # Integer > items to generate (for every item in equipment)
                                int_itemgen = len(p['equip'])

                                iterated = 0
                                # Loop through all empty spaces in table
                                for y in range(px_times_height):
                                    for x in range(px_times_width):
                                        # Armor positions, numbering and drawing pics
                                        for int_generated in range(int_itemgen):
                                            if iterated == int_itemgen:
                                                break

                                            # Check helmet (Accurate position > inv400x400)
                                            if not p['equip']['head'] == []:
                                                if checked_head == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['head'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (100, 0), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['head'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (100 + px_item_offset, 0 + px_item_offset), img_temp)
                                                    str_iter = str(1)
                                                    # number all iterations in pic
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2 + shadow_offset, 0 + px_text_offset + shadow_offset), str_iter, (0, 0, 0),
                                                                                   font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2, 0 + px_text_offset), str_iter, (255, 255, 255),
                                                                                   font=font)
                                                    iterated = iterated + 1
                                                    checked_head = True
                                            # Check armor
                                            if not p['equip']['armor'] == []:
                                                if checked_armor == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['armor'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (100, 100), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['armor'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (100 + px_item_offset, 100 + px_item_offset), img_temp)
                                                    str_iter = str(2)
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2 + shadow_offset, 100 + px_text_offset + shadow_offset), str_iter, (0, 0, 0),
                                                                                   font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2, 100 + px_text_offset), str_iter, (255, 255, 255),
                                                                                   font=font)
                                                    iterated = iterated + 1
                                                    checked_armor = True
                                            # Check handL
                                            if not p['equip']['handL'] == []:
                                                if checked_handL == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['handL'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (0, 150), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['handL'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_temp = ImageOps.mirror(img_temp)
                                                    img_bg.paste(img_temp, (0 + px_item_offset, 150 + px_item_offset), img_temp)
                                                    str_iter = str(3)
                                                    ImageDraw.Draw(img_bg).text((0 + px_text_offset*2 + shadow_offset, 150 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((0 + px_text_offset*2, 150 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_handL = True
                                            # Check handR
                                            if not p['equip']['handR'] == []:
                                                if checked_handR == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['handR'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (200, 150), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['handR'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (200 + px_item_offset, 150 + px_item_offset), img_temp)
                                                    str_iter = str(4)
                                                    ImageDraw.Draw(img_bg).text((200 + px_text_offset*2 + shadow_offset, 150 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((200 + px_text_offset*2, 150 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_handR = True
                                            # Check pants
                                            if not p['equip']['pants'] == []:
                                                if checked_pants == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['pants'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (100, 200), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['pants'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (100 + px_item_offset, 200 + px_item_offset), img_temp)
                                                    str_iter = str(5)
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2 + shadow_offset, 200 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((100 + px_text_offset*2, 200 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_pants = True
                                            # Check bootL
                                            if not p['equip']['bootL'] == []:
                                                if checked_bootL == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['bootL'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (50, 300), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['bootL'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_temp = ImageOps.mirror(img_temp)
                                                    img_bg.paste(img_temp, (50 + px_item_offset, 300 + px_item_offset), img_temp)
                                                    str_iter = str(6)
                                                    ImageDraw.Draw(img_bg).text((50 + px_text_offset*2 + shadow_offset, 300 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((50 + px_text_offset*2, 300 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_bootL = True
                                            # Check bootR
                                            if not p['equip']['bootR'] == []:
                                                if checked_bootR == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['bootR'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (150, 300), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['bootR'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (150 + px_item_offset, 300 + px_item_offset), img_temp)
                                                    str_iter = str(7)
                                                    ImageDraw.Draw(img_bg).text((150 + px_text_offset*2 + shadow_offset, 300 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((150 + px_text_offset*2, 300 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_bootR = True
                                            # Check ring1
                                            if not p['equip']['ring1'] == []:
                                                if checked_ring1 == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['ring1'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (300, 0), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['ring1'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (300 + px_item_offset, 0 + px_item_offset), img_temp)
                                                    str_iter = str(8)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2 + shadow_offset, 0 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2, 0 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_ring1 = True
                                            # Check ring2
                                            if not p['equip']['ring2'] == []:
                                                if checked_ring2 == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['ring2'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (300, 100), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['ring2'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (300 + px_item_offset, 100 + px_item_offset), img_temp)
                                                    str_iter = str(9)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2 + shadow_offset, 100 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2, 100 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_ring2 = True
                                            # Check weapon
                                            if not p['equip']['weapon'] == []:
                                                if checked_weapon == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['weapon'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (300, 200), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['weapon'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (300 + px_item_offset, 200 + px_item_offset), img_temp)
                                                    str_iter = str(10)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2 + shadow_offset, 200 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2, 200 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_weapon = True
                                            # Check belt
                                            if not p['equip']['belt'] == []:
                                                if checked_belt == False:
                                                    # Frame
                                                    img_temp = getRarity(p['equip']['belt'][0])[2]
                                                    img_temp = img_temp.resize((100, 100))
                                                    img_bg.paste(img_temp, (300, 300), img_temp)
                                                    # Item
                                                    img_temp = Image.open(p['equip']['belt'][0][0])
                                                    img_temp = img_temp.resize((90, 90))
                                                    img_bg.paste(img_temp, (300 + px_item_offset, 300 + px_item_offset), img_temp)
                                                    str_iter = str(11)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2 + shadow_offset, 300 + px_text_offset + shadow_offset),str_iter, (0, 0, 0),
                                                                                font=shadow_font)
                                                    ImageDraw.Draw(img_bg).text((300 + px_text_offset*2, 300 + px_text_offset), str_iter, (255, 255, 255),
                                                                                font=font)
                                                    iterated = iterated + 1
                                                    checked_belt = True

                                # Final Output Image:
                                img_bg.save("resources/misc/temp.png")

                                if iterated == 0:
                                    await message.channel.send('{}, put on some clothes!'.format(message.author.mention), file=discord.File("resources/misc/temp.png"))
                                    return
                                else:
                                    await message.channel.send('{}, which item would you like to inspect?'.format(message.author.mention), file=discord.File("resources/misc/temp.png"))

                                    stop = 0
                                    while stop is not 1:
                                        def check(msg):
                                            return msg.author == message.author
                                        try:
                                            msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                        except asyncio.TimeoutError:
                                            await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                            return
                                        else:
                                            try:
                                                # Preventing shop from opening multiple times!
                                                if prefix in msg.content:
                                                    return
                                                if int(msg.content):
                                                    slot = getEquipment(int(msg.content))
                                                    await message.channel.send(file=getDesc(int(msg.content), p['equip'][slot][0], message.author.id))
                                                    stop = 1
                                                    return
                                            except ValueError:
                                                await message.channel.send("{}, I need a single integer!".format(message.author.mention))
                                            except IndexError:
                                                await message.channel.send("{}, you do not have anything equipped there!".format(message.author.mention))

                    # Loot generate random
                    if 'loot' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                await message.channel.send(file=getDesc(-1, generate_loot(0), message.author.id))

                    if 'inv' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                if (len(p['items'])) >= inventory_limit:
                                    await message.channel.send('{}, your inventory is full!'.format(message.author.mention), file=getInv(p))
                                    return
                                else:
                                    # p['items'].append(generate_loot(0))
                                    # with open('./resources/battle/rogue.json', 'w') as f:
                                    #     json.dump(contents, f, indent=4)
                                    await message.channel.send('{}'.format(message.author.mention), file=getInv(p))
                                    return

                    # Shop
                    if 'sp' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if str(message.author.id) == str(p['name']):
                                if (len(p['items'])) >= inventory_limit:
                                    await message.channel.send("{}, your inventory is full!\nYou can't buy anything right now...".format(message.author.mention))
                                    return

                                for s in contents['shop']:
                                    # If last generated shop is at least a day old, generate new shop with new seed
                                    if s['last_gen'] < str(datetime.date.today()):
                                        for s in contents['shop']:
                                            print(s)
                                            s['items'] = genShop(0, False, True)
                                            s['last_gen'] = str(datetime.date.today())
                                            with open('./resources/battle/rogue.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                        await message.channel.send('*Shop has been restocked today!*')

                                    await message.channel.send('{}, which item would you like to inspect?'.format(message.author.mention), file=genShop(0, False, False))

                                    # Stop item inspection loop. So when you make a mistake you can retry.
                                    stop_item_inspect = False
                                    while stop_item_inspect is False:
                                        def check(msg):
                                            return msg.author == message.author
                                        try:
                                            msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                        except asyncio.TimeoutError:
                                            await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                            return
                                        else:
                                            try:
                                                # Preventing shop from opening multiple times!
                                                if prefix in msg.content:
                                                    return
                                                if int(msg.content):
                                                    # Storing which item we're iterating right now
                                                    shop_item_index = int(msg.content) - 1
                                                    current_item = s['items'][shop_item_index]

                                                    stop_item_inspect = True

                                                    temp_msg = '{}, would you like to buy this item?\n**Y**/**N** (*Yes*/*No*)\n'.format(message.author.mention)
                                                    await message.channel.send(temp_msg, file=getDesc(-2, genShop(int(msg.content), True, False), message.author.id))


                                                    stop_item_buying = False
                                                    while stop_item_buying is False:
                                                        def check(msg):
                                                            return msg.author == message.author
                                                        try:
                                                            msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                                        except asyncio.TimeoutError:
                                                            await message.channel.send("{}, you've waited too long!".format(message.author.mention))
                                                            return
                                                        else:
                                                            if str(msg.content).lower() == 'y' or str(msg.content).lower() == 'yes':
                                                                # Add item to player inventory
                                                                p['items'].append(current_item)
                                                                # Remove item from shop and generate a new one
                                                                for s in contents['shop']:
                                                                    s['items'].remove(current_item)
                                                                    s['items'].append(generate_loot(0))
                                                                with open('./resources/battle/rogue.json', 'w') as f:
                                                                    json.dump(contents, f, indent=4)
                                                                await message.channel.send(
                                                                    "{}, you bought the **{}**!\nIt's now in your inventory".format(message.author.mention, current_item[1]),
                                                                    file=getInv(p))
                                                                stop_item_buying = True
                                                                return
                                                            elif str(msg.content).lower() == 'n' or str(msg.content).lower() == 'no':
                                                                await message.channel.send("{} did *not* buy the **{}** and has left the shop!".format(message.author.mention, current_item[1]))
                                                                stop_item_buying = True
                                                                return
                                                            else:
                                                                await message.channel.send("{}, answer with **Y**/**N** (*Yes*/*No*)".format(message.author.mention))

                                            except ValueError:
                                                await message.channel.send("{}, I need a single integer!".format(message.author.mention))
                                            # except IndexError:
                                            #     await message.channel.send("{}, there aren't that many items in the shop!".format(message.author.mention))

                    else:
                        print('help msg')

# Rarity multiplier. Can be / 2 or ** -2 or ** -3
# to make rarity values 1-4 inverted, and used as a weight
def rarity_multiplier(a):
    return a ** -2.25

# Specific is the representing integer for a dictionary
# 1 = axe, 2 = sword, 3 = ring, 4 = head, 5 = armor, 6 = gloves, 7 = boots, 8 = pants, 9 = belts
# 0 or any other integer will also randomly generate any of the above
# returns an item as array [pic, name, rarity etc.]
def generate_loot(specific):
    # Generating items
    items_gend = []

    if specific == 0:
        int_r = random.randrange(1, 9)
    elif specific not in range(1,9):
        print('ERROR! Generate_loot function only has {}\nGenerating random loot in that range'.format(range(1,9)))
        int_r = random.randrange(1, 9)
    else:
        int_r = specific

    # if random or specific int corresponds with a represented dictionary integer, generate loot based on rarity weight via weight_gen function
    if int_r == 1:
        items_gend.append(weight_gen(img_axes))
    if int_r == 2:
        items_gend.append(weight_gen(img_swords))
    if int_r == 3:
        items_gend.append(weight_gen(img_rings))
    if int_r == 4:
        items_gend.append(weight_gen(img_helmets))
    if int_r == 5:
        items_gend.append(weight_gen(img_armor))
    if int_r == 6:
        items_gend.append(weight_gen(img_gloves))
    if int_r == 7:
        items_gend.append(weight_gen(img_boots))
    if int_r == 8:
        items_gend.append(weight_gen(img_pants))
    if int_r == 9:
        items_gend.append(weight_gen(img_belts))
        
    return items_gend[0]

# This function takes a dictionary as input. E.g. img_axes
def weight_gen(img):
    # Weights based on rarity using rarity_multiplier function
    weigths = []
    for weight_ite in range(len(img)):
        weigths.append(rarity_multiplier(img[list(img.keys())[weight_ite]][2]))
    # Get random choice
    random_choice = random.choices(list(img), weights=weigths)
    # Grab random key from dict and take its first array value > 0. file-loc picture 1. name 2.RANK-pool
    return img[[random_choice[0]][0]]

# Get description for an item key from a dictionary. Returns discord temp image file
# SLOT INT, DICT KEY, AUTHOR ID
# e.g. 1 (head), p['equip'][1 (head)][0], message.author.id
# If slot = 0, do different message.
# If slot = -1 do loot text
# If slot = -2 do shop text
def getDesc(slot, dict_key, id):
    with open('./resources/battle/rogue.json') as log:
        contents = json.load(log)
    for p in contents['players']:
        if str(id) == str(p['name']):
            # pixels offset for text
            px_text_offset = 3

            # Getting empty PNG
            img_bg = Image.open('resources/misc/empty600x400.png')
            # Getting armor rarity
            rarity = dict_key[2]
            # Color for text & Color for frame
            color = (0, 0, 0)
            if rarity == 1:
                rarity = 'Bad'
                color = col_bad
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_green.png')
                img_temp = img_temp.resize((200, 200))
                img_bg.paste(img_temp, (400, 0), img_temp)
            elif rarity == 2:
                rarity = 'Ok'
                color = col_ok
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_blue.png')
                img_temp = img_temp.resize((200, 200))
                img_bg.paste(img_temp, (400, 0), img_temp)
            elif rarity == 3:
                rarity = 'Rare'
                color = col_rare
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_red.png')
                img_temp = img_temp.resize((200, 200))
                img_bg.paste(img_temp, (400, 0), img_temp)
            elif rarity == 4:
                rarity = 'Ultra'
                color = col_ultra
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_violet.png')
                img_temp = img_temp.resize((200, 200))
                img_bg.paste(img_temp, (400, 0), img_temp)
            else:
                rarity = 'Unknown'
                color = col_unknown
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_blue.png')
                img_temp = img_temp.resize((200, 200))
                img_bg.paste(img_temp, (400, 0), img_temp)

            # text beneath pic.
            str_iter = 'Quality: '
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (255,255,255), font=font)

            # Rarity text with different color. Getting characters from last str_iter. Adding those amount of spaces.
            chars = len(str_iter)
            str_iter = ' '
            str_iter = str_iter * chars
            str_iter = str_iter + '{}'.format(rarity)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, color, font=font)

            # Adding armor/damage amount
            type = ''
            if dict_key[4] == 1:
                type = '🔘'
                str_iter = '\n' + type
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=emoji_font)
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (51, 160, 226), font=emoji_font)
            elif dict_key[4] == 2:
                type = '🔪'
                str_iter = '\n' + type
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=emoji_font)
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (200, 50, 50), font=emoji_font)
            else:
                type = 'unknown'
                str_iter = '\n' + type
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=emoji_font)
                ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (255, 196, 66), font=emoji_font)

            str_iter = '\n  +{}'.format(dict_key[3])
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (255,255,255), font=font)

            # Adding gem emoji, then item value
            str_iter = '\n\n💎'
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=emoji_font)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (0, 255, 255), font=emoji_font)

            str_iter = '\n\n  {}'.format(dict_key[5])
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2 + shadow_offset, 200 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((400 + px_text_offset * 2, 200 + px_text_offset), str_iter, (0, 255, 255), font=font)


            # Loot text
            if slot == -1:
                temp_item = dict_key
                str_iter = 'You found:\n\nThe '
            # Shop text
            elif slot == -2:
                temp_item = dict_key
                str_iter = '\n\nThe '
            # Equipment text
            else:
                temp_item = p['equip'][getEquipment(int(slot))][0]
                str_iter = 'Equipment slot {} [{}]\n\nThe '.format(slot, getEquipment(int(slot)))

            # Pasting equipment to empty PNG on top of frame
            img_temp = Image.open(temp_item[0])
            img_temp = img_temp.resize((180, 180))
            img_bg.paste(img_temp, (410, 10), img_temp)

            # Drawing 1st sentence
            ImageDraw.Draw(img_bg).text((px_text_offset * 2 + shadow_offset, 0 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((px_text_offset * 2, 0 + px_text_offset), str_iter, (255, 255, 255), font=font)

            # Drawing item name in rarity color
            str_iter = '\n\n    {}'.format(temp_item[1])
            ImageDraw.Draw(img_bg).text((px_text_offset * 2 + shadow_offset, 0 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((px_text_offset * 2, 0 + px_text_offset), str_iter, color, font=font)

            # Drawing item description in grey
            str_iter = '\n\n\n\n'
            idx = 0
            for char in temp_item[6]:
                idx = idx + 1
                if idx >= 18:
                    if char == ' ':
                        str_iter = str_iter + '\n'
                        idx = 0
                    elif idx == 26:
                        str_iter = str_iter + char + '-\n'
                        idx = 0
                    else:
                        str_iter = str_iter + char
                else:
                    str_iter = str_iter + char
            ImageDraw.Draw(img_bg).text((px_text_offset * 2 + shadow_offset, 0 + px_text_offset + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
            ImageDraw.Draw(img_bg).text((px_text_offset * 2, 0 + px_text_offset), str_iter, (200,200,200), font=font)


            img_bg.save("resources/misc/temp.png")

            return discord.File("resources/misc/temp.png")

# Get equipment string (AKA: key in p['equip'] array > head, armor, handL etc.)
def getEquipment(int):
    if int == 1:
        return 'head'
    if int == 2:
        return 'armor'
    if int == 3:
        return 'handL'
    if int == 4:
        return 'handR'
    if int == 5:
        return 'pants'
    if int == 6:
        return 'bootL'
    if int == 7:
        return 'bootR'
    if int == 8:
        return 'ring1'
    if int == 9:
        return 'ring2'
    if int == 10:
        return 'weapon'
    if int == 11:
        return 'belt'

# Function for generating dictionary armor/damage/value range
def genInt(min,max):
    if min == max:
        return max
    else:
        return random.randrange(min, max)

# Function for generating shop layout
# Slot = which slot you want to get (Leave at 0 if you don't want to request a specific item)
# bool_get_item = True//False whether you want to get a specific item that you request with a slot integer mentioned above
# bool_generate = True/False if you want to generate a fresh shop
def genShop(slot, bool_get_item, bool_generate):
    # px_per_item multiplier > width of img_bg
    px_times_width = 4
    # px_per_item multiplier > height of img_bg
    px_times_height = 2
    # Integer > items to generate
    int_itemgen = px_times_width * px_times_height

    img_bg = Image.open('resources/misc/inv400x200.png')

    iterated = 0
    items_gend = []
    with open('./resources/battle/rogue.json') as log:
        contents = json.load(log)
        if bool_generate == True:
            for items_to_gen in range(int_itemgen):
                items_gend.append(generate_loot(0))
            return items_gend
        else:
            for s in contents['shop']:
                items_gend = s['items']


    # Loop through all empty spaces in table
    for y in range(px_times_height):
        for x in range(px_times_width):
            # Getting rarity color
            rarity = items_gend[iterated][2]
            # Color for text & Color for frame
            color = (0, 0, 0)
            if rarity == 1:
                rarity = 'Bad'
                color = col_bad
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_green.png')
                img_temp = img_temp.resize((100, 100))
                img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
            elif rarity == 2:
                rarity = 'Ok'
                color = col_ok
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_blue.png')
                img_temp = img_temp.resize((100, 100))
                img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
            elif rarity == 3:
                rarity = 'Rare'
                color = col_rare
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_red.png')
                img_temp = img_temp.resize((100, 100))
                img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
            elif rarity == 4:
                rarity = 'Ultra'
                color = col_ultra
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_violet.png')
                img_temp = img_temp.resize((100, 100))
                img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
            else:
                rarity = 'Unknown'
                color = col_unknown
                # Pasting frame behind armor piece
                img_temp = Image.open('resources/misc/frame_blue.png')
                img_temp = img_temp.resize((100, 100))
                img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)

            img_temp = Image.open(items_gend[iterated][0])
            img_temp = img_temp.resize((90, 90))

            img_bg.paste(img_temp, (x * px_per_item + px_item_offset, y * px_per_item + px_item_offset), img_temp)

            str_iter = str(iterated + 1) + ' '

            # number all iterations in pic
            ImageDraw.Draw(img_bg).text((x * px_per_item + shadow_offset, y * px_per_item + shadow_offset), str_iter, (0, 0, 0),
                                           font=shadow_font)
            ImageDraw.Draw(img_bg).text((x * px_per_item, y * px_per_item), str_iter, (255,255,255),
                                           font=font)

            iterated = iterated + 1

    img_bg.save("resources/misc/temp.png")

    if bool_get_item == True:
        return items_gend[slot - 1]
    else:
        return discord.File("resources/misc/temp.png")

# Script to get an items rarity. Input the full item array
# returns rarity = (string)
#         color  = (0,0,0)
#         frame  = (Image.open())

# getRarity(p['equip']['head'])[0] returns rarity string of player's helmet
def getRarity(item):
    # Getting armor rarity
    rarity = item[2]
    # Color for text & Color for frame
    color = (0, 0, 0)
    if rarity == 1:
        rarity = 'Bad'
        color = col_bad
        frame = Image.open('resources/misc/frame_green.png')
    elif rarity == 2:
        rarity = 'Ok'
        color = col_ok
        frame = Image.open('resources/misc/frame_blue.png')
    elif rarity == 3:
        rarity = 'Rare'
        color = col_rare
        frame = Image.open('resources/misc/frame_red.png')
    elif rarity == 4:
        rarity = 'Ultra'
        color = col_ultra
        frame = Image.open('resources/misc/frame_violet.png')
    else:
        rarity = 'Unknown'
        color = col_unknown
        frame = Image.open('resources/misc/frame_yellow.png')
    return rarity, color, frame

# Function for getting player inventory
# player = p from a loop: for p in contents['players']
# returns discord.file(image)
def getInv(player):
    # px_per_item multiplier > width of img_bg
    px_times_width = 4
    # px_per_item multiplier > height of img_bg
    px_times_height = 2

    img_bg = Image.open('resources/misc/inv400x200.png')

    iterated = 0

    #  Store familiar items so we don't iterate over them again!
    stored = []

    # Loop through all empty spaces in table
    for y in range(px_times_height):
        for x in range(px_times_width):
            for p_items in player['items']:
                if p_items not in stored:
                    stored.append(p_items)

                    # Getting rarity color
                    rarity = p_items[2]
                    # Color for text & Color for frame
                    color = (0, 0, 0)
                    if rarity == 1:
                        rarity = 'Bad'
                        color = col_bad
                        # Pasting frame behind armor piece
                        img_temp = Image.open('resources/misc/frame_green.png')
                        img_temp = img_temp.resize((100, 100))
                        img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    elif rarity == 2:
                        rarity = 'Ok'
                        color = col_ok
                        # Pasting frame behind armor piece
                        img_temp = Image.open('resources/misc/frame_blue.png')
                        img_temp = img_temp.resize((100, 100))
                        img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    elif rarity == 3:
                        rarity = 'Rare'
                        color = col_rare
                        # Pasting frame behind armor piece
                        img_temp = Image.open('resources/misc/frame_red.png')
                        img_temp = img_temp.resize((100, 100))
                        img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    elif rarity == 4:
                        rarity = 'Ultra'
                        color = col_ultra
                        # Pasting frame behind armor piece
                        img_temp = Image.open('resources/misc/frame_violet.png')
                        img_temp = img_temp.resize((100, 100))
                        img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)
                    else:
                        rarity = 'Unknown'
                        color = col_unknown
                        # Pasting frame behind armor piece
                        img_temp = Image.open('resources/misc/frame_blue.png')
                        img_temp = img_temp.resize((100, 100))
                        img_bg.paste(img_temp, (x * px_per_item, y * px_per_item), img_temp)

                    img_temp = Image.open(p_items[0])
                    img_temp = img_temp.resize((90, 90))

                    img_bg.paste(img_temp, (x * px_per_item + px_item_offset, y * px_per_item + px_item_offset), img_temp)

                    str_iter = str(iterated + 1) + ' '

                    # number all iterations in pic
                    ImageDraw.Draw(img_bg).text((x * px_per_item + shadow_offset, y * px_per_item + shadow_offset), str_iter, (0, 0, 0), font=shadow_font)
                    ImageDraw.Draw(img_bg).text((x * px_per_item, y * px_per_item), str_iter, (255, 255, 255), font=font)

                    iterated = iterated + 1
                    break


    img_bg.save("resources/misc/temp.png")

    return discord.File("resources/misc/temp.png")

# Dictionaries for cleaner code in rogue py

# global dict for items
# key: [0.file-location, 1.name, 2.rarity (1:bad 2:ok 3:good 4:sick), 3.armor/damage range, 4.armor/damage type (1:armor 2:damage etc.), 5.value, 6.description]
img_rings = {
    "r1": ['resources/items/ring/r1.png', "Dragon Ring", 4, genInt(4,8), 2, genInt(1,100), "Description", ],
    "r2": ['resources/items/ring/r2.png', "Emerald Ring", 3, genInt(3,6), 2, genInt(1,100), "Description"],
    "r3": ['resources/items/ring/r3.png', "Magic Ring", 1, genInt(1,2), 1, genInt(1,100), "Description"],
    "r4": ['resources/items/ring/r4.png', "Diamond Ring", 4, genInt(2,9), 1, genInt(1,100), "Description"],
    "r5": ['resources/items/ring/r5.png', "Topaz Ring", 3, genInt(2,7), 2, genInt(1,100), "Description"],
    "r6": ['resources/items/ring/r6.png', "All-seeing Ring", 4, genInt(7,9), 1, genInt(1,100), "Description"],
    "r7": ['resources/items/ring/r7.png', "Ruby Ring", 2, genInt(1,4), 2, genInt(1,100), "Description"],
    "r8": ['resources/items/ring/r8.png', "Orb Ring", 3, genInt(3,5), 2, genInt(1,100), "Description"],
    "r9": ['resources/items/ring/r9.png', "Amethyst Ring", 3, genInt(3,6), 1, genInt(1,100), "Description"],
    "r10": ['resources/items/ring/r10.png', "Rusty Ring", 1, genInt(1,1), 1, genInt(1,100), "Description"],
    "r12": ['resources/items/ring/r11.png', "Gold Ring", 2, genInt(1,4), 1, genInt(1,100), "Description"],
    "r13": ['resources/items/ring/r12.png', "Iron Ring", 1, genInt(1,2), 2, genInt(1,100), "Description"],
    "r14": ['resources/items/ring/r13.png', "Lesser Emerald Ring", 2, genInt(1,6), 2, genInt(1,100), "Description"]
}

img_swords = {
    "s1": ['resources/items/sword/s1.png', "Iron Cutlass", 2, genInt(1,8), 2, genInt(1,100), "Description"],
    "s2": ['resources/items/sword/s2.png', "Steel Dagger", 3, genInt(3,11), 2, genInt(1,100), "Description"],
    "s3": ['resources/items/sword/s3.png', "Iron Sword", 2, genInt(2,6), 2, genInt(1,100), "Description"],
    "s4": ['resources/items/sword/s4.png', "Great Kunai", 2, genInt(1,4), 2, genInt(1,100), "Description"],
    "s5": ['resources/items/sword/s5.png', "Rugged Dagger", 1, genInt(1,1), 2, genInt(1,100), "Description"],
    "s6": ['resources/items/sword/s6.png', "Fine Sword", 3, genInt(4,11), 2, genInt(1,100), "Description"],
    "s7": ['resources/items/sword/s7.png', "Diamond Sword", 4, genInt(13,20), 2, genInt(1,100), "Description"],
    "s8": ['resources/items/sword/s8.png', "Silver Sword", 2, genInt(3,7), 2, genInt(1,100), "Description"],
    "s9": ['resources/items/sword/s9.png', "Elven Sword", 3, genInt(5,12), 2, genInt(1,100), "Description"],
    "s10": ['resources/items/sword/s10.png', "Lapis Sword", 2, genInt(2,8), 2, genInt(1,100), "Description"],
    "s11": ['resources/items/sword/s11.png', "King Sword", 4, genInt(15,20), 2, genInt(1,100), "Description"],
    "s12": ['resources/items/sword/s12.png', "Short Sword", 1, genInt(1,2), 2, genInt(1,100), "Description"],
    "s13": ['resources/items/sword/s13.png', "Rusty Dagger", 1, genInt(1,1), 2, genInt(1,100), "Description"],
    "s14": ['resources/items/sword/s14.png', "Unholy Sword", 4, genInt(12,20), 2, genInt(1,100), "Description"],
    "s15": ['resources/items/sword/s15.png', "Rusty Sword", 1, genInt(1,3), 2, genInt(1,100), "Description"]
}

img_axes = {
    "a1": ['resources/items/axe/a1.png', "Iron Labrys", 2, genInt(1,7), 2, genInt(1,100), "Description"],
    "a2": ['resources/items/axe/a2.png', "Rusty Axe", 1, genInt(1,2), 2, genInt(1,100), "Description"],
    "a3": ['resources/items/axe/a3.png', "Elven Axe", 2, genInt(2,8), 2, genInt(1,100), "Description"],
    "a4": ['resources/items/axe/a4.png', "Meteorite Labrys", 3, genInt(6,15), 2, genInt(1,100), "Description"],
    "a5": ['resources/items/axe/a5.png', "Blunt Axe", 1, genInt(1,3), 2, genInt(1,100), "Description"],
    "a6": ['resources/items/axe/a6.png', "Warpick", 1, genInt(1,1), 2, genInt(1,100), "Description"],
    "a7": ['resources/items/axe/a7.png', "Iron Axe", 2, genInt(1,6), 2, genInt(1,100), "Description"],
    "a8": ['resources/items/axe/a8.png', "Diamond Axe", 4, genInt(12,22), 2, genInt(1,100), "Description"],
    "a9": ['resources/items/axe/a9.png', "Ancient Axe", 3, genInt(7,14), 2, genInt(1,100), "Description"],
    "a10": ['resources/items/axe/a10.png', "Dwarven Axe", 4, genInt(16,21), 2, genInt(1,100), "Description"]
}

img_helmets = {
    "h1": ['resources/items/helmet/helmet_1.png', "Iron Helmet", 1, genInt(1,2), 1, genInt(1,100), "This helmet was mass produced. Though it looks clean, it feels like it could fall apart at any moment..."],
    "h2": ['resources/items/helmet/helmet_2.png', "Viking Helmet", 1, genInt(1,2), 1, genInt(1,100), "There's some inscriptions on the back, but you can't make out what it means. You also see some blonde hairs stuck in a small wooden crevice."],
    "h3": ['resources/items/helmet/helmet_3.png', "Steel Helmet", 2, genInt(2,4), 1, genInt(1,100), "It feels pretty sturdy. It emits a deep reverberation when you knock on it."],
    "h4": ['resources/items/helmet/helmet_4.png', "Silver Helmet", 3, genInt(3,6), 1, genInt(1,100), "Don't let its looks deceive you. It appears long, heavy and therefore clumsy. But it's great at deflecting strikes from your opponents."],
    "h5": ['resources/items/helmet/helmet_5.png', "Gold Helmet", 4, genInt(4,8), 1, genInt(1,100), "It looks like it could be worth a hefty sum. You might blind your opponents with its bright reflective properties."]
}

img_armor = {
    "ar1": ['resources/items/armor/armor_1.png', "Amethyst Chestplate", 3, genInt(4,9), 1, genInt(1,100), "Description"],
    "ar2": ['resources/items/armor/armor_2.png', "Rusty Chestguard", 1, genInt(1,3), 1, genInt(1,100), "Description"],
    "ar3": ['resources/items/armor/armor_3.png', "Diamond Heirloom", 4, genInt(5,12), 1, genInt(1,100), "Description"],
    "ar4": ['resources/items/armor/armor_4.png', "Obese Cuirass", 2, genInt(2,5), 1, genInt(1,100), "Description"]
}

img_gloves = {
    "g1": ['resources/items/gloves/gloves_1.png', "Diamond Gauntlet", 4, genInt(4,6), 1, genInt(1,100), "Description"],
    "g2": ['resources/items/gloves/gloves_2.png', "Iron Handguards", 2, genInt(2,3), 1, genInt(1,100), "Description"],
    "g3": ['resources/items/gloves/gloves_3.png', "Sausage Fingers", 1, genInt(1,2), 1, genInt(1,100), "Description"],
    "g4": ['resources/items/gloves/gloves_4.png', "Ancient Gloves", 3, genInt(3,5), 1, genInt(1,100), "Description"]
}

img_pants = {
    "p1": ['resources/items/pants/pants_1.png', "Leather Legwraps", 1, genInt(1,1), 1, genInt(1,100), "Description"],
    "p2": ['resources/items/pants/pants_2.png', "Diamond Greaves", 4, genInt(4,8), 1, genInt(1,100), "Description"],
    "p3": ['resources/items/pants/pants_3.png', "Silk Leggings", 2, genInt(1,4), 1, genInt(1,100), "Description"],
    "p4": ['resources/items/pants/pants_4.png', "Iron Breeches", 3, genInt(3,6), 1, genInt(1,100), "Description"]
}

img_boots = {
    "b1": ['resources/items/boots/boots_1.png', "Leather Sprinters", 2, genInt(2,3), 1, genInt(1,100), "Description"],
    "b2": ['resources/items/boots/boots_2.png', "Iron Sabaton", 3, genInt(3,5), 1, genInt(1,100), "Description"],
    "b3": ['resources/items/boots/boots_3.png', "Dwarven Greatboots", 4, genInt(4,6), 1, genInt(1,100), "Description"],
    "b4": ['resources/items/boots/boots_4.png', "Worn Footpads", 1, genInt(1,2), 1, genInt(1,100), "Description"]
}

img_belts = {
    "be1": ['resources/items/belts/belts_1.png', "Reinforced Belt", 4, genInt(3,5), 1, genInt(1,100), "Description"],
    "be2": ['resources/items/belts/belts_2.png', "Leather Belt", 1, genInt(1,1), 1, genInt(1,100), "Description"],
    "be3": ['resources/items/belts/belts_3.png', "Rusty Belt", 2, genInt(1,2), 1, genInt(1,100), "Description"],
    "be4": ['resources/items/belts/belts_4.png', "Viking Belt", 1, genInt(1,1), 1, genInt(1,100), "Description"],
    "be5": ['resources/items/belts/belts_5.png', "Skele-belt", 3, genInt(1,4), 1, genInt(1,100), "Description"]
}

# V generation methods V

# Storing item in json

# for p in contents['players']:
#     if str(message.author.id) == str(p['name']):
#         p['equip']['head'] = [items_gend[iterated]]
#         with open('./resources/battle/rogue.json', 'w') as f:
#             json.dump(contents, f, indent=4)


# Rarity Text colors & generation

# rarity = items_gend[iterated][2]
# color = (0, 0, 0)
# if rarity == 1:
#     rarity = 'Bad'
#     color = (255, 0, 0)
# if rarity == 2:
#     rarity = 'Ok'
#     color = (255, 255, 0)
# if rarity == 3:
#     rarity = 'Rare'
#     color = (0, 255, 0)
# if rarity == 4:
#     rarity = 'Ultra'
#     color = (255, 0, 255)
#
# # Add blank space after every character from the iterable integer [var iterated]
# spaces = ''
# for chars in range(len(str_iter)):
#     spaces = spaces + ' '
#
# rarity = "{}{}".format(spaces, rarity)
#
# # amount of spaces between number and rarity
# ImageDraw.Draw(img_bg).text((x * px_per_item + shadow_offset, y * px_per_item + shadow_offset), rarity,
#                             (0, 0, 0), font=shadow_font)
# ImageDraw.Draw(img_bg).text((x * px_per_item, y * px_per_item), rarity,
#                             color, font=font)