#!/usr/bin/env python3
import sys
import math
from collections import namedtuple as t
######################Helping definitions##########################
Range = t('Range', [
    'start',
    'stop'
])
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting the line by commas, and making input
    to the char for dirrection, and int for the distance
    """
    with open(filepath, 'r') as f:
        range_from,range_to = f.readline().split("-")
        return Range(int(range_from),int(range_to))
#########################Main functions############################
def solver_1star(d):
    """
    Test the conditions for each number, and accumulate in a loop
    """
    counter = 0
    for number in range(d.start,d.stop):
        have_pair = False
        never_decrease = True
        last_seen_digit = -1
        for digit in [int(i) for i in str(number)]:

            # Test if it is a pair
            if last_seen_digit == digit:
                have_pair = True

            # Test if the number is not higer than last, terminate
            if last_seen_digit > digit:
                never_decrease = False

            # Set the last seen digit to this digit
            last_seen_digit = digit

        if have_pair and never_decrease:
            counter += 1

    return counter

def solver_2star(d):
    """
    Test the conditions for each number, and accumulate in a loop.
    Keep track if we see a pair
    """
    counter = 0
    for number in range(d.start,d.stop):
        never_decrease = True
        last_seen_digit = -1
        seen_pair = []
        pair = []

        for i,digit in enumerate([int(i) for i in str(number)]):

            # Test if it is a pair
            if last_seen_digit == digit:
                if digit in seen_pair:
                    if digit in pair:
                        pair.remove(digit)
                else:
                    seen_pair.append(digit)
                    pair.append(digit)

            # Test if the number is not higer than last, terminate
            if last_seen_digit > digit:
                never_decrease = False
                break

            # Set the last seen digit to this digit
            last_seen_digit = digit

        if never_decrease and len(pair) > 0:
            counter += 1

    return counter
##############################MAIN#################################
def main():
    """
    Run the program by itself, return a tuple of star1 and star2
    """
    input_source = "../input1.txt"
    d = data_parser(input_source)
    return (solver_1star(d),solver_2star(d))

if __name__ == "__main__":
    star1,star2 = main()
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == '1':
           print(star1)
        elif arg == '2':
           print(star2)
    else:
        print("Day 1 first star:")
        print(star1)
        print("Day 1 second star:")
        print(star2)