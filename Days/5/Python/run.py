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

def intcode_runner(data,input_list):
    """
    See the input data as a tape, and move forward on the operations
    Since instructions can have modes for their input reference, (position,intermediate)
    we parse them before hand
    """
    #Local helper functiton
    def get(mode,value):
        """
        Gets the data based on:
        * mode 0: position          d[x]
        * mode 1: intermediate      x
        """
        if mode == 0:
            return data[value]
        elif mode == 1:
            return value
    ptr = 0
    output_list = []
    while range(10):
        # Unpack the instruction and load/save registers
        # Append zeroes for default args
        arg = "0000" + str(data[ptr])
        inst = int(arg[-2]+arg[-1])
        param = [int(d) for d in arg[:-2]]
        param.reverse()

        if inst == 1: # Add
            a,b,ret = data[ptr+1:ptr+4]
            A,B,_   = param[:3]
            data[ret] = get(A,a) + get(B,b)
            ptr += 4

        elif inst == 2: # Multiply
            a,b,ret = data[ptr+1:ptr+4]
            A,B,_   = param[:3]
            data[ret] = get(A,a) * get(B,b)
            ptr += 4

        elif inst == 3: # Get input
            ret = data[ptr+1]
            data[ret] = input_list.pop(0)
            ptr += 2

        elif inst == 4: # Save output
            ret = data[ptr+1]
            RET = param[0]
            output_list.append(get(RET,ret))
            ptr += 2

        elif inst == 5: # Jump if true
            comp,ret = data[ptr+1:ptr+3]
            COMP,RET = param[:2]
            if get(COMP,comp) != 0:
                ptr = get(RET,ret)
            else:
                ptr += 3

        elif inst == 6: # Jump if false
            comp,ret = data[ptr+1:ptr+3]
            COMP,RET = param[:2]
            if get(COMP,comp) == 0:
                ptr = get(RET,ret)
            else:
                ptr += 3

        elif inst == 7: # less than
            a,b,ret = data[ptr+1:ptr+4]
            A,B,_   = param[:3]
            if get(A,a) < get(B,b):
                data[ret] = 1
            else:
                data[ret] = 0
            ptr += 4

        elif inst == 8: # equals
            a,b,ret = data[ptr+1:ptr+4]
            A,B,_   = param[:3]
            if get(A,a) == get(B,b):
                data[ret] = 1
            else:
                data[ret] = 0
            ptr += 4

        elif inst == 99: # Halt
            break
            pass

        else: # Undefined inst, terminate
            break
    return output_list

#########################Main functions############################
def solver_1star(d):
    """
    Set the parameters as described in the assignment, and run the intcode
    """
    output = intcode_runner(d,[1])
    return output[-1]

def solver_2star(d):
    """
    Set the parameters as described in the assignment, and run the intcode
    """
    output = intcode_runner(d,[5])
    return output[-1]

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