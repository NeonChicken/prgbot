import random
import asyncio
import tensorflow as tf
import numpy as np
import magenta as mag

prefix = '!'

wait_time = 0.5
timeout_time = 20
min_seed = 0
max_seed = 1000

async def run(client, message):
    if len(message.content.split()) < 2:

        pass