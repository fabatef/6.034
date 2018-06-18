# MIT 6.034 Lab 6: Neural Nets
# Written by 6.034 Staff

from nn_problems import *
import math
from math import e
from itertools import product
INF = float('inf')


#### Part 1: Wiring a Neural Net ###############################################

nn_half = [1]

nn_angle = [2,1]

nn_cross = [2,2,1]

nn_stripe = [3,1]

nn_hexagon = [6,1]

nn_grid = [4,2,1]


#### Part 2: Coding Warmup #####################################################

# Threshold functions
def stairstep(x, threshold=0):
    "Computes stairstep(x) using the given threshold (T)"
    return 1 if x >= threshold else 0

def sigmoid(x, steepness=1, midpoint=0):
    "Computes sigmoid(x) using the given steepness (S) and midpoint (M)"
    return 1/(1 + math.exp(-steepness*(x-midpoint)))

def ReLU(x):
    "Computes the threshold of an input using a rectified linear unit."
    return max(0,x)

# Accuracy function
def accuracy(desired_output, actual_output):
    "Computes accuracy. If output is binary, accuracy ranges from -0.5 to 0."
    return -0.5*(desired_output - actual_output)**2


#### Part 3: Forward Propagation ###############################################

def node_value(node, input_values, neuron_outputs):  # PROVIDED BY THE STAFF
    """
    Given 
     * a node (as an input or as a neuron),
     * a dictionary mapping input names to their values, and
     * a dictionary mapping neuron names to their outputs
    returns the output value of the node.
    This function does NOT do any computation; it simply looks up
    values in the provided dictionaries.
    """
    if isinstance(node, str):
        # A string node (either an input or a neuron)
        if node in input_values:
            return input_values[node]
        if node in neuron_outputs:
            return neuron_outputs[node]
        raise KeyError("Node '{}' not found in either the input values or neuron outputs dictionary.".format(node))
    
    if isinstance(node, (int, float)):
        # A constant input, such as -1
        return node
    
    raise TypeError("Node argument is {}; should be either a string or a number.".format(node))

def forward_prop(net, input_values, threshold_fn=stairstep):
    """Given a neural net and dictionary of input values, performs forward
    propagation with the given threshold function to compute binary output.
    This function should not modify the input net.  Returns a tuple containing:
    (1) the final output of the neural net
    (2) a dictionary mapping neurons to their immediate outputs"""
    neuron_outputs = {}
    for node in net.topological_sort():
        #sum the wire_weight*value of all neurons going into the currrent node
        #then squish the sum with the threshold/actvn fun and update the newly computed neurons' value dict
        activn = [net.get_wires(i, node)[0].get_weight()*node_value(i, input_values, neuron_outputs)\
                  for i in net.get_incoming_neighbors(node)]
        neuron_outputs[node] = threshold_fn(sum(activn))
    return (neuron_outputs[net.get_output_neuron()], neuron_outputs)


#### Part 4: Backward Propagation ##############################################


def gradient_ascent_step(func, inputs, step_size):
    """Given an unknown function of three variables and a list of three values
    representing the current inputs into the function, increments each variable
    by +/- step_size or 0, with the goal of maximizing the function output.
    After trying all possible variable assignments, returns a tuple containing:
    (1) the maximum function output found, and
    (2) the list of inputs that yielded the highest function output."""
    #**3 b/c possiblities are + step, - step and 0
    inputs = [tuple(inputs)]*(len(inputs)**3)
    possible_steps = [i for i in product([-step_size, 0, step_size], repeat=3)]
    trials = [[sum(j) for j in zip(i[0],i[1])] for i in zip(inputs, possible_steps)]
    trial_outputs = [(func(*t), t) for t in trials]
    return max(trial_outputs, key = lambda entry: entry[0])

def get_back_prop_dependencies(net, wire):
    """Given a wire in a neural network, returns a set of inputs, neurons, and
    Wires whose outputs/values are required to update this wire's weight."""
    dependency = set()
    def back_prop_dependency_helper(net, wire, dependency):
        dependency.add(wire)
        dependency.add(wire.startNode)
        dependency.add(wire.endNode)
        if net.is_output_neuron(wire.endNode):
            return dependency
        else:
            for neuron in net.get_outgoing_neighbors(wire.endNode):
                back_prop_dependency_helper(net, net.get_wires(wire.endNode, neuron)[0], dependency)
        return dependency
    return back_prop_dependency_helper(net, wire, dependency)
                                                     

def calculate_deltas(net, desired_output, neuron_outputs):
    """Given a neural net and a dictionary of neuron outputs from forward-
    propagation, computes the update coefficient (delta_B) for each
    neuron in the net. Uses the sigmoid function to compute neuron output.
    Returns a dictionary mapping neuron names to update coefficient (the
    delta_B values). """
    #from the formula in the lab directly
    deltas = {}
    for neuron in reversed(net.topological_sort()):
        if net.is_output_neuron(neuron):
            out_B = neuron_outputs[neuron]
            delta_B = out_B * (1 - out_B) * (desired_output - out_B)
            deltas[neuron] = delta_B
        else:
            summation = 0
            out_B = neuron_outputs[neuron]
            for wire in net.get_wires(startNode = neuron):
                summation += (wire.get_weight()*deltas[wire.endNode])
            delta_B = out_B * (1 - out_B) * summation
            deltas[neuron] = delta_B
    return deltas

def update_weights(net, input_values, desired_output, neuron_outputs, r=1):
    """Performs a single step of back-propagation.  Computes delta_B values and
    weight updates for entire neural net, then updates all weights.  Uses the
    sigmoid function to compute neuron output.  Returns the modified neural net,
    with the updated weights."""
    deltas = calculate_deltas(net, desired_output, neuron_outputs)
    for wire in net.get_wires():
        old_weight = wire.get_weight()
        big_delta = r * node_value(wire.startNode, input_values, neuron_outputs)\
                    * deltas[wire.endNode]
        new_weight = old_weight + big_delta
        wire.set_weight(new_weight)
    return net

def back_prop(net, input_values, desired_output, r=1, minimum_accuracy=-0.001):
    """Updates weights until accuracy surpasses minimum_accuracy.  Uses the
    sigmoid function to compute neuron output.  Returns a tuple containing:
    (1) the modified neural net, with trained weights
    (2) the number of iterations (that is, the number of weight updates)"""
    #aliasing happens b/n function names and variable names!
    cost = -INF
    iters = 0
    while True:
        actual_output, neuron_outputs = forward_prop(net, input_values, sigmoid)
        cost = accuracy(desired_output, actual_output)
        if cost < minimum_accuracy:
            update_weights(net, input_values, desired_output, neuron_outputs, r)
            iters+=1
        else:
            break
    return (net, iters)


#### Part 5: Training a Neural Net #############################################

ANSWER_1 = 17
ANSWER_2 = 20
ANSWER_3 = 3
ANSWER_4 = 110
ANSWER_5 = 60

ANSWER_6 = 1
ANSWER_7 = "checkerboard"
ANSWER_8 = ['small', 'medium', 'large']
ANSWER_9 = "B"

ANSWER_10 = "D"
ANSWER_11 = ["A", "C"]
ANSWER_12 = ["A", "E"]


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 4
WHAT_I_FOUND_INTERESTING = "the whole lab was very interesting"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = None
