import random
import asyncio
import json
from .insultme import generate_insult
import os
import io

timeout_time = 10.0  # message.author response time in seconds
wait_time = 0  # time in between bot messages TO DO --> change to 3 or 2, used for testing
max_player_level = 20  # must be at least 10
crafting_cost = 30  # cost of crafting a new sword
max_items = 3  # maximum amount of items in player inventory
max_shop_items = 3  # maximum amount of items in shop inventory TODO change to 10


class monster:
    def __init__(self, name, hp, min_damage, max_damage, min_reward, max_reward, min_xp, max_xp, odds):
        self.name = name
        self.hp = hp
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.min_reward = min_reward
        self.max_reward = max_reward
        self.min_xp = min_xp
        self.max_xp = max_xp
        self.odds = odds


monster_list = dict(
    goblin=monster("Goblin", 5, 0, 2, 1, 3, 50, 100, .5),
    imp=monster("Imp", 3, 0, 1, 0, 1, 25, 50, .5),
    wurm=monster("Wurm", 2, 0, 1, 0, 1, 25, 50, .3),
    ogre=monster("Ogre", 7, 0, 3, 1, 5, 75, 150, .5),
    orc=monster("Orc", 10, 0, 4, 1, 5, 100, 200, .3),
    golem=monster("Golden Golem", 10, 1, 5, 10, 50, 150, 350, .1),
    dragon=monster("Dragon", 30, 1, 8, 20, 100, 500, 1000, .02),
    demon=monster("Demon", 20, 0, 6, 20, 70, 300, 500, .05)
)
monsters = []
monsters_weight = []
for k in monster_list:
    monsters.append(monster_list[k])
    monsters_weight.append(monster_list[k].odds)


class modifier:
    def __init__(self, name, price, odds, extra_damage):
        self.name = name
        self.price = price
        self.odds = odds
        self.extra_damage = extra_damage


modifier_list = dict(
    legendary=modifier("```css\n[Legendary]```", 20, .01, 10),
    rare=modifier("```ini\n[Rare]```", 10, .05, 3),
    uncommon=modifier("```diff\n! Uncommon```", 4, .30, 1),
    common=modifier("```\nCommon```", 1, .50, 0)
)
modifiers = []
modifiers_weight = []
for k in modifier_list:
    modifiers.append(modifier_list[k])
    modifiers_weight.append(modifier_list[k].odds)


class sword:
    def __init__(self, name, min_damage, max_damage, price, odds):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.price = price
        self.odds = odds


sword_list = dict(
    excalibur=sword("```diff\n- Excalibur```", 30, 100, 1000, 0.001),
    dawnbreaker=sword("```css\n[Dawn breaker]```", 7, 25, 100, .0025),
    banisher=sword("```css\n[Banisher]```", 5, 20, 100, .004),
    katana=sword("```css\n[Katana]```", 5, 20, 100, .004),
    broadsword=sword("```\nBroadsword```", 2, 7, 20, .15),
    claymore=sword("```\nClaymore```", 1, 4, 10, .25),
    sabre=sword("```\nSabre```", 0, 5, 5, .20),
    knife=sword("```\nKnife```", 0, 3, 3, .30)
)
swords = []
swords_weight = []
for k in sword_list:
    swords.append(sword_list[k])
    swords_weight.append(sword_list[k].odds)


class item:
    def __init__(self, name, buy_price, sell_price, heal, odds):
        self.name = name
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.heal = heal
        self.odds = odds


item_list = dict(
    apple=item("Apple", 3, 1, 2, 0.7),
    bread=item("Bread", 10, 2, 5, 0.35),
    stew=item("Stew", 50, 10, 15, 0.2)
)
items = []
items_weight = []
for k in item_list:
    items.append(item_list[k])
    items_weight.append(item_list[k].odds)

# TODO Special Items: heart=item("HP Pizza", 100, 10, 15, 0, 0.5)

def generate_insult():
    with open('./resources/insults/insults-eng.txt') as insults:
        with open('./resources/insults/adjectives-eng.txt') as adjectives:
            return random.choice(list(adjectives)).rstrip() + ' ' + random.choice(list(insults)).rstrip()


data = {}
data['players'] = []

