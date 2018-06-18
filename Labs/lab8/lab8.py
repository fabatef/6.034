# MIT 6.034 Lab 8: Bayesian Inference
# Written by 6.034 staff

from nets import *
import itertools
from copy import deepcopy

#### Part 1: Warm-up; Ancestors, Descendents, and Non-descendents ##############

def get_ancestors(net, var):
    "Return a set containing the ancestors of var"
    output = set()
    expand = [var]
    while expand:
        cur_var = expand.pop(0)
        parents = net.get_parents(cur_var)
        if parents:
            expand += list(parents)
            output.update(parents)
    return output         
            

def get_descendants(net, var):
    "Returns a set containing the descendants of var"
    output = set()
    expand = [var]
    while expand:
        cur_var = expand.pop(0)
        children= net.get_children(cur_var)
        if children:
            expand += list(children)
            output.update(children)
    return output 

def get_nondescendants(net, var):
    "Returns a set containing the non-descendants of var"
    descendants = get_descendants(net, var)
    universe = set(net.get_variables())
    return universe.difference(descendants, set(var))


#### Part 2: Computing Probability #############################################

def simplify_givens(net, var, givens):
    """
    If givens include every parent of var and no descendants, returns a
    simplified list of givens, keeping only parents.  Does not modify original
    givens.  Otherwise, if not all parents are given, or if a descendant is
    given, returns original givens.
    """
    parents = net.get_parents(var)
    descendants = get_descendants(net, var)
    gvns = set(givens.keys())
    if parents.issubset(gvns) and descendants.isdisjoint(gvns):
        return dict((p,givens[p]) for p in parents)
    else:
        return dict((v,givens[v]) for v in givens)
    
    
def probability_lookup(net, hypothesis, givens=None):
    "Looks up a probability in the Bayes net, or raises LookupError"
    try:
        hypt = [h for h in hypothesis.keys()]
        if givens != None:
            givens = simplify_givens(net, hypt[0], givens)
        return net.get_probability(hypothesis, givens)
    except ValueError:
        raise LookupError

def probability_joint(net, hypothesis):
    "Uses the chain rule to compute a joint probability"
    keys = net.topological_sort()
    keys.reverse()
    conditional_probs = []
    for i in range(len(keys)):
        hypt = {keys[i]: hypothesis[keys[i]]}
        gvns = None
        if i != len(keys)-1:
            gvns = dict((keys[j], hypothesis[keys[j]]) for j in range(i+1,len(keys)))
        conditional_probs.append(probability_lookup(net, hypt, gvns))
    return product(conditional_probs)
        
    
def probability_marginal(net, hypothesis):
    "Computes a marginal probability as a sum of joint probabilities"
    output = 0
    for cmbn in net.combinations(net.get_variables()):
        if set(hypothesis.items()).issubset(set(cmbn.items())):
            output+=probability_joint(net, cmbn)
    return output

def probability_conditional(net, hypothesis, givens=None):
    "Computes a conditional probability as a ratio of marginal probabilities"
    if givens == None:
        return probability_marginal(net, hypothesis)
    else:
        edge_case = set(hypothesis.keys()).intersection(set(givens.keys()))
        if edge_case and not all(hypothesis[var] == givens[var] for var in edge_case):
            return 0
        return probability_marginal(net, dict(givens, **hypothesis))/probability_marginal(net, givens)
    
def probability(net, hypothesis, givens=None): #?? what's the point
    "Calls previous functions to compute any probability"
    return probability_conditional(net, hypothesis, givens)


#### Part 3: Counting Parameters ###############################################

def number_of_parameters(net):#??
    """
    Computes the minimum number of parameters required for the Bayes net.
    """
    #for one RV: num_params = (d-1)d^p (d: domain, p: num_parents)
    output = 0
    for var in net.get_variables():
        parents = [len(net.get_domain(p))for p in net.get_parents(var)]
        d = len(net.get_domain(var))
        num_params = (d-1)* product(parents)
        output+= num_params
    return output
        


#### Part 4: Independence ######################################################

def is_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    otherwise False. Uses numerical independence.
    """
    #P(XY|Z)=P(X|Z)P(Y|Z)
    for b1 in net.get_domain(var1):
        for b2 in net.get_domain(var2):
            xy_z = probability(net, {var1:b1, var2:b2}, givens)
            x_z = probability(net, {var1:b1}, givens)
            y_z = probability(net, {var2: b2}, givens)
            if not approx_equal(xy_z, x_z*y_z):
                return False
    return True
    
def is_structurally_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    based on the structure of the Bayes net, otherwise False.
    Uses structural independence only (not numerical independence).
    """
    #ancestoral graph(all of the mentioned vars and their ancestors)
    expr_vars = [var1, var2]
    if givens != None:
        expr_vars+=[i for i in givens.keys()]
    subnet_vars = deepcopy(expr_vars)
    for var in expr_vars:
        subnet_vars += list(get_ancestors(net, var))#gets messed up when i work with sets.. use of union??
    subnet = net.subnet(list(set(subnet_vars)))

    #moralize by marrying.. lol wut (if a var has more than 1 parent, draw an edge b/n all possible pairs)
    #extract pairs then add links so as not to mutate the graph and mess up the parent->child relations while iterating
    link_pairs = [pair for pair in itertools.combinations(subnet.get_parents(var), 2)\
                  for var in subnet.get_variables() if len(subnet.get_parents(var)) > 1]
    for p,c in link_pairs:
        subnet.link(p,c)
        
    #disorient graph
    subnet.make_bidirectional() 

    #delete givens and their edges
    if givens != None:
        for var in givens.keys():
            subnet.remove_variable(var)

    return subnet.find_path(var1, var2) == None #disconnected --> independent


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 4
WHAT_I_FOUND_INTERESTING = "Bayesian inference"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
