#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import sys
from collections import defaultdict
from random import randint
import time


#****************** CSP class to hold all the values ******************

class CSP():
    
    #To keep track of all the variables needed
    def __init__(self, variables, domains, neighbors, num_colors):
        self.variables = variables #initialize values
        self.domains = domains
        self.neighbors = neighbors
        self.current_domains = None
        self.num_colors = num_colors
        
#****************** fucntion that implements min conflict algorithm ****************** 

def minimum_conflicts(csp, max_steps):
    
    csp.current = current = {}
    
    for variable in csp.variables: #an initial complete assignment for csp, assigning minimum conflict value which is still a random assignment
        value = minimum_conflicts_value(csp, variable, current)
        current[variable] = value

    for x in range(max_steps): #setting maximum number of steps
        if time.time() - start_time > 60:
            return "No answer"
            
        if max_steps > 100000: #introducing more randomness by changing values of some variables to random vales to avoid getting stuck in minima
            assign_random_values(current, csp.num_colors)  
            
        conflicted = conflicted_variable(csp, current) #list of conflicted variables
        #print (conflicted)
        if not conflicted: #stop when there are no conflicts
            print ("############ Steps taken to reach solution: ", x)
            return current
        variable = random.choice(conflicted) #randomly chosen conflicted variable to avoid repetition
        value = minimum_conflicts_value(csp, variable, current) #value for variable that minimized conflicts
        current[variable] = value

    return None


#****************** fucntion to get conflited variables ******************    

def conflicted_variable(csp, current):
    conflicted = list()
    for variable in csp.variables:
        if num_conflicts(csp, variable, current[variable], current) > 0:
            conflicted.append(variable)
    return conflicted
            
            
def num_conflicts(csp, variable, value, assignment):
    conflicts = 0
    for v in csp.neighbors[variable]:
        if v in assignment and not constraints(variable, value, v, assignment[v]):
            conflicts += 1   
    return conflicts

#****************** function to get value with minimum conflicts ******************    

def minimum_conflicts_value(csp, variable, current):
    items = list(csp.domains[variable])
    random.shuffle(items) #shuffling the items in the list
    return min(items, key=lambda value: num_conflicts(csp, variable, value, current))

    
#****************** create domain for every variable ******************

def create_domains(variables, colors):
    domains = {}
    for variable in variables:
        domains[variable] = colors
    return domains
                        
            
#****************** neighbors cannot have the same color ****************** 
  
def constraints(X, x, Y, y):
    return x != y
    
#****************** fucntion to get conflited variables ******************   

def assign_random_values(current, num_colors):
    num_keys = len(current.items())
    num_times = int(num_keys/num_colors)
    for x in range(num_times):
        random_variable = randint(0, num_keys-1) #choose a random variable
        random_value = randint(0, num_colors-1) #choose a random value for the variable
        current[random_variable] = random_value
        

#****************** function to read input file and formulate the CSP problem ******************

def read_input_file(input_file):
    
    file = open(input_file)
    lines = file.readlines()
    file.close()
    [N, M, K] = lines[0].strip().split()
    [num_variables, num_constraints, num_colors] = [int(N), int(M), int(K)] #reading input specifics
    csp_dict = {} #dict representation for the graph
    csp_dict = defaultdict(set)
        
    colors = list()
    for color in range(num_colors):
        colors.append(color)
        
    for edge in range(num_constraints):
        [u, v] = lines[edge + 1].strip().split()
        [var1, var2] = [int(u), int(v)]
        csp_dict[var1].add(var2) #edge from A to  means edge from B to A
        csp_dict[var2].add(var1)
       
    return [csp_dict, colors, num_variables] 


#****************** function to generate output file in the required format ******************

def write_output_file(solution, output_file):
    if solution is None or solution == "No answer":
        with open(output_file, 'a') as out:
            out.write("No answer") 
    else:
        color_list = list(solution.values())
        with open(output_file, 'a') as out:
            for color in color_list:
                out.write("%s\n" % color)         

    
#****************** main function ******************

def main(argv):
    args = list(argv)
    
    if len(args) < 3:
        print("You need to give 2 arguments to run this program: python minconflicts.py <input_file> <output_file>\n")
        return None
    else:
        input_file = args[1]
        output_file = args[2]

    [csp_dict, colors, num_variables] = read_input_file(input_file)
    csp = CSP(list(csp_dict.keys()), create_domains(list(csp_dict.keys()), colors), csp_dict, len(colors))
    
    print("\n################# Map coloring started using Min Conflicts #################\n")
    global start_time
    start_time = time.time() #capture the time when program starts
    solution = minimum_conflicts (csp, max_steps=1000000000)
    finish_time = time.time() #capture the time when program ends
    time_taken = finish_time - start_time #total time spent inside the min coflict function
    print("\n################# Total time taken to run ", time_taken)
    
    write_output_file(solution, output_file)
    
    
#****************** main ******************
if __name__ == "__main__":
    main(sys.argv)
    
    
#written by: Leena Shekhar