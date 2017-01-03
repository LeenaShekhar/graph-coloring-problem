#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict
import random
import time

#****************** CSP class to hold all the values ******************

class CSP():
    
    #To keep track of all the variables needed
    def __init__(self, variables, domains, neighbors):
        self.variables = variables #initialize values
        self.domains = domains
        self.neighbors = neighbors
        self.current_domains = None
        
        
#****************** function that implements dfsb plain ******************    

n_dfsb_calls = 0

def dfsb_plain(csp, assignment):
        global n_dfsb_calls
        
        if time.time() - start_time > 60: #terminating the program if time exceeds 1 min
            return None
            
        n_dfsb_calls += 1
            
        if len(assignment) == len(csp.variables): #if all variables assigned values
            print ("\n################# Number of calls needed to solve ", n_dfsb_calls)
            return assignment
            
        variable = select_unassigned_variable(assignment, csp) #select any one variable at a time
        
        for value in domain_colors(variable, assignment, csp):
            if num_conflicts(csp, variable, value, assignment) == 0:
                
                assignment[variable] = value
                if csp.current_domains is None:
                    csp.current_domains = {color: list(csp.domains[color]) for color in csp.variables}

                pair = []
                for color in csp.current_domains[variable]:
                    if color != value:
                        pair.append((variable, color))
                csp.current_domains[variable] = [value]
                result = dfsb_plain(csp, assignment)
                
                if result is not None:
                    return result
                for Z, z in pair:
                    csp.current_domains[Z].append(z)
                    
        if variable in assignment:
            del assignment[variable]
        return None    

        
#****************** function that implemets dfsb with variable and value ordering and AC3 ******************

n_dfsbpp_calls = 0
n_arcprune_calls = 0

def dfsb_plus_plus(csp, assignment):
        global n_dfsbpp_calls
        global n_arcprune_calls
        
        if time.time() - start_time > 60: #terminating the program if time exceeds 1 min
            return None
            
        n_dfsbpp_calls += 1
        if len(assignment) == len(csp.variables):
            print ("\n################# Number of calls needed to solve ", n_dfsbpp_calls, n_arcprune_calls)
            return assignment
            
        variable = MRV(assignment, csp)
        
        for value in LCV(variable, assignment, csp):
            if num_conflicts(csp, variable, value, assignment) == 0:
                
                assignment[variable] = value
                if csp.current_domains is None:
                    csp.current_domains = {color: list(csp.domains[color]) for color in csp.variables}
                
                pair = []
                for color in csp.current_domains[variable]:
                    if color != value:
                        pair.append((variable, color))
                csp.current_domains[variable] = [value]

                if arc_consistency(csp, variable, value, assignment, pair): #AC3
                    result = dfsb_plus_plus(csp, assignment)
                    if result is not None:
                        return result
                for Z, z in pair:
                    csp.current_domains[Z].append(z)
        if variable in assignment:
            del assignment[variable]
        return None    

        
#****************** function that implements AC3 ******************

def arc_consistency(csp, variable, value, assignment, removals):
    global n_arcprune_calls
    queue = [(X, variable) for X in csp.neighbors[variable]] #all arcs
    if queue is None:
        queue = [(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]] #add all arcs in csp to queue
    if csp.current_domains is None:
            csp.current_domains = {v: list(csp.domains[v]) for v in csp.variables}
    
    while queue:
        (Xi, Xj) = queue.pop() #remove first from te queue
        if remove_inconsistent_values(csp, Xi, Xj, removals):
            n_arcprune_calls += 1
            if not csp.current_domains[Xi]:
                return False
            for Xk in csp.neighbors[Xi]:
                if Xk != Xi:
                    queue.append((Xk, Xi)) #add affected arcs to queue
    return True
    
                

def remove_inconsistent_values(csp, Xi, Xj, removals):
    removed = False
    for x in csp.current_domains[Xi][:]:
        if all(not constraints(Xi, x, Xj, y) for y in csp.current_domains[Xj]):
            csp.current_domains[Xi].remove(x)
            if removals is not None:
                removals.append((Xi, x))
            removed = True #true iff we remove a value or inconsistency
    return removed
    

#****************** functions that implement variable ordering ******************

def MRV(assignment, csp):
    unassigned_variables = list()
    for variable in csp.variables:
        if variable not in assignment:
            unassigned_variables.append(variable)
    random.shuffle(unassigned_variables)
    return (min(unassigned_variables, key=lambda variable: num_legal_values(csp, variable, assignment)))
     
    
def num_legal_values(csp, variable, assignment):
    if csp.current_domains:
        return len(csp.current_domains[variable])
    else:
        legal = 0
        for value in csp.domains[variable]:
            if num_conflicts(csp, variable, value, assignment) == 0:
                legal += 1
        return legal
                             
