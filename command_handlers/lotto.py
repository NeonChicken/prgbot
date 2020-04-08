import random

# Take any number of arguments and return one of them randomly.
def respond(message):
    if len(message.content.split()) < 2:
        return "I can't choose anything if you don't give me any options!"
    options = message.content.split()[1:]
    return random.choice(options)
