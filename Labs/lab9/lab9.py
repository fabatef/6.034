# MIT 6.034 Lab 9: Boosting (Adaboost)
# Written by 6.034 staff

from math import log as ln
from utils import *


#### Part 1: Helper functions ##################################################

def initialize_weights(training_points):
    """Assigns every training point a weight equal to 1/N, where N is the number
    of training points.  Returns a dictionary mapping points to weights."""
    w_o = make_fraction(1, len(training_points))
    return dict((tp, w_o) for tp in training_points)

def calculate_error_rates(point_to_weight, classifier_to_misclassified):
    """Given a dictionary mapping training points to their weights, and another
    dictionary mapping classifiers to the training points they misclassify,
    returns a dictionary mapping classifiers to their error rates."""
    output = {}
    for h,tps in classifier_to_misclassified.items():
        error_rate = sum([point_to_weight[tp] for tp in tps])
        output[h] = error_rate
    return output

def pick_best_classifier(classifier_to_error_rate, use_smallest_error=True):
    """Given a dictionary mapping classifiers to their error rates, returns the
    best* classifier, or raises NoGoodClassifiersError if best* classifier has
    error rate 1/2.  best* means 'smallest error rate' if use_smallest_error
    is True, otherwise 'error rate furthest from 1/2'."""
    if use_smallest_error:
        best = min(sorted(classifier_to_error_rate.items()), \
                   key = lambda entry: entry[1])
    else:
        best = max(sorted(classifier_to_error_rate.items()), \
                   key = lambda entry: abs(make_fraction(1,2) - entry[1]))

    if best[1] == make_fraction(1,2):
        raise NoGoodClassifiersError
    else:
        return best[0]
        

def calculate_voting_power(error_rate):
    """Given a classifier's error rate (a number), returns the voting power
    (aka alpha, or coefficient) for that classifier."""
##    1/2 * ln((1-ε)/ε)
    if error_rate == 0: #no_error
        return INF
    elif error_rate == 1: #all_error
        return -INF
    else:
        return make_fraction(1,2)* ln(make_fraction(1-error_rate, error_rate))
    

def get_overall_misclassifications(H, training_points, classifier_to_misclassified):
    """Given an overall classifier H, a list of all training points, and a
    dictionary mapping classifiers to the training points they misclassify,
    returns a set containing the training points that H misclassifies.
    H is represented as a list of (classifier, voting_power) tuples."""
    misclassified_tps = set()
    for tp in training_points:
        H_out = sum([alpha if tp not in classifier_to_misclassified[c] else -alpha for c,alpha in H ]) 
        if H_out <= 0:
            misclassified_tps.add(tp)            
    return misclassified_tps
            
        

def is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance=0):
    """Given an overall classifier H, a list of all training points, a
    dictionary mapping classifiers to the training points they misclassify, and
    a mistake tolerance (the maximum number of allowed misclassifications),
    returns False if H misclassifies more points than the tolerance allows,
    otherwise True.  H is represented as a list of (classifier, voting_power)
    tuples."""
    misclassified = get_overall_misclassifications(H, training_points, classifier_to_misclassified)
    return len(misclassified) <= mistake_tolerance

def update_weights(point_to_weight, misclassified_points, error_rate):
    """Given a dictionary mapping training points to their old weights, a list
    of training points misclassified by the current weak classifier, and the
    error rate of the current weak classifier, returns a dictionary mapping
    training points to their new weights.  This function is allowed (but not
    required) to modify the input dictionary point_to_weight."""
    #correct: new weight = 1/2 * 1/(1-ε) * (old weight)
    #misclassified: new weight = 1/2 * 1/ε * (old weight)
    
    for tp,w in point_to_weight.items():
        if tp in misclassified_points:
            new_weight = make_fraction(1,2) * make_fraction(1, error_rate)* point_to_weight[tp]
        else:
            new_weight = make_fraction(1,2) * make_fraction(1, 1-error_rate)* point_to_weight[tp]
        point_to_weight[tp] = new_weight
    return point_to_weight


#### Part 2: Adaboost ##########################################################

def adaboost(training_points, classifier_to_misclassified,
             use_smallest_error=True, mistake_tolerance=0, max_rounds=INF):
    """Performs the Adaboost algorithm for up to max_rounds rounds.
    Returns the resulting overall classifier H, represented as a list of
    (classifier, voting_power) tuples."""
    point_to_weight = initialize_weights(training_points)
    H = []
    while max_rounds != 0:
        classifier_to_error_rate = calculate_error_rates(point_to_weight, classifier_to_misclassified)
        try:
            best_classifier = pick_best_classifier(classifier_to_error_rate, use_smallest_error)
            error_rate = classifier_to_error_rate[best_classifier]
            alpha = calculate_voting_power(error_rate)
            H.append((best_classifier, alpha))
            if is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance):
                break
            misclassified_points = classifier_to_misclassified[best_classifier]
            update_weights(point_to_weight, misclassified_points, error_rate)
            max_rounds -= 1
        except NoGoodClassifiersError:
            break   
    return H


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 3
WHAT_I_FOUND_INTERESTING = "Adaboost"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
