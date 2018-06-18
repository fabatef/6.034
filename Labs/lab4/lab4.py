# MIT 6.034 Lab 4: Constraint Satisfaction Problems
# Written by 6.034 staff

from constraint_api import *
from test_problems import get_pokemon_problem
from copy import deepcopy
from itertools import combinations


#### Part 1: Warmup ############################################################

def has_empty_domains(csp) :
    """Returns True if the problem has one or more empty domains, otherwise False"""
    return any([len(csp.get_domain(var)) == 0 for var in csp.get_all_variables()])

def check_all_constraints(csp) :
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    for constraint in csp.get_all_constraints():
        val1 = csp.get_assignment(constraint.var1)
        val2 = csp.get_assignment(constraint.var2)
        if val1 != None and val2 != None:
            if not constraint.check(val1, val2):
                return False        
    return True


#### Part 2: Depth-First Constraint Solver #####################################

def solve_constraint_dfs(problem) :
    """
    Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values)
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple.
    """
    
    agenda = [problem]
    solution = None
    num_extentions = 0

    while agenda:
        current_csp = agenda.pop(0)
        num_extentions += 1
        unassigned_var = current_csp.pop_next_unassigned_var()
        new_csps = []
        if has_empty_domains(current_csp) or not check_all_constraints(current_csp):
            continue
        if check_all_constraints(current_csp) and unassigned_var == None:
            solution = current_csp.assignments
            break
        if unassigned_var != None:
            for val in current_csp.get_domain(unassigned_var):
                new_csps.append(current_csp.copy().set_assignment(unassigned_var, val))
        agenda = new_csps + agenda
        
    return (solution, num_extentions)
                 

# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with DFS?

##print (solve_constraint_dfs(get_pokemon_problem()))

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

ANSWER_1 = 20


#### Part 3: Forward Checking ##################################################

def eliminate_from_neighbors(csp, var) :
    """
    Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp.  Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None.
    """
    output = []
    v_vals = csp.get_domain(var)
    if len(v_vals) < 1:
        return output
    else:
        for neighbor in csp.get_neighbors(var):
            n_vals = deepcopy(csp.get_domain(neighbor))
            valid_pairs = []
            for constraint in csp.constraints_between(var,neighbor):
                for n in n_vals:
                    eliminate = all([not constraint.check(v , n) for v in v_vals])
                    valid_pairs+=[(v,n) for v in v_vals if constraint.check(v,n)]
                    if eliminate:
                        csp.eliminate(neighbor, n)
                        if len(csp.get_domain(neighbor)) == 0:
                            return None
                if len(csp.get_domain(neighbor)) != len(n_vals):
                       output.append(neighbor)
            
            check_validity = [(constraint.check(v,n), n) for (v,n) in valid_pairs \
                              for constraint in csp.constraints_between(var,neighbor)]
            #print (check_validity)
            
            for valid, n in check_validity:
                if not valid and n in csp.get_domain(neighbor):
                    csp.eliminate(neighbor,n)
                    if len(csp.get_domain(neighbor)) == 0:
                        return None
                    else:
                        if neighbor not in output:
                            output.append(neighbor) 
        return output
             

# Because names give us power over things (you're free to use this alias)
forward_check = eliminate_from_neighbors

def solve_constraint_forward_checking(problem) :
    """
    Solves the problem using depth-first search with forward checking.
    Same return type as solve_constraint_dfs.
    """
    agenda = [problem]
    solution = None
    num_extentions = 0

    while agenda:
        current_csp = agenda.pop(0)
        num_extentions += 1
        unassigned_var = current_csp.pop_next_unassigned_var()
        new_csps = []
        if has_empty_domains(current_csp) or not check_all_constraints(current_csp):
            continue
        if check_all_constraints(current_csp) and unassigned_var == None:
            solution = current_csp.assignments
            break
        if unassigned_var != None:
            for val in current_csp.get_domain(unassigned_var):
                new_csp = current_csp.copy().set_assignment(unassigned_var, val)
                #elimnate invalid values from the neighbors of the now assigned var
                forward_check(new_csp, unassigned_var)
                new_csps.append(new_csp)
                
        agenda = new_csps + agenda
        
    return (solution, num_extentions)


# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking?

##print (solve_constraint_forward_checking(get_pokemon_problem()))

