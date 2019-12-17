#!/usr/bin/env python3
import sys
import math
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting the line by commas, and making input
    to ints
    """
    with open(filepath, 'r') as f:
        return [int(x) for x in f.readline().split(",")]

def intcode_runner(d):
    """
    See the input data as a tape, and move forward on the operations
    """
    ptr = 0
    while True:
        # Unpack the instruction and load/save registers
        inst,a,b,ret = d[ptr:ptr+4]
        if inst == 1:
            d[ret] = d[a] + d[b]
        elif inst == 2:
            d[ret] = d[a] * d[b]
        elif inst == 99:
            break
            pass
        ptr += 4
    return d[0]
#########################Main functions############################
def solver_1star(d):
    """
    Set the parameters as described in the assignment, nd run the intcode
    """
    d[1] = 12
    d[2] = 2
    intcode_runner(d)
    return d[0]

def solver_2star(d):
    """
    Iterate over the input space of range 0 to 100 in both varriables,
    and bruteforce for the target
    """
    target = 19690720
    for noun in range(100):
        for verb in range (100):
            e = d.copy()
            e[1] = noun
            e[2] = verb
            res = intcode_runner(e)
            if res == target:
                return 100 * noun + verb
##############################MAIN#################################
def main():
    """
    Run the program by itself, return a tuple of star1 and star2
    """
    input_source = "../input1.txt"
    # Make list, since the generator has to be used multiple times
    d1 = list(data_parser(input_source))
    # Copy it since we do inline manipulation
    d2 = d1.copy()
    return (solver_1star(d1),solver_2star(d2))

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