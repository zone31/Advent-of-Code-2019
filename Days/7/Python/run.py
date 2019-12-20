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
        self.input_queue = None
        self.program = program
        self.program_queue = Queue()
        self.halted = Value('b', False)
        self.running_lock = Lock()
        self.reset_lock = Lock()
        self.got_input_lock = Lock()
        self.input_submitted = Lock()

    def set_input_queue(self,queue):
        """
        Sets the input queue, so we can reference it from
        an outside object
        """
        self.input_queue = queue

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
        # for halt
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
        def get(mode,value):
            """
            Gets the data based on:
            * mode 0: position          d[x]
            * mode 1: intermediate      x
            """
            if mode == 0:
                return program[value]
            elif mode == 1:
                return value

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

            program = self.program.copy()
            ptr = 0
            self.running_lock.acquire()
            while True:
                # Unpack the instruction and load/save registers
                # Append zeroes for default args
                arg = "0000" + str(program[ptr])
                inst = int(arg[-2]+arg[-1])
                param = [int(d) for d in arg[:-2]]
                param.reverse()

                if inst == 1: # Add
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,_   = param[:3]
                    program[ret] = get(A,a) + get(B,b)
                    ptr += 4

                elif inst == 2: # Multiply
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,_   = param[:3]
                    program[ret] = get(A,a) * get(B,b)
                    ptr += 4

                elif inst == 3: # Get input. Special case, halt if string received("HALT")
                    self.got_input_lock.release()
                    self.input_submitted.acquire()

                    ret = program[ptr+1]
                    data = self.input_queue.get()
                    program[ret] = data
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
                    ptr += 2

                elif inst == 5: # Jump if true
                    comp,ret = program[ptr+1:ptr+3]
                    COMP,RET = param[:2]
                    if get(COMP,comp) != 0:
                        ptr = get(RET,ret)
                    else:
                        ptr += 3

                elif inst == 6: # Jump if false
                    comp,ret = program[ptr+1:ptr+3]
                    COMP,RET = param[:2]
                    if get(COMP,comp) == 0:
                        ptr = get(RET,ret)
                    else:
                        ptr += 3

                elif inst == 7: # less than
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,_   = param[:3]
                    if get(A,a) < get(B,b):
                        program[ret] = 1
                    else:
                        program[ret] = 0
                    ptr += 4

                elif inst == 8: # equals
                    a,b,ret = program[ptr+1:ptr+4]
                    A,B,_   = param[:3]
                    if get(A,a) == get(B,b):
                        program[ret] = 1
                    else:
                        program[ret] = 0
                    ptr += 4

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
    Generate all permutations of the phases, and bruteforce
    The functions seems to be linear, so there may be a way to find the
    max without bruteforce
    """
    # Setup the Intcode processes
    input_queue = Queue()
    p1 = IntcodeProcess("Process 1",d.copy())
    p2 = IntcodeProcess("Process 2",d.copy())
    p3 = IntcodeProcess("Process 3",d.copy())
    p4 = IntcodeProcess("Process 4",d.copy())
    p5 = IntcodeProcess("Process 5",d.copy())
    p1.set_input_queue(input_queue)
    p2.set_input_queue(p1.output_queue)
    p3.set_input_queue(p2.output_queue)
    p4.set_input_queue(p3.output_queue)
    p5.set_input_queue(p4.output_queue)
    process = [p1,p2,p3,p4,p5]
    output_queue = p5.output_queue

    # Start the threads
    [p.start() for p in process]

    permutations = itertools.permutations([0,1,2,3,4])
    max_signal = 0
    for permutation in permutations:
        # Load the phases
        for p,phase in zip(process,permutation):
            p.safe_insert_input(phase)

        # Insert the value
        p1.safe_insert_input(0)

        # Get the output
        signal = output_queue.get()

        # Reset the treads
        [p.reset() for p in process]

        # Compare if this is better
        if signal > max_signal:
            max_signal = signal

    # Stop the treads
    [p.shutdown() for p in process]

    return max_signal

def solver_2star(d):
    """
    Do nearly the same as the other star, but wait for all prosesses to halt,
    and wire them in a loop
    """
    # Setup the Intcode processes
    p1 = IntcodeProcess("Process 1",d.copy())
    p2 = IntcodeProcess("Process 2",d.copy())
    p3 = IntcodeProcess("Process 3",d.copy())
    p4 = IntcodeProcess("Process 4",d.copy())
    p5 = IntcodeProcess("Process 5",d.copy())
    p1.set_input_queue(p5.output_queue)
    p2.set_input_queue(p1.output_queue)
    p3.set_input_queue(p2.output_queue)
    p4.set_input_queue(p3.output_queue)
    p5.set_input_queue(p4.output_queue)
    process = [p1,p2,p3,p4,p5]
    output_queue = p5.output_queue
    input_queue = p1.input_queue

    # Start the threads
    [p.start() for p in process]

    permutations = itertools.permutations([5,6,7,8,9])
    max_signal = 0
    for permutation in permutations:
        # Load the phases
        for p,phase in zip(process,permutation):
            p.safe_insert_input(phase)

        # Insert the value
        p1.safe_insert_input(0)

        # Wait for all processes to halt
        [p.wait_for_halt() for p in process]

        # Get the output
        signal = output_queue.get()

        # Reset the treads
        [p.reset() for p in process]

        # Compare if this is better
        if signal > max_signal:
            max_signal = signal

    # Stop the treads
    [p.shutdown() for p in process]

    return max_signal
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