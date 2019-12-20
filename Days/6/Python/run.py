#!/usr/bin/env python3
import sys
import math
from collections import namedtuple as t
######################Helping definitions##########################
Planet = t('Planet', [
    'name',
    'parent',
    'child'
])

Orbit = t('Orbit', [
    'center',
    'child'
])

Traversal = t('Traversal', [
        'seen',
        'depth'
    ])
#######################Helping functions###########################
def data_parser(filepath):
    """
    Parse the data by splitting the line by commas, and making input
    to ints
    """
    orbit_list = []
    with open(filepath, 'r') as f:
        for line in f:
            center,orbit = line.split(")")
            orbit_list.append(Orbit(center.rstrip(),orbit.rstrip()))
    return orbit_list

def generate_orbit_graph(orbit_list):
    """
    Generates an acrylic graph based on the orbits from input
    """
    # Return a dict with planet name as key, and
    orbit_graph = dict()
    for orbit in orbit_list:
        if orbit.center not in orbit_graph:
            orbit_graph[orbit.center] = Planet(orbit.center,[],[])
        if orbit.child not in orbit_graph:
            orbit_graph[orbit.child] = Planet(orbit.child,[],[])

        orbit_graph[orbit.center].child.append(orbit.child)
        orbit_graph[orbit.child].parent.append(orbit.center)

    return orbit_graph

def distance_between(planet_a,planet_b,orbit_graph,traversed = []):
    """
    Find the distance between two planets by orbital graph.
    """
    # If the planet has already been traversed, we terminate
    if planet_a.name in traversed or planet_b.name in traversed:
        return Traversal(False,0)

    # If the planet hits, we got a possible travel
    if planet_a.name == planet_b.name:
        return Traversal(True,0)

    # Find child
    for child in planet_a.child:
        t = traversed.copy()
        t.append(planet_a.name)
        travel = distance_between(orbit_graph[child],planet_b,orbit_graph,t)
        if travel.seen:
            return Traversal(True,travel.depth + 1)

    # Find parent
    for parent in planet_a.parent:
        t = traversed.copy()
        t.append(planet_a.name)
        travel = distance_between(orbit_graph[parent],planet_b,orbit_graph,t)
        if travel.seen:
            return Traversal(True,travel.depth + 1)

    return Traversal(False,0)

def total_orbits(orbit_graph):
    """
    Traverse the graph recursively, and save if the note has been seen,
    and the depth. Sum over all this for all planets
    """
    def travel(from_planet,to_planet):
        #print("-------------",(from_planet,to_planet))
        if from_planet.name == to_planet.name:
            return Traversal(True,0)

        if len(orbit_graph[from_planet.name]) == 0:
            return Traversal(False,0)

        temp = [travel(orbit_graph[x],to_planet) for x in orbit_graph[from_planet.name].child]
        result = list(filter(lambda x: x.seen, temp))
        result.sort(key = lambda x: x.depth)

        if result == []:
            return Traversal(False,0)
        return Traversal(True,result[0].depth + 1)

    return sum([travel(orbit_graph["COM"],orbit_graph[planet]).depth for planet in orbit_graph])
#########################Main functions############################
def solver_1star(d):
    """
    Generate the orbit graph, and count the orbits
    """
    orbit_graph = generate_orbit_graph(d)
    return total_orbits(orbit_graph)

def solver_2star(d):
    """
    Use the orbit graph, and traverse between the planets
    """
    orbit_graph = generate_orbit_graph(d)
    travel = distance_between(orbit_graph["YOU"],orbit_graph["SAN"],orbit_graph)
    return travel.depth - 2

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