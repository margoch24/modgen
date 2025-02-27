import random
import time
from datetime import datetime, timedelta


def current_milli_time():
    return round(time.time() * 1000)


def get_random(maximum: int):
    random_number = random.random()
    multiplied = random_number * maximum
    return int(multiplied)
