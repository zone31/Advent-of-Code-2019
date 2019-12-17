#!/usr/bin/env python3
import sys
import math
import matplotlib.pyplot as plt
from collections import namedtuple as t
######################Helping definitions##########################
Point = t('Point', [
    'x',
    'y'
])

Line = t('Line', [
    'type',
    'point',
    'move',
    'last'
])

Intersection = t('Intersection', [
    'point',
    'line_a',
    'line_b'
])
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting the line by commas, and making input
    to the char for dirrection, and int for the distance
    """
    with open(filepath, 'r') as f:
        wire1 = list([(x[0],int(x[1:])) for x in f.readline().split(",")])
        wire2 = list([(x[0],int(x[1:])) for x in f.readline().split(",")])
        return [wire1,wire2]

def plot_paths(line_list_list):
    """
    Plots a list of paths
    """
    fig, ax = plt.subplots()
    for line_list in line_list_list:
        X = [x.point.x for x in line_list]
        Y = [x.point.y for x in line_list]

        # append last
        last_line = line_list[-1]
        if last_line.type == "-":
            X.append(last_line.point.x + last_line.move)
            Y.append(last_line.point.y)
        else:
            X.append(last_line.point.x)
            Y.append(last_line.point.y + last_line.move)

        ax.plot(X, Y)

    ax.grid()
    ax.axis('equal')
    plt.show()

def manhattan_distance(point_a,point_b=Point(0,0)):
    return abs(point_a.x - point_b.x) + abs(point_a.y - point_b.y)

def between_numbers(a,b,c):
    """
    Helper function to retur if the number is between values
    """
    if a >= b:
        return a >= c >= b
    return b >= c >= a

def generate_line_paths(d):
    """
    Generates a set of paths based on the movement
    The line offsets:
          U(0,+)
    L(-,0)      R(+,0)
          D(0,-)
    The path structure
    ("-",(x,y),(move))
    where "-" is a horizontal line, and "|" is a vertical line, the point is the
    starting point, and move is how long the path is
    """
    ret =  []
    last_line = None
    last_point = Point(0,0)
    for dirrection,move in d:


        if dirrection == "U":
            this_point = Point(last_point.x, last_point.y + move)
            line = "|"

        if dirrection == "D":
            this_point = Point(last_point.x, last_point.y - move)
            line = "|"
            move = move * -1

        if dirrection == "R":
            this_point = Point(last_point.x + move, last_point.y)
            line = "-"

        if dirrection == "L":
            this_point = Point(last_point.x - move, last_point.y)
            line = "-"
            move = move * -1

        this_line = Line(line, last_point, move, last_line)
        last_line = this_line
        last_point = this_point
        ret.append(this_line)

    return ret

def intersections(line,line_list):
    """
    Return all intersection points
    """
    # Mirror x and y if we work in lines in the other direction
    x,y = 0,1
    if line.type == "|":
        x,y = 1,0

    # Mirror the cords
    pa_x, pa_y = line.point[x], line.point[y]

    # We filter out lines in the list that are not the correct line
    # dirrection for intersections.
    res = []
    for line_scope in filter(lambda a: a[0] != line.type, line_list):
        pb_x, pb_y = line_scope.point[x], line_scope.point[y]

        # point pa_x in the comparing line needs to be between point pb_x,
        # and the same needs to be true in the reverse
        if (between_numbers(pa_x,pa_x+line.move,pb_x) and
            between_numbers(pb_y,pb_y+line_scope.move,pa_y)):
            temp = (pb_x,pa_y)
            # Convert back to not mirrored system
            res.append(Intersection(Point(temp[x],temp[y]),line,line_scope))

    return res

def length_to_source(intersection):
    """
    Takes in an intersection, and gives the distance from the intersection point
    to the last seen wire
    """

    ret = 0
    lines = [intersection.line_a,intersection.line_b]
    for line in lines:
        # Calculate the intersection distance to first corner
        ret += manhattan_distance(intersection.point,line.point)

        # Iterate over the paths until it is null
        path = line.last
        while path != None:
            ret += abs(path.move)
            path = path.last

    return ret
#########################Main functions############################
def solver_1star(d):
    """
    Collisions between wires can only happen between vertical and
    horizontal paths. We can therefore limit the search set to only
    these pairs for each wire.
    """
    paths_1 = generate_line_paths(d[0])
    paths_2 = generate_line_paths(d[1])
    all_intersections = []
    for path in paths_1:
        inter = intersections(path,paths_2)
        if inter != []:
            all_intersections.extend(intersections(path,paths_2))

    # Sort the intersections by their manhattan distance
    all_intersections.sort( key=lambda x: manhattan_distance(x.point))

    # return the smallest, if the smallest is (0,0), exclude it
    best_intersection = all_intersections[0] if all_intersections[0].point != Point(0,0) else all_intersections[1]

    return manhattan_distance(best_intersection.point)

def solver_2star(d):
    """
    Repeat star1, but calculate the distance in each intersection
    """
    paths_1 = generate_line_paths(d[0])
    paths_2 = generate_line_paths(d[1])
    all_intersections = []
    for path in paths_1:
        inter = intersections(path,paths_2)
        if inter != []:
            all_intersections.extend(intersections(path,paths_2))

    # Find the length to the source for all intersection
    ret = []
    for intersection in all_intersections:
        ret.append(length_to_source(intersection))
    ret.sort()

    return ret[0]
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