def select_unassigned_variable(assignment, csp):
    for variable in csp.variables:
        if variable not in assignment:
            return variable
    
       
#****************** functions that implement value ordering ******************

def LCV(variable, assignment, csp):
    return sorted((csp.current_domains or csp.domains)[variable], key=lambda value: num_conflicts(csp, variable, value, assignment))
    
def domain_colors(variable, assignment, csp):
    return (csp.current_domains or csp.domains)[variable]

#****************** function that counts the number of conflicts ******************

def num_conflicts(csp, variable, value, assignment):
    conflicts = 0
    for v in csp.neighbors[variable]:
        if v in assignment and not constraints(variable, value, v, assignment[v]):
            conflicts += 1
    return conflicts
        
        
#****************** function that checks for goal test ******************

def assignment_completed(csp, assignment):
    all_assigned = (len(assignment) == len(csp.variables))
    no_conflicts = (all(num_conflicts(csp, variable, assignment[variable], assignment) == 0 for variable in csp.variables))
    return (all_assigned and no_conflicts)
  

#****************** neighbors cannot have the same color ******************
 
def constraints(A, a, B, b):
    return a != b

#****************** create domain for every variable ******************

def create_domains(variables, colors):
    domains = {}
    for variable in variables:
        domains[variable] = colors
    return domains
            

#****************** function to call dfsb based on mode flag ******************            

def dfsb(csp, mode_flag):
    
    assignment = {}
    if mode_flag == 0:
        result = dfsb_plain(csp, assignment)
    else:
        result = dfsb_plus_plus(csp, assignment)
    assert result is None or assignment_completed(csp, result)
    return result

#****************** function to read input file and formulate the CSP problem ******************

def read_input_file(input_file):
    
    file = open(input_file)
    lines = file.readlines()
    file.close()
    [N, M, K] = lines[0].strip().split()
    [num_variables, num_constraints, num_colors] = [int(N), int(M), int(K)] #reading input specifics
    csp_dict = {} #dict representation for the graph
    csp_dict = defaultdict(set)
    
    colors = set() #set representation for the domain
    for color in range(num_colors):
        colors.add(color)        
    for edge in range(num_constraints):
        [u, v] = lines[edge + 1].strip().split()
        [var1, var2] = [int(u), int(v)]
        csp_dict[var1].add(var2) #edge from A to  means edge from B to A
        csp_dict[var2].add(var1)
       
    return [csp_dict, colors, num_variables] 


#****************** function to generate output file ******************

def write_output_file(solution, output_file):
    if solution is not None:
        color_list = list(solution.values())
        with open(output_file, 'a') as out:
            for color in color_list:
                out.write("%s\n" % color)
    else:
        with open(output_file, 'a') as out:
            out.write("No answer")



#****************** functions to validate the graph and output ******************

def validate_graph(graph, num_variables):
    assert(num_variables == len(graph))
    for variable,neighbors in graph.items():
        assert(variable not in neighbors) #no variable linked to itself
        for next in neighbors:
            assert(next in graph and variable in graph[next]) # edge from A to B is same as B to A    
    
    
def validate_solution(graph, solution):
    if solution is not None:
        for variable,neighbors in graph.items():
            assert(variable in solution)
            color = solution[variable]
            for neighbor in neighbors:
                assert(neighbor in solution and solution[neighbor] != color)
                
                
#****************** main function ******************
def main(argv):
    args = list(argv)
    
    if len(args) < 4:
        print("You need to give 3 arguments to run this program: python dfsb.py <input_file> <output_file> <mode_flag>\n")
        return None
    else:
        input_file = args[1]
        output_file = args[2]
        mode_flag = int(args[3])

    [csp_dict, colors, num_variables] = read_input_file(input_file)
    
    validate_graph(csp_dict, num_variables)
    
    csp = CSP(set(csp_dict.keys()), create_domains(set(csp_dict.keys()), colors), csp_dict)
    
    print("################# Map coloring started using DFSB with mode: ", mode_flag)
    global start_time
    start_time = time.time() #time when the function call started
    solution = dfsb(csp, mode_flag)
    finish_time = time.time() #time when the function all ended with or without a solution for the problem
    time_taken = finish_time - start_time #total time spent inside the dfsb or dfsb++ function call
    print("################# Total time taken to run: ", time_taken)
    write_output_file(solution, output_file)
    
    validate_solution(csp_dict,solution)
    
    
#****************** main ******************
if __name__ == "__main__":
    main(sys.argv)
    
    
    
#written by: Leena Shekhar    