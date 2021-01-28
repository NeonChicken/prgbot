import random
import asyncio
import os

prefix = '!'

wait_time = 0.25
timeout_time = 20
input_limit = 10  # Limits the amount of seconds a player can generate (to prevent spam & crash)


# Procedural generation
# Kate Weeden
def generate_noise(width, height):
    noise_map = []
    # Populate a noise map with 0s
    for y in range(height):
        new_row = []
        for x in range(width):
            new_row.append(0)
        noise_map.append(new_row)

    top_of_range = 0
    bottom_of_range = 0
    for y in range(height):
        for x in range(width):
            if x == 0 and y == 0:
                continue
            if y == 0:  # If the current position is in the first row
                new_value = noise_map[y][x - 1] + random.randint(-1000, +1000)
            elif x == 0:  # If the current position is in the first column
                new_value = noise_map[y - 1][x] + random.randint(-1000, +1000)
            else:
                minimum = min(noise_map[y][x - 1], noise_map[y - 1][x])
                maximum = max(noise_map[y][x - 1], noise_map[y - 1][x])
                average_value = minimum + ((maximum - minimum) / 2.0)
                new_value = average_value + random.randint(-1000, +1000)
            noise_map[y][x] = new_value
            # check whether value of current position is new top or bottom
            # of range
            if new_value < bottom_of_range:
                bottom_of_range = new_value
            elif new_value > top_of_range:
                top_of_range = new_value
    # Normalises the range, making minimum = 0 and maximum = 1
    difference = float(top_of_range - bottom_of_range)
    for y in range(height):
        for x in range(width):
            noise_map[y][x] = (noise_map[y][x] - bottom_of_range) / difference
    return noise_map


# Alphabet
a = ord('a')
alph = [chr(i) for i in range(a, a + 26)]


# Procedural Generation
async def run(client, message):
    if len(message.content.split()) < 2:
        print('help')

    elif len(message.content.split()) >= 3:
        input_sec = int(message.content.split()[1])
        input_text = message.content.split()[2]
        if input_sec <= input_limit and input_sec >= 0:
            def gen_msg():
                noise = generate_noise(33, 33)
                temp_list = []
                msg = '```\n'
                for i in noise:
                    for u in i:
                        u = u * 10
                        if u == 10:
                            msg = msg + "{}".format(input_text)
                        elif u >= 6:
                            msg = msg + "'"
                            # msg = msg + "{}".format(random.choice(alph).upper())
                        elif u <= 4:
                            msg = msg + '.'
                            # msg = msg + "{}".format(random.choice(alph))
                        elif u == 0:
                            msg = msg + ','
                        else:
                            msg = msg + '·'  # gen letters of alphabet?
                msg = msg + '\n```'
                return msg

            final_msg = await message.channel.send(gen_msg())
            await final_msg.edit(content=gen_msg())
            for s in range(input_sec):
                await asyncio.sleep(wait_time)
                await final_msg.edit(content=gen_msg())
        elif input_sec > input_limit:
            filename = str(os.path.basename(__file__))
            commandname = filename.replace('.py', '')
            await message.channel.send("You can't **" + prefix + "{}** ".format(commandname) +
                                       "for more than {} seconds!".format(input_limit))
        else:
            await message.channel.send("That doesn't work!")
