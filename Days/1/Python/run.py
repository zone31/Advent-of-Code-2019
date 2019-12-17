#!/usr/bin/env python3
import sys
import math
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting each line into a string, and making
    each string into a number
    """
    d = [int(line) for line in open(filepath)]
    return (int(s) for s in d)

def iterative_fuel(d):
    """
    Take in an weight, add the current fuel cost, and iterate onto that
    until the accumulator is under 0
    """
    accumulator = d
    total = 0
    while True:
        accumulator = math.floor(accumulator / 3) - 2
        if accumulator < 0:
            return total
        total += accumulator
#########################Main functions############################
def solver_1star(d):
    """
    Run the function floor(x/3)-2 on all input, and sum it together
    """
    return sum([math.floor(x / 3) - 2 for x in d])

def solver_2star(d):
    """
    Find the needed fuel for all modules individually
    """
    return sum([iterative_fuel(x) for x in d])

##############################MAIN#################################
def main():
    """
    Run the program by itself, return a tuple of star1 and star2
    """
    input_source = "../input1.txt"
    # Make list, since the generator has to be used multiple times
    d = list(data_parser(input_source))
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