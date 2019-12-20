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
        return [int(x) for x in list(f.readline())]

def format_picture(width,height,data):
    """
    Return the picture as a nested list of format
    d[layer_id][y][x]
    """
    layers = []
    for layer_offset in range(0,len(data),width*height):
        image = []
        for height_offset in range(0,width*height,width):
            image.append(data[layer_offset+height_offset:layer_offset+height_offset+width])
        layers.append(image)
    return layers

def recursive_count(nested_list,target):
    """
    Look in a list, and check if it contains the target element.
    If another list is found, also count in that
    """
    total = 0
    for element in nested_list:
        if type(element) is list:
            total += recursive_count(element,target)
        elif element == target:
            total += 1
    return total
#########################Main functions############################
def solver_1star(d):
    """
    Simply recursively find the amounts of zeros in each picture
    """
    width = 25
    height = 6
    layers = format_picture(width,height,d)
    min_count, min_id = 9999, 0
    for id, layer in enumerate(layers):
        count = recursive_count(layer,0)
        if count < min_count:
            min_count = count
            min_id = id
    return recursive_count(layers[min_id],1) * recursive_count(layers[min_id],2)

def solver_2star(d):
    """
    """
    width = 25
    height = 6
    layers = format_picture(width,height,d)
    # Create the inital photo
    photo = [ [2] * width for _ in range(height)]
    for id in range(len(layers)):
        for x in range(width):
            for y in range(height):
                if photo[y][x] == 2:
                    photo[y][x] = layers[id][y][x]
    # Helping print to see the photo, Could be
    # done with some character recognition, but that would be overkill :)
    #
    # for line in photo:
    #     print(''.join([(lambda x: "X" if x==1 else " ")(x) for x in line]))

    # Return the image flattened as the input instread
    # Code is "CJZHR"
    return ''.join([str(item) for sublist in photo for item in sublist])


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