data_shop = {}
data_shop['shop_items'] = []


def create_json_player():
    with io.open(os.path.join('./resources/battle', 'log.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/log.json') as log:
        first_log = json.load(log)
        first_log['players'].append({'name': 'null'})
        with open('./resources/battle/log.json', 'w') as f:
            json.dump(first_log, f, indent=4)


def create_json_shop():
    with io.open(os.path.join('./resources/battle', 'shop.json'), 'w') as file:
        json.dump(data_shop, file, indent=4)
    with open('./resources/battle/shop.json') as log:
        first_log = json.load(log)
        first_log['shop_items'].append({'items': []})
        with open('./resources/battle/shop.json', 'w') as f:
            json.dump(first_log, f, indent=4)


# adventure game
async def run(client, message):
    # loading save files
    if not os.path.isfile('./resources/battle/log.json'):
        # if file not found, make log.json with create_json_player function
        create_json_player()
        await message.channel.send('Log.json has been created. Please try again.')
    else:
        with open('./resources/battle/log.json') as log:
            contents = json.load(log)
            if str(contents) == '' or str(contents) == '[]':
                create_json_player()
                await message.channel.send('Log.json was empty. Please try again.')
            else:
                count = 0
                for p in contents['players']:
                    if '{}'.format(message.author) == '{}'.format(p['name']):
                        print("Found {}".format(message.author) + " in players!")
                    elif '{}'.format(message.author) is not '{}'.format(p['name']) and count == int(
                            len(contents['players'])):
                        contents['players'].append({
                            'name': '{}'.format(message.author),  # TODO change to author.id in def checks!!
                            'name_at_save': '{}'.format(message.author.name),
                            'hp': 10,
                            'max_hp': 10,
                            'lvl': 1,
                            'xp': 0,
                            'gem': 0,
                            "inv": [
                                {
                                    "modifier": "```\nCommon```",
                                    "sword": "```\nKnife```"
                                }
                            ],
                            "items": []
                        })
                        with open('./resources/battle/log.json', 'w') as f:
                            json.dump(contents, f, indent=4)
                        await message.channel.send('*Created a save file for {}.*'.format(message.author))
                        await asyncio.sleep(wait_time)
                    count = count + 1

                # game logic
                if len(message.content.split()) < 2:
                    # TODO make different areas based on player lvl with harder monsters more rewards
                    r_monster = random.choices(monsters, monsters_weight)
                    response = "{} encountered *{}* with {} HP. You can either **fight** or **run**." \
                        .format(message.author.mention, r_monster[0].name, r_monster[0].hp)
                    await message.channel.send(response)

                    def check(msg):
                        return msg.author == message.author

                    try:
                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                    except asyncio.TimeoutError:
                        await message.channel.send("{} didn't respond in time!:zzz:".format(message.author.mention))
                    else:
                        if msg.content.lower() == 'fight':

                            max_hp = p['max_hp']
                            player_hp = p['hp']
                            monster_hp = r_monster[0].hp
                            someone_died = 0

                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                for l in p['inv']:
                                    for m in modifiers:
                                        if l['modifier'] in str(m.name):
                                            current_modifier = m
                                    for s in swords:
                                        if l['sword'] in str(s.name):
                                            current_sword = s

                                    while someone_died == 0:

                                        damage = random.randint(current_sword.min_damage,
                                                                current_sword.max_damage) + current_modifier.extra_damage
                                        monster_hp = monster_hp - damage
                                        if monster_hp <= 0:
                                            monster_hp = 0
                                        await message.channel.send(
                                            ":crossed_swords:\n```css\n{} did [{}] damage!\n{} HP: {} / {}```"
                                                .format(message.author.name, damage, r_monster[0].name,
                                                        monster_hp, r_monster[0].hp))
                                        if monster_hp <= 0:
                                            p['hp'] = player_hp

                                            await asyncio.sleep(wait_time)
                                            await message.channel.send(":trophy: {} has slain the *{}*! :trophy:"
                                                                       .format(message.author.mention,
                                                                               r_monster[0].name))
                                            await asyncio.sleep(wait_time)

                                            # Experience points
                                            xp = random.randrange(r_monster[0].min_xp, r_monster[0].max_xp)
                                            p['xp'] = p['xp'] + xp
                                            with open('./resources/battle/log.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                            await message.channel.send(
                                                "{} received *{}* XP".format(message.author.mention, xp))
                                            await asyncio.sleep(wait_time)

                                            # Level up check
                                            if p['lvl'] < max_player_level:
                                                # Arithmetic level progression
                                                if p['xp'] >= (50 * p['lvl'] * (1 + p['lvl'])):
                                                    p['lvl'] = p['lvl'] + 1
                                                    with open('./resources/battle/log.json', 'w') as f:
                                                        json.dump(contents, f, indent=4)
                                                    await message.channel.send("**{} LEVELED UP!**"
                                                                               .format(message.author.mention))
                                                    await asyncio.sleep(wait_time)
                                            elif int(p['lvl']) == int(max_player_level):
                                                await message.channel.send(
                                                    ":dart: *{} has reached* **max level {}**! :dart:"
                                                        .format(message.author.mention, max_player_level))
                                                p['lvl'] = max_player_level + 1

                                            # Gems
                                            award = random.randrange(r_monster[0].min_reward, r_monster[0].max_reward)
                                            p['gem'] = p['gem'] + award
                                            with open('./resources/battle/log.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                            await message.channel.send(
                                                "{} found **{}** :gem:".format(message.author.mention, award))
                                            someone_died = 1
                                            return
                                        await asyncio.sleep(wait_time)

                                        received_damage = random.randint(r_monster[0].min_damage,
                                                                         r_monster[0].max_damage)
                                        player_hp = player_hp - received_damage
                                        if player_hp <= 0:
                                            player_hp = 0
                                        await message.channel.send(
                                            ":shield:\n```ini\n{} received [{}] damage! Your HP:\n[{}/{}]```"
                                                .format(message.author.name, received_damage, player_hp, max_hp))
                                        if player_hp <= 0:
                                            player_hp = 0
                                            await message.channel.send("{} has been killed by the *{}*! RIP :skull:"
                                                                       .format(message.author.mention,
                                                                               r_monster[0].name))
                                            await asyncio.sleep(wait_time)
                                            lost_gems = int(p['gem'] * .25)
                                            p['gem'] = int(p['gem'] * .75)

                                            await message.channel.send("*{} died and lost {} :gem:*"
                                                                       .format(message.author.mention, lost_gems))
                                            p['hp'] = p['max_hp']  # resetting to full hp after death
                                            with open('./resources/battle/log.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                            someone_died = 1
                                            return
                                        await asyncio.sleep(wait_time)

                        elif msg.content.lower() == 'run':
                            escape = [
                                ':man_running: {} got away!'.format(message.author.mention),
                                ':man_running: {} ran away!'.format(message.author.mention),
                                ':man_running: {} barely escaped!'.format(message.author.mention),
                                ':man_running: {} ran like a {}!'.format(message.author.mention, generate_insult())
                            ]
                            response = random.choice(escape)
                            await message.channel.send(response)
                        else:
                            await message.channel.send('{} did not choose fight or run! The fight was cancelled'.format(
                                message.author.mention))

                if len(message.content.split()) >= 2:
                    # Gems check
                    if 'gems' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                await message.channel.send(
                                    '{} has **{}** :gem:'.format(message.author.mention, p['gem']))

                    # HP check
                    elif 'hp' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                await message.channel.send(
                                    '{} has **{}**/**{}** HP'.format(message.author.mention, p['hp'], p['max_hp']))
                    # Level check
                    elif 'lvl' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                if p['lvl'] >= max_player_level:
                                    await message.channel.send("{}\n```cs\nLEVEL {}```"
                                                               .format(message.author.mention, max_player_level))
                                else:
                                    await message.channel.send("{}\n```cs\nLEVEL {}```"
                                                               .format(message.author.mention, p['lvl']))

                    # Sword check
                    elif 'sword' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                for l in p['inv']:
                                    await message.channel.send("{} has {}{}"
                                                               .format(message.author.mention, l['modifier'],
                                                                       l['sword']))
                    # TODO add asyncio.sleep in between messages: wait_time
                    # Sword crafting
                    elif 'craft' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                if p['gem'] < crafting_cost:
                                    await message.channel.send("{} doesn't have enough :gem:"
                                                               .format(message.author.mention))
                                    return
                                else:
                                    await message.channel.send(
                                        "{}, crafting costs {} :gem:\nDo you wish to continue? **yes**/**no**"
                                            .format(message.author.mention, crafting_cost))

                                    def check(msg):
                                        return msg.author == message.author

                                    try:
                                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                    except asyncio.TimeoutError:
                                        await message.channel.send(
                                            "{} didn't respond in time, you didn't craft anything:zzz:"
                                                .format(message.author.mention))
                                    else:
                                        if msg.content.lower() == 'yes':
                                            p['gem'] = p['gem'] - crafting_cost
                                            with open('./resources/battle/log.json', 'w') as f:
                                                json.dump(contents, f, indent=4)
                                            r_modifier = random.choices(modifiers, modifiers_weight)
                                            r_sword = random.choices(swords, swords_weight)
                                            await message.channel.send(
                                                "{} made {}{}".format(message.author.mention, r_modifier[0].name,
                                                                      r_sword[0].name))

                                            for p in contents['players']:
                                                if '{}'.format(message.author) == '{}'.format(p['name']):
                                                    for l in p['inv']:
                                                        await message.channel.send(
                                                            "{}, you can only have *one* sword. Do you want to sell your: "
                                                            "{}{}**yes**/**no** "
                                                                .format(message.author.mention, l['modifier'],
                                                                        l['sword']))

                                            def check(msg):
                                                return msg.author == message.author

                                            try:
                                                msg = await client.wait_for('message', check=check,
                                                                            timeout=timeout_time)
                                            except asyncio.TimeoutError:
                                                await message.channel.send(
                                                    "{} didn't respond in time, you lost the sword!:zzz:"
                                                        .format(message.author.mention))
                                            else:
                                                for p in contents['players']:
                                                    if '{}'.format(message.author) == '{}'.format(p['name']):
                                                        for l in p['inv']:

                                                            if msg.content.lower() == 'yes':
                                                                old_modifier = l['modifier']
                                                                old_sword = l['sword']
                                                                l['modifier'] = r_modifier[0].name
                                                                l['sword'] = r_sword[0].name
                                                                sell_value = 0
                                                                for m in modifiers:
                                                                    if old_modifier in str(m.name):
                                                                        sell_value = sell_value + m.price
                                                                for s in swords:
                                                                    if old_sword in str(s.name):
                                                                        sell_value = sell_value + s.price
                                                                await message.channel.send(
                                                                    "{}, you sold your {}{} for {} :gem:\n Now you have {}{}"
                                                                        .format(message.author.mention,
                                                                                old_modifier, old_sword, sell_value,
                                                                                l['modifier'],
                                                                                l['sword']))
                                                                with open('./resources/battle/log.json', 'w') as f:
                                                                    json.dump(contents, f, indent=4)

                                                            elif msg.content.lower() == 'no':
                                                                await message.channel.send(
                                                                    "{}, you kept your {}{}"
                                                                        .format(message.author.mention, l['modifier'],
                                                                                l['sword']))
                                        elif msg.content.lower() == 'no':
                                            await message.channel.send(
                                                "{} didn't craft anything.".format(message.author.mention))
                                        else:
                                            await message.channel.send(
                                                "{} didn't answer **yes** or **no**.".format(message.author.mention))

                    # Items check
                    elif 'items' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                if str(p['items']) == '[]':
                                    await message.channel.send(
                                        "{} has no items in their inventory!".format(message.author.mention))
                                    return
                                else:
                                    v = 0
                                    player_item_list = []
                                    player_item_list_hp = []
                                    player_item_list_sell = []
                                    for g in p['items']:
                                        player_item_list.append(p['items'][v]['name'])
                                        for i in items:
                                            if str(p['items'][v]['name']) in str(i.name):
                                                player_item_list_hp.append(i.heal)
                                                player_item_list_sell.append(i.sell_price)
                                        player_item_list.append(
                                            ' - **' + str(player_item_list_hp[v]) + '** :sparkling_heart:')
                                        player_item_list.append(' - **' + str(player_item_list_sell[v]) + '** :gem:\n')
                                        if v < max_items:
                                            v = v + 1
                                    player_item_list_msg = "".join(map(str, player_item_list))
                                    await message.channel.send(
                                        '{} has the following items: \n{}'.format(message.author.mention,
                                                                                  player_item_list_msg))

                    # Shop
                    elif 'shop' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                # loading shop log
                                if not os.path.isfile('./resources/battle/shop.json'):
                                    # if file not found, make log.json with create_json_player function
                                    create_json_shop()
                                    await message.channel.send('Shop.json has been created. Please try again.')
                                else:
                                    with open('./resources/battle/shop.json') as shop_log:
                                        if len(message.content.split()) == 3:
                                            split = message.content.split()[2].lower()
                                            if 'buy' in str(split):
                                                await message.channel.send(
                                                    "{}, tell me which **item** you want to *buy* after the command!".format(message.author.mention))
                                            elif 'sell' in str(split):
                                                await message.channel.send(
                                                    "{}, tell me which **item** you want to *sell* after the command!".format(message.author.mention))
                                            else:
                                                await message.channel.send(
                                                    "{}, you can only **buy**/**sell** in the shop.".format(message.author.mention))
                                        elif len(message.content.split()) > 3:
                                            split = message.content.split()[2].lower()
                                            split_item = message.content.split()[3].lower()
                                            if 'buy' in str(split):
                                                contents = json.load(shop_log)
                                                if str(contents) == '' or str(contents) == '[]':
                                                    create_json_shop()
                                                    await message.channel.send(
                                                        'Shop.json was empty and has been fixed. Please try again.')
                                                else:
                                                    for c in contents['shop_items']:
                                                        if str(split_item) in str(c).lower():
                                                            for i in items:
                                                                if str(split_item) in str(i.name).lower():
                                                                    print(i.name)
                                                            # todo immediately create new random entry in shop.json
                                                        else:
                                                            await message.channel.send("{}, that item isn't in the shop!").format(message.author.mention)
                                            elif 'sell' in str(split):
                                                if str(p['items']) == '[]':
                                                    await message.channel.send(
                                                        "{} has no items in their inventory!".format(
                                                            message.author.mention))
                                                    return
                                                else:
                                                    for v in range(max_items):
                                                        for g in p['items']:
                                                            # If item entered does not exist in item list
                                                            if str(split_item) not in str(item_list).lower():
                                                                await message.channel.send(
                                                                    "{}, that item does not exist!".format(
                                                                        message.author.mention))
                                                                return
                                                            # If item entered DOES exist but not in player inv
                                                            else:
                                                                if str(split_item) not in str(
                                                                        p['items']).lower():
                                                                    await message.channel.send(
                                                                        "{}, that item isn't in your inventory!".format(
                                                                            message.author.mention))
                                                                    return
                                                            # If item entered is found in player inventory
                                                            if str(split_item) in str(p['items']).lower():
                                                                for i in items:
                                                                    if str(split_item) in str(i.name).lower():
                                                                        await message.channel.send(
                                                                            "{} sold the {} and received {} :gem:".format(
                                                                                message.author.mention, i.name,
                                                                                i.sell_price))
                                                                        del (p['items'][v])
                                                                        p['gem'] = p['gem'] + i.sell_price
                                                                        with open('./resources/battle/log.json',
                                                                                  'w') as f:
                                                                            json.dump(contents, f, indent=4)
                                                                        return
                                                                        # TODO test this

                                        else:
                                            contents = json.load(shop_log)
                                            if str(contents) == '' or str(contents) == '[]':
                                                create_json_shop()
                                                await message.channel.send(
                                                    'Shop.json was empty and has been fixed. Please try again.')
                                            else:
                                                for c in contents['shop_items']:
                                                    # Generate new items in shop if empty
                                                    if str(c['items']) == '[]':
                                                        await message.channel.send(
                                                            "Shop now has new items! Please try again.")
                                                        shop_list = []
                                                        for s in range(max_shop_items):
                                                            r_item = random.choices(items, items_weight)
                                                            shop_list.append(r_item)
                                                        for h in shop_list:
                                                            c['items'].append({
                                                                'name': '{}'.format(h[0].name)
                                                            })
                                                        with open('./resources/battle/shop.json', 'w') as f:
                                                            json.dump(contents, f, indent=4)
                                                        return

                                                    if len(p['items']) < max_items:
                                                        shop_item_list = []
                                                        shop_item_list_hp = []
                                                        shop_item_list_buy = []
                                                        for l in c['items']:
                                                            for i in items:
                                                                if str(l['name']).lower() in str(i.name).lower():
                                                                    shop_item_list.append(i.name)
                                                                    shop_item_list_hp.append(i.heal)
                                                                    shop_item_list_buy.append(i.buy_price)
                                                        shop_item_list_msg = []
                                                        for v in range(max_shop_items):
                                                            shop_item_list_msg.append(
                                                                str(shop_item_list[v]) + ' - **' + str(
                                                                    shop_item_list_hp[
                                                                        v]) + '** :sparkling_heart: - **' + str(
                                                                    shop_item_list_buy[v]) + '** :gem:')

                                                        item_msg = "\n".join(map(str, shop_item_list_msg))
                                                        await message.channel.send(
                                                            "{}, Items in shop: \n{}".format(message.author.mention,
                                                                                             item_msg))
                                                        return
                                                    else:
                                                        await message.channel.send(
                                                            "{} can't go above the item limit! *(You have {} items)*".format(
                                                                message.author.mention, max_items))
                                                        return

                    # Eat (food items)
                    elif 'eat' in '{}'.format(message.content.lower()):
                        for p in contents['players']:
                            if '{}'.format(message.author) == '{}'.format(p['name']):
                                if len(message.content.split()) > 2:
                                    split = message.content.split()[2].lower()
                                    # If item inventory is empty
                                    if str(p['items']) == '[]':
                                        await message.channel.send(
                                            "{} has no items in their inventory!".format(message.author.mention))
                                        return
                                    else:
                                        for v in range(max_items):
                                            for g in p['items']:
                                                # If item entered does not exist in item list
                                                if str(split) not in str(item_list).lower():
                                                    await message.channel.send(
                                                        "{}, that item does not exist!".format(message.author.mention))
                                                    return
                                                # If item entered DOES exist but not in player inv
                                                else:
                                                    if str(split) not in str(
                                                            p['items']).lower():
                                                        await message.channel.send(
                                                            "{}, that item isn't in your inventory!".format(
                                                                message.author.mention))
                                                        return
                                                # If item entered is found in player inventory
                                                if str(split) in str(p['items']).lower():
                                                    for i in items:
                                                        if str(split) in str(i.name).lower():
                                                            if p['hp'] is not p['max_hp']:
                                                                await message.channel.send(
                                                                    "{} used the {}, it healed {} HP".format(
                                                                        message.author.mention, i.name, i.heal))
                                                                p['hp'] = p['hp'] + i.heal
                                                                if p['hp'] > p['max_hp']:
                                                                    p['hp'] = p['max_hp']
                                                                del (p['items'][v])
                                                                with open('./resources/battle/log.json', 'w') as f:
                                                                    json.dump(contents, f, indent=4)
                                                                return
                                                                # IMPORTANT 'return' --> uses only one apple
                                                                # when there are multiple in inventory
                                                                # Return at the end keeps the FOR from looping!
                                                            else:
                                                                await message.channel.send(
                                                                    "{} is already at *max* HP!".format(
                                                                        message.author.mention))
                                                                return
                                else:
                                    await message.channel.send("{}, please enter which *food item* you want "
                                                               "to use *after the command*".format(
                                        message.author.mention))

                    # Test
                    elif 'test' in '{}'.format(message.content.lower()):
                        print('test')

                    elif 'help' in '{}'.format(message.content.lower()):
                        response = "{}, after the command you can use: " \
                                   "**gems**, **hp**, **lvl**, **shop**, **items**, **eat**, **craft** or **sword**".format(
                            message.author.mention)
                        await message.channel.send(response)

                    else:
                        response = "{}, after the command you can use: " \
                                   "**gems**, **hp**, **lvl**, **shop**, **items**, **eat**, **craft** or **sword**".format(
                            message.author.mention)
                        await message.channel.send(response)

# Shop: buy <-> sell
# Armor items with received_damage modifier
# Fun items
# Shop or trade system to sell-buy items and swords
# Blackjack