ANSWER_2 = 9


#### Part 4: Domain Reduction ##################################################

def domain_reduction(csp, queue=None) :
    """
    Uses constraints to reduce domains, propagating the domain reduction
    to all neighbors whose domains are reduced during the process.
    If queue is None, initializes propagation queue by adding all variables in
    their default order. 
    Returns a list of all variables that were dequeued, in the order they
    were removed from the queue.  Variables may appear in the list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None.
    This function modifies the original csp.
    """
    dequed = []
    
    if queue == None:
        queue = deepcopy(csp.get_all_variables())

    while queue:
        current_var = queue.pop(0)
        dequed.append(current_var)
        reduced = eliminate_from_neighbors(csp, current_var)
        if reduced == None:
            return None
        
        for var in reduced:
            if var not in queue:
                queue.append(var)
    return dequed
        


# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with DFS (no forward checking) if you do domain reduction before solving it?

##csp = get_pokemon_problem()
##domain_reduction(csp)
##print (solve_constraint_dfs(csp))

ANSWER_3 = 6


def solve_constraint_propagate_reduced_domains(problem) :
    """
    Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs.
    """
    agenda = [problem]
    solution = None
    num_extentions = 0

    while agenda:
        current_csp = agenda.pop(0)
        num_extentions += 1
        unassigned_var = current_csp.pop_next_unassigned_var()
        new_csps = []
        if has_empty_domains(current_csp) or not check_all_constraints(current_csp):
            continue
        if check_all_constraints(current_csp) and unassigned_var == None:
            solution = current_csp.assignments
            break
        if unassigned_var != None:
            for val in current_csp.get_domain(unassigned_var):
                new_csp = current_csp.copy().set_assignment(unassigned_var, val)
                domain_reduction(new_csp, [unassigned_var])
                new_csps.append(new_csp)
                
        agenda = new_csps + agenda
        
    return (solution, num_extentions)


# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through reduced domains?

##print (solve_constraint_propagate_reduced_domains(get_pokemon_problem()))

ANSWER_4 = 7


#### Part 5A: Generic Domain Reduction #########################################

def propagate(enqueue_condition_fn, csp, queue=None) :
    """
    Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced. Same return type as domain_reduction.
    """
    dequed = []
    
    if queue == None:
        queue = deepcopy(csp.get_all_variables())

    while queue:
        current_var = queue.pop(0)
        dequed.append(current_var)
        reduced = eliminate_from_neighbors(csp, current_var)
        if reduced == None:
            return None
        for var in reduced:
            if var not in queue and enqueue_condition_fn(csp,var):
                queue.append(var)
    return dequed

def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True

def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    return len(csp.get_domain(var)) == 1

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### Part 5B: Generic Constraint Solver ########################################

def solve_constraint_generic(problem, enqueue_condition=None) :
    """
    Solves the problem, calling propagate with the specified enqueue
    condition (a function). If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs.
    """
    agenda = [problem]
    solution = None
    num_extentions = 0

    while agenda:
        current_csp = agenda.pop(0)
        num_extentions += 1
        unassigned_var = current_csp.pop_next_unassigned_var()
        new_csps = []
        if has_empty_domains(current_csp) or not check_all_constraints(current_csp):
            continue
        if check_all_constraints(current_csp) and unassigned_var == None:
            solution = current_csp.assignments
            break
        if unassigned_var != None:
            for val in current_csp.get_domain(unassigned_var):
                new_csp = current_csp.copy().set_assignment(unassigned_var, val)
                if enqueue_condition != None:
                    propagate(enqueue_condition, new_csp, [unassigned_var])
                new_csps.append(new_csp)
                
        agenda = new_csps + agenda
        
    return (solution, num_extentions)

# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through singleton domains? (Don't
#    use domain reduction before solving it.)

##print (solve_constraint_generic(get_pokemon_problem(), condition_forward_checking and condition_singleton))

ANSWER_5 = 8


#### Part 6: Defining Custom Constraints #######################################

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    return abs(m-n) == 1

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    return abs(m-n) != 1

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    output = []
    for var1,var2 in combinations(variables, 2):
        output.append(Constraint(var1,var2, constraint_different))
    return output


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 6
WHAT_I_FOUND_INTERESTING = "solving constraint satisfaction problems"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
