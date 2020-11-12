#!/usr/bin/python3

import time
import random
import tty
import termios
import sys
import select

DIR_DICT = {"\x1b[A":"UP", "\x1b[B":"DOWN", "\x1b[D":"LEFT", "\x1b[C":"RIGHT"}
OLD_DIR_DICT = DIR_DICT.copy()

CELL_HT = 15
CELL_WD = 25

BOUNDARY_CHAR = "\033[0;43m \033[0;39m"
FLOOR_CHAR = "\033[0;39m.\033[0;39m"
SNAKE_CHAR = "\033[1;32m#\033[0;39m"
FOOD1_CHAR = "\033[1;36m*\033[0;39m"
FOOD2_CHAR = "\033[1;36m$\033[0;39m"
MAGIC_CHAR = "\033[1;35m?\033[0;39m"
FOOD2_PROB = 0.3
MAGIC_PROB = 0.17


def isBoundary(x,y):
    if (x == 0 or y == 0 or x == CELL_WD-1 or y == CELL_HT-1):
        return True
    else:
        return False

def inputExists():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

SNAKE = [(3,1), (2,1), (1,1)]
SNAKE_LEN = 3
SNAKE_DIR = "RIGHT"
SNAKE_DEAD = False

SCORE = 0

STEP_DUR = 0.25
FOOD1S = []
FOOD2S = []
MAGICS = []

def stockFood():
    if len(FOOD1S) == 0:
        FOOD1S.append(random.choice([(x,y) for x in range(1,CELL_WD-1) for y in range(1,CELL_HT-1) if (x,y) not in SNAKE\
                        and (x,y) not in FOOD1S\
                        and (x,y) not in FOOD2S\
                        and (x,y) not in MAGICS]))
        if random.random() < FOOD2_PROB:
            FOOD2S.append(random.choice([(x,y) for x in range(1,CELL_WD-1) for y in range(1,CELL_HT-1)\
                            if (x,y) not in SNAKE\
                            and (x,y) not in FOOD1S\
                            and (x,y) not in FOOD2S\
                            and (x,y) not in MAGICS]))
        if random.random() < MAGIC_PROB:
            MAGICS.append(random.choice([(x,y) for x in range(1,CELL_WD-1) for y in range(1,CELL_HT-1)\
                            if (x,y) not in SNAKE\
                            and (x,y) not in FOOD1S\
                            and (x,y) not in FOOD2S\
                            and (x,y) not in MAGICS]))


############################################################################################################################################################
#### ALL MAGIC FUNCTIONS

def change_snake_color():
    global SNAKE_CHAR
    SNAKE_CHAR = "\033[{};{}m#\033[0;39m".format(random.choice([0,1]), random.choice(range(31,40)))

def boost_snake_speed():
    global STEP_DUR
    STEP_DUR *= 2/3

def lower_snake_speed():
    global STEP_DUR
    STEP_DUR *= 3/2

def inhibit_snake():
    global SNAKE_LEN
    SNAKE_LEN //= 2

