# MIT 6.034 Lab 7: Support Vector Machines
# Written by 6.034 staff

from svm_data import *
from functools import reduce
import math


#### Part 1: Vector Math #######################################################

def dot_product(u, v):
    """Computes the dot product of two vectors u and v, each represented 
    as a tuple or list of coordinates. Assume the two vectors are the
    same length."""
    return sum([i*j for i,j in zip(u,v)])

def norm(v):
    """Computes the norm (length) of a vector v, represented 
    as a tuple or list of coords."""
    return math.sqrt(sum([i**2 for i in v]))


#### Part 2: Using the SVM Boundary Equations ##################################

def positiveness(svm, point):
    """Computes the expression (w dot x + b) for the given Point x."""
    return dot_product(svm.w, point.coords) + svm.b

def classify(svm, point):
    """Uses the given SVM to classify a Point. Assume that the point's true
    classification is unknown.
    Returns +1 or -1, or 0 if point is on boundary."""
    plane = positiveness(svm, point)
    return 1 if plane > 0 else -1 if plane < 0 else 0

def margin_width(svm):
    """Calculate margin width based on the current boundary."""
    return 2/norm(svm.w)

def check_gutter_constraint(svm):
    """Returns the set of training points that violate one or both conditions:
        * gutter constraint (positiveness == classification, for support vectors)
        * training points must not be between the gutters
    Assumes that the SVM has support vectors assigned."""
    violations = set()

    for training_point in svm.training_points:
        if (training_point not in svm.support_vectors):
            if -1 < positiveness(svm, training_point) < 1:
                violations.add(training_point)
        else:
            if training_point.classification != positiveness(svm, training_point):
                violations.add(training_point)
            
    return violations


#### Part 3: Supportiveness ####################################################

def check_alpha_signs(svm):
    """Returns the set of training points that violate either condition:
        * all non-support-vector training points have alpha = 0
        * all support vectors have alpha > 0
    Assumes that the SVM has support vectors assigned, and that all training
    points have alpha values assigned."""
    violations = set()
    
    for training_point in svm.training_points:
        if (training_point not in svm.support_vectors):
            if training_point.alpha != 0:
                violations.add(training_point) 
        else:
            if training_point.alpha <= 0:
                violations.add(training_point) 
            
    return violations

def check_alpha_equations(svm):
    """Returns True if both Lagrange-multiplier equations are satisfied,
    otherwise False. Assumes that the SVM has support vectors assigned, and
    that all training points have alpha values assigned."""

    boundary = sum([tp.classification * tp.alpha for tp in svm.training_points])
    weight = reduce(vector_add, [scalar_mult(tp.classification * tp.alpha, tp.coords)\
                                 for tp in svm.training_points])

    return weight == svm.w and boundary == 0


#### Part 4: Evaluating Accuracy ###############################################

def misclassified_training_points(svm):
    """Returns the set of training points that are classified incorrectly
    using the current decision boundary."""
    misclassified = set()
    for training_point in svm.training_points:
        if classify(svm, training_point) != training_point.classification:
            misclassified.add(training_point)
            
    return misclassified


#### Part 5: Training an SVM ###################################################

def update_svm_from_alphas(svm):
    """Given an SVM with training data and alpha values, use alpha values to
    update the SVM's support vectors, w, and b. Return the updated SVM."""
    
    #separating support vectors
    support_vectors = [tp for tp in svm.training_points if tp.alpha > 0]
    negtv_spvs = [sv for sv in support_vectors if sv.classification == -1]
    postv_spvs = [sv for sv in support_vectors if sv.classification == 1]

    #calculating weight
    weight = reduce(vector_add, [scalar_mult(tp.classification * tp.alpha, tp.coords)\
                                 for tp in svm.training_points])
    #calculating b
    b_negtv = min([(-1 - dot_product(weight, sv.coords)) for sv in negtv_spvs])
    b_postv = max([(1 - dot_product(weight, sv.coords)) for sv in postv_spvs])  
    b = (b_negtv + b_postv)/2

    #updating svm
    svm.set_boundary(weight, b)
    svm.support_vectors = support_vectors

    return svm


#### Part 6: Multiple Choice ###################################################

ANSWER_1 = 11
ANSWER_2 = 6
ANSWER_3 = 3
ANSWER_4 = 2

ANSWER_5 = ['A', 'D']
ANSWER_6 = ['A', 'B', 'D']
ANSWER_7 = ['A', 'B', 'D']
ANSWER_8 = []
ANSWER_9 = ['A', 'B', 'D']
ANSWER_10 = ['A', 'B', 'D']

ANSWER_11 = False
ANSWER_12 = True
ANSWER_13 = False
ANSWER_14 = False
ANSWER_15 = False
ANSWER_16 = True

ANSWER_17 = [1, 3, 6, 8] #1, 3, 8 definitely happened on recit_data
ANSWER_18 = [1, 2, 4, 5, 6, 7, 8] #1, 4, 8 definitely happened on recit_data
ANSWER_19 = [1, 2, 4, 5, 6, 7, 8] #2, 5, 8 definitely happened on recit_data

ANSWER_20 = 6


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 3
WHAT_I_FOUND_INTERESTING = "SVMs"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
