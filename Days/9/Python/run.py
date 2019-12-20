#!/usr/bin/env python3
import sys
import math
import time
import itertools
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue, Value, Lock
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting the line by commas, and making input
    to ints
    """
    with open(filepath, 'r') as f:
        return [int(x) for x in f.readline().split(",")]

class IntcodeProcess(Process):
    """
    The IntcodeProcess Is A multiprocess class
    That have the ability to wait for input from a
    queue(Get input), and dump to a queue (Set input),
    And inspect the Intcode program when the process has halted
    """
    def __init__(self,name,program):
        super().__init__()
        self.name = name
        self.output_queue = Queue()
        self.input_queue = Queue()
        self.program = program
        self.program_queue = Queue()
        self.halted = Value('b', False)

        self.running_lock = Lock()
        self.reset_lock = Lock()
        self.got_input_lock = Lock()
        self.input_submitted = Lock()

    def shutdown(self):
        self.reset()
        self.halted.value = True
        self.join()

    def reset(self):
        """
        Stops and resets the processor if possible.
        Clears the internal queues and resets the program
        """
        # IF not halted, send HALT to input and wait
        # for a halt command
        if not self.is_halted():
            self.input_queue.put("HALT")
            self.wait_for_halt()

        # Clear the queues
        while not self.output_queue.empty():
            self.output_queue.get()
        while not self.input_queue.empty():
            self.input_queue.get()
        while not self.program_queue.empty():
            self.program_queue.get()

        # Set the halted status, and release the lock to run
        self.halted.value = False
        self.reset_lock.release()

    def wait_for_halt(self):
        """
        Will only pass if current program has halted, and needs reset
        """
        while not self.is_halted():
            self.running_lock.acquire()
            self.running_lock.release()

    def is_halted(self):
        """
        Returns if the program is halted or not
        """
        return self.halted.value

    def safe_insert_input(self,data):
        """
        Insert data safe into the process, and
        detect if it has been gobbled up
        """
        self.got_input_lock.acquire()
        self.input_queue.put(data)
        self.input_submitted.acquire()
        self.got_input_lock.release()
        self.input_submitted.release()

    def inspect_program(self):
        """
        Inspect the program after it has been halted
        """
        return self.program_queue.get()

    def run(self):
        """
        Run the program
        """
        # Internal helping function
        def get(mode,argument):
            """
            Gets the data based on:
            * mode 0: position          d[x]
            * mode 1: intermediate      x
            * mode 2: relative          d[x + relative_base]
            """
            extend_program(mode,argument)
            if mode == 0:
                return program[argument]
            elif mode == 1:
                return argument
            elif mode == 2:
                return program[argument+relative_base]

        def put(mode,argument,value):
            """
            Puts the data based on the mode, and extends the program size
            if needed
            """
            extend_program(mode,argument)
            #program[get(mode,argument)] = value
            if mode == 0:
                program[argument] = value
            elif mode == 1:
                print("WHHAAAATTT??!?!?")
            elif mode == 2:
                program[argument+relative_base] = value

        def extend_program(mode,argument):
            """
            Extends the program space based on the wanted arguments
            """
            size = 0
            if mode == 0:
                size = argument + 1
            if mode == 2:
                size = argument + relative_base + 1
            if size > len(program):
                program.extend([0] * (size - len(program) + 1))

        # Acquire the lock initially, since it is "inverse"
        self.got_input_lock.acquire()

        # Running loop
        while True:
            # Acquire the lock, so we know that we need to run
            self.reset_lock.acquire()

            # If the program already halted, we become ready to terminate
            # No more running from this point!
            if(self.is_halted()):
                break

            # Lock the running lock, indicating that the program is running
            self.running_lock.acquire()

            # Reset program, program pointer, and relative base
            program = self.program.copy()
            ptr = 0
            relative_base = 0

            while True:
                # Unpack the instruction and load/save registers
                # Append zeroes for default args
                arg = "0000" + str(program[ptr])
                inst = int(arg[-2]+arg[-1])
                param = [int(d) for d in arg[:-2]]
                param.reverse()
                #print(f"\n{inst} *{ptr} base:{relative_base} param:{param} program") #:\n{program}

                if inst == 1: # Add
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,RET = param[:3]
                    #print(f"Add {a=} {b=} {ret=} mode:{A=} {B=} {RET=}")
                    data = get(A,a) + get(B,b)
                    put(RET,ret,data)
                    ptr += 4

                elif inst == 2: # Multiply
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,RET   = param[:3]
                    #print(f"Mult {a=} {b=} {ret=} mode:{A=} {B=} {RET=}")
                    data = get(A,a) * get(B,b)
                    put(RET,ret,data)
                    ptr += 4

                elif inst == 3: # Get input. Special case, halt if string received("HALT")
                    self.got_input_lock.release()
                    self.input_submitted.acquire()

                    ret = program[ptr+1]
                    data = self.input_queue.get()
                    put(RET,ret,data)
                    #print(f"Get {ret=} {data=}")
                    ptr += 2

                    self.input_submitted.release()
                    self.got_input_lock.acquire()

                    # Halt program if Halt command is seen
                    if data == "HALT":
                        break

                elif inst == 4: # Save output
                    ret = program[ptr+1]
                    RET = param[0]
                    self.output_queue.put(get(RET,ret))
                    #print(f"Put {ret=} mode:{RET=} value {get(RET,ret)}")
                    ptr += 2

                elif inst == 5: # Jump if true
                    comp,ret = program[ptr+1:ptr+3]
                    COMP,RET = param[:2]
                    #print(f"Jump if true {comp=} {ret=} mode:{COMP=} {RET=}")
                    if get(COMP,comp) != 0:
                        ptr = get(RET,ret)
                    else:
                        ptr += 3

                elif inst == 6: # Jump if false
                    comp,ret = program[ptr+1:ptr+3]
                    COMP,RET = param[:2]
                    #print(f"Jump if false {comp=} {ret=} mode:{COMP=} {RET=}")
                    if get(COMP,comp) == 0:
                        ptr = get(RET,ret)
                    else:
                        ptr += 3

                elif inst == 7: # less than
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,RET = param[:3]
                    #print(f"Less than {a=} {b=} {ret=} mode:{A=} {B=} {RET=}")
                    if get(A,a) < get(B,b):
                        put(RET,ret,1)
                    else:
                        put(RET,ret,0)
                    ptr += 4

                elif inst == 8: # equals
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,RET = param[:3]
                    #print(f"Equals {a=} {b=} {ret=} mode:{A=} {B=} {RET=}")
                    if get(A,a) == get(B,b):
                        put(RET,ret,1)
                    else:
                        put(RET,ret,0)
                    ptr += 4

                elif inst == 9: # Append to relative_value
                    ret = program[ptr+1]
                    RET = param[0]
                    #print(f"Relative base {ret=} mode:{RET=}")
                    relative_base += get(RET,ret)
                    ptr += 2

                elif inst == 99: # Halt
                    break

                else: # Undefined inst, terminate
                    break

            # Save the program after it halted, and set halting status
            self.halted.value = True
            self.running_lock.release()
            self.program_queue.put(program)
#########################Main functions############################
def solver_1star(d):
    """
    Use the new and improved intcode process!
    """
    # Setup the Intcode processes
    p = IntcodeProcess("Process 1",d.copy())

    # Start it
    p.start()

    #Insert 1
    p.input_queue.put(1)

    #Wait for output
    res = p.output_queue.get()

    # shutdown intcodeProcess
    p.shutdown()

    # Return
    return res


def solver_2star(d):
    """
    """
    # Setup the Intcode processes
    p = IntcodeProcess("Process 1",d.copy())

    # Start it
    p.start()

    #Insert 2
    p.input_queue.put(2)

    #Wait for output
    res = p.output_queue.get()

    # shutdown intcodeProcess
    p.shutdown()

    # Return
    return res

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