def shrink_snake():
    global SNAKE
    global SNAKE_LEN
    if SNAKE_LEN > 1:
        SNAKE = SNAKE[:SNAKE_LEN//2]
        SNAKE_LEN //= 2
    else:
        pass

def double_snake():
    global SNAKE_LEN
    SNAKE_LEN *= 2

def create_food2():
    global FOOD2S
    count = random.choice(range(3,8))
    for i in range(count):
            FOOD2S.append(random.choice([(x,y) for x in range(1,CELL_WD-1) for y in range(1,CELL_HT-1)\
                            if (x,y) not in SNAKE\
                            and (x,y) not in FOOD1S\
                            and (x,y) not in FOOD2S\
                            and (x,y) not in MAGICS]))

def change_snake_into_food():
    global SNAKE
    global SNAKE_LEN
    temp = random.choice(range(1,len(SNAKE)))
    SNAKE_LEN = temp
    temp2 = SNAKE[temp:]
    SNAKE = SNAKE[:temp]
    FOOD1S.extend([x for x in temp2 if random.random() < 0.5])

def change_floor_color():
    global FLOOR_CHAR
    FLOOR_CHAR = "\033[{};{}m.\033[0;39m".format(random.choice([0,1]), random.choice(range(31,40)))

def change_boundary_color():
    global BOUNDARY_CHAR
    BOUNDARY_CHAR = "\033[{};{}m \033[0;39m".format(random.choice([0,1]), random.choice(range(41,47)))

def make_snake_invisible():
    global SNAKE_CHAR
    SNAKE_CHAR = " "



MAGIC_FUNCS = [double_snake, inhibit_snake, change_snake_color, boost_snake_speed, lower_snake_speed, create_food2, change_snake_into_food, change_floor_color,
                change_boundary_color, make_snake_invisible]
############################################################################################################################################################


OLD_SETTINGS = termios.tcgetattr(sys.stdin)
def move(x, y):
    global SNAKE
    global SNAKE_LEN
    global SCORE

    if SNAKE_DIR == "UP":
        SNAKE_NEXT = (x, y-1)
    elif SNAKE_DIR == "LEFT":
        SNAKE_NEXT = (x-1, y)
    elif SNAKE_DIR == "DOWN":
        SNAKE_NEXT = (x, y+1)
    elif SNAKE_DIR == "RIGHT":
        SNAKE_NEXT = (x+1, y)

    if SNAKE_NEXT in FOOD1S:
        FOOD1S.remove(SNAKE_NEXT)
        SNAKE_LEN += 1
        SCORE += 1

    if SNAKE_NEXT in FOOD2S:
        FOOD2S.remove(SNAKE_NEXT)
        SNAKE_LEN += 2
        SCORE += 2

    if SNAKE_NEXT in MAGICS:
        MAGICS.remove(SNAKE_NEXT)
        a = random.choice(MAGIC_FUNCS)
        a()

    if not isBoundary(*SNAKE_NEXT) and SNAKE_NEXT not in SNAKE:
        SNAKE.insert(0, SNAKE_NEXT)
    else:
        print("\033[{}B".format(CELL_HT+2))
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, OLD_SETTINGS)
        quit()
        #SNAKE_DEAD = True

    while len(SNAKE) > SNAKE_LEN:
        SNAKE.pop()


tty.setcbreak(sys.stdin.fileno())


##############  GAME  STARTS  HERE  ##########################################################################
print(u"\u00A9", "Pranav Minasandra 2020, Max Planck Institute of Animal Behaviour\npminasandra.github.io\n")

while True:
    try:
        if not SNAKE_DEAD:
            print()
            stockFood()
            for y in range(CELL_HT):
                for x in range(CELL_WD):

                    if isBoundary(x,y):
                        print(BOUNDARY_CHAR, end = "")
                    elif (x,y) in SNAKE:
                        print(SNAKE_CHAR, end="")
                    elif (x,y) in FOOD1S:
                        print(FOOD1_CHAR, end="")
                    elif (x,y) in FOOD2S:
                        print(FOOD2_CHAR, end="")
                    elif (x,y) in MAGICS:
                        print(MAGIC_CHAR, end="")
                    else:
                        print(FLOOR_CHAR, end="")
                print()
            #print("\r\033[1;43;30mSCORE:\t{}".format(SCORE))
            print()

            time.sleep(STEP_DUR)
            move(*SNAKE[0])
            print("SCORE: {} | LENGTH: {}\033[{}A".format(SCORE, SNAKE_LEN, CELL_HT+3))

            if inputExists():
                SNAKE_DIR = DIR_DICT[sys.stdin.read(3)]
        else:
            break

    except KeyboardInterrupt:
        print("\033[{}B".format(CELL_HT+2))
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, OLD_SETTINGS)
        quit()
    except SystemExit and ValueError:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, OLD_SETTINGS)
        quit()
        
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, OLD_SETTINGS)
quit()

