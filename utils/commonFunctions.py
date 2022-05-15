import random
def randomUserAgent(filename):
    with open(filename) as f:
        lines = f.readlines()

    return random.choice(lines).replace("\n","")