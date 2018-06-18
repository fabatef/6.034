# MIT 6.034 Lab 5: k-Nearest Neighbors and Identification Trees
# Written by 6.034 Staff

from api import *
from data import *
from copy import deepcopy
import math
log2 = lambda x: math.log(x, 2)
INF = float('inf')


################################################################################
############################# IDENTIFICATION TREES #############################
################################################################################


#### Part 1A: Classifying points ###############################################

def id_tree_classify_point(point, id_tree):
    """Uses the input ID tree (an IdentificationTreeNode) to classify the point.
    Returns the point's classification."""
    current_node = id_tree
    while not current_node.is_leaf():
        current_node = current_node.apply_classifier(point)
    return current_node.get_node_classification()


#### Part 1B: Splitting data with a classifier #################################

def split_on_classifier(data, classifier):
    """Given a set of data (as a list of points) and a Classifier object, uses
    the classifier to partition the data.  Returns a dict mapping each feature
    values to a list of points that have that value."""
    output = {}
    for point in data:
        feature_value = classifier.classify(point)
        points = output.get(feature_value, [])
        output[feature_value] = points+[point]
    return output


#### Part 1C: Calculating disorder #############################################

def branch_disorder(data, target_classifier):
    """Given a list of points representing a single branch and a Classifier
    for determining the true classification of each point, computes and returns
    the disorder of the branch."""
    ##n_b: the number of data points in the branch
    ##n_bc: the number of data points in the branch with the given classification
    final_classification = split_on_classifier(data, target_classifier)
    n_b = len(data)
    branch_disorder = 0
    for feature_value in final_classification:
        n_bc = len(final_classification[feature_value])
        branch_disorder -= (n_bc/n_b)*log2(n_bc/n_b)
    return branch_disorder

def average_test_disorder(data, test_classifier, target_classifier):
    """Given a list of points, a feature-test Classifier, and a Classifier
    for determining the true classification of each point, computes and returns
    the disorder of the feature-test stump."""
    test_classification = split_on_classifier(data, test_classifier)
    average = 0
    for branch_value in test_classification:
        branch_data = test_classification[branch_value]
        weight = len(branch_data)/len(data)
        average+= weight*branch_disorder(branch_data, target_classifier)
    return average


## To use your functions to solve part A2 of the "Identification of Trees"
## problem from 2014 Q2, uncomment the lines below and run lab5.py:

##for classifier in tree_classifiers:
##    print(classifier.name, average_test_disorder(tree_data, classifier, feature_test("tree_type")))


#### Part 1D: Constructing an ID tree ##########################################

def find_best_classifier(data, possible_classifiers, target_classifier):
    """Given a list of points, a list of possible Classifiers to use as tests,
    and a Classifier for determining the true classification of each point,
    finds and returns the classifier with the lowest disorder.  Breaks ties by
    preferring classifiers that appear earlier in the list.  If the best
    classifier has only one branch, raises NoGoodClassifiersError."""
    disorder = [(average_test_disorder(data, test_classifier, target_classifier)\
                 ,test_classifier) for test_classifier in possible_classifiers]
    
    best_classifier = min(disorder, key= lambda x: x[0])[1]
    if average_test_disorder(data, best_classifier, target_classifier) == 1:
    #if len(split_on_classifier(data,best_classifier)) == 1:
        raise NoGoodClassifiersError
    else:
        return best_classifier


## To find the best classifier from 2014 Q2, Part A, uncomment:
# print(find_best_classifier(tree_data, tree_classifiers, feature_test("tree_type")))

def construct_greedy_id_tree(data, possible_classifiers, target_classifier, id_tree_node=None):
    """Given a list of points, a list of possible Classifiers to use as tests,
    a Classifier for determining the true classification of each point, and
    optionally a partially completed ID tree, returns a completed ID tree by
    adding classifiers and classifications until either perfect classification
    has been achieved, or there are no good classifiers left."""
    #Initialize id_tree_node if none is given
    if id_tree_node == None:
        id_tree_node = IdentificationTreeNode(target_classifier)

    #homogenous node: every point in the data has the same feature value for the target_classifier
    #set the leaf node with its classification
    if branch_disorder(data, target_classifier) == 0:
        classification = data[0][target_classifier.name]
        id_tree_node.set_node_classification(classification)
        
    #find the best_classifier, classifiy the data using it -> get the node's branches/children),
    #set the best_classifier for the current node, then recursively classify its children
    else: 
        try:
            best_classifier = find_best_classifier(data, possible_classifiers, target_classifier)
            branches_data = split_on_classifier(data, best_classifier)
            possible_classifiers.remove(best_classifier)
            features = branches_data.keys()
            id_tree_node.set_classifier_and_expand(best_classifier,features)
            for branch, child_node in id_tree_node.get_branches().items():
                construct_greedy_id_tree(branches_data[branch], possible_classifiers, target_classifier, child_node)
        except NoGoodClassifiersError:
            #if there're no classifiers, do nothing
            return id_tree_node
            
    return id_tree_node
    


## To construct an ID tree for 2014 Q2, Part A:
##print(construct_greedy_id_tree(tree_data, tree_classifiers, feature_test("tree_type")))


## To use your ID tree to identify a mystery tree (2014 Q2, Part A4):
# tree_tree = construct_greedy_id_tree(tree_data, tree_classifiers, feature_test("tree_type"))
# print(id_tree_classify_point(tree_test_point, tree_tree))

## To construct an ID tree for 2012 Q2 (Angels) or 2013 Q3 (numeric ID trees):
# print(construct_greedy_id_tree(angel_data, angel_classifiers, feature_test("Classification")))
# print(construct_greedy_id_tree(numeric_data, numeric_classifiers, feature_test("class")))


#### Part 1E: Multiple choice ##################################################

ANSWER_1 = 'bark_texture'
ANSWER_2 = 'leaf_shape'
ANSWER_3 = 'orange_foliage'

ANSWER_4 = [2,3]
ANSWER_5 = [3] #? oh
ANSWER_6 = [2]
ANSWER_7 = 2

ANSWER_8 = 'No' # because the set of data points that are being classified have changed.
ANSWER_9 = 'No' # it picks C first and ends up creating binary tree 3


#### OPTIONAL: Construct an ID tree with medical data ##########################

## Set this to True if you'd like to do this part of the lab
DO_OPTIONAL_SECTION = False

if DO_OPTIONAL_SECTION:
    from parse import *
    medical_id_tree = construct_greedy_id_tree(heart_training_data, heart_classifiers, heart_target_classifier_discrete)


################################################################################
############################# k-NEAREST NEIGHBORS ##############################
################################################################################

#### Part 2A: Drawing Boundaries ###############################################

BOUNDARY_ANS_1 = 3 
BOUNDARY_ANS_2 = 4#1

BOUNDARY_ANS_3 = 1#3
BOUNDARY_ANS_4 = 2

BOUNDARY_ANS_5 = 2
BOUNDARY_ANS_6 = 4#2#1#3
BOUNDARY_ANS_7 = 1
BOUNDARY_ANS_8 = 4#2
BOUNDARY_ANS_9 = 4#2

BOUNDARY_ANS_10 = 4#2
BOUNDARY_ANS_11 = 2
BOUNDARY_ANS_12 = 1
BOUNDARY_ANS_13 = 4#2
BOUNDARY_ANS_14 = 4#2


#### Part 2B: Distance metrics #################################################

def dot_product(u, v):
    """Computes dot product of two vectors u and v, each represented as a tuple
    or list of coordinates.  Assume the two vectors are the same length."""
    return sum([i*j for i,j in zip(u,v)])

def norm(v):
    "Computes length of a vector v, represented as a tuple or list of coords."
    return math.sqrt(sum([i**2 for i in v]))

def euclidean_distance(point1, point2):
    "Given two Points, computes and returns the Euclidean distance between them."
    return math.sqrt(sum([(u_i - v_i)**2 for u_i, v_i in zip(point1, point2)]))

def manhattan_distance(point1, point2):
    "Given two Points, computes and returns the Manhattan distance between them."
    return sum([abs(u_i - v_i) for u_i, v_i in zip(point1, point2)])

def hamming_distance(point1, point2):
    "Given two Points, computes and returns the Hamming distance between them."
    return sum([1 for i, j in zip(point1, point2) if i != j])

def cosine_distance(point1, point2):
    """Given two Points, computes and returns the cosine distance between them,
    where cosine distance is defined as 1-cos(angle_between(point1, point2))."""
    return 1 - (dot_product(point1, point2)/(norm(point1)*norm(point2)))


#### Part 2C: Classifying points ###############################################

def get_k_closest_points(point, data, k, distance_metric):
    """Given a test point, a list of points (the data), an int 0 < k <= len(data),
    and a distance metric (a function), returns a list containing the k points
    from the data that are closest to the test point, according to the distance
    metric.  Breaks ties lexicographically by coordinates."""
    #sorted is a stable sort, so sort by coordinates first, then sort by closeness
    distance = sorted([(distance_metric(point, point_i), point_i) for point_i in data],\
                      key = lambda x: x[1].coords)
    return [points for distance, points in sorted(distance, key = lambda x: x[0])[0:k]]

def knn_classify_point(point, data, k, distance_metric):
    """Given a test point, a list of points (the data), an int 0 < k <= len(data),
    and a distance metric (a function), returns the classification of the test
    point based on its k nearest neighbors, as determined by the distance metric.
    Assumes there are no ties."""

    closest_points = get_k_closest_points(point, data, k, distance_metric)
    clasfn_freq= [point.classification for point in closest_points]
    return max(clasfn_freq, key = lambda clasfn: clasfn_freq.count(clasfn))



## To run your classify function on the k-nearest neighbors problem from 2014 Q2
## part B2, uncomment the line below and try different values of k:
# print(knn_classify_point(knn_tree_test_point, knn_tree_data, 1, euclidean_distance))


#### Part 2C: Choosing k #######################################################

def cross_validate(data, k, distance_metric):
    """Given a list of points (the data), an int 0 < k <= len(data), and a
    distance metric (a function), performs leave-one-out cross-validation.
    Return the fraction of points classified correctly, as a float."""
    correct_clasfn = 0
    for i in range(len(data)):
        training_set = deepcopy(data)
        test_set = training_set.pop(i)
        training_clasfn = knn_classify_point(test_set, training_set, k, distance_metric)
        if test_set.classification == training_clasfn:
            correct_clasfn+=1  
    return correct_clasfn/len(data)

def find_best_k_and_metric(data):
    """Given a list of points (the data), uses leave-one-out cross-validation to
    determine the best value of k and distance_metric, choosing from among the
    four distance metrics defined above.  Returns a tuple (k, distance_metric),
    where k is an int and distance_metric is a function."""
    distance_metrics = [euclidean_distance, manhattan_distance, hamming_distance, cosine_distance]
    output = []
    for k in range(1,int(len(data)*0.75)):
        for distance_metric in distance_metrics:
            accuracy = cross_validate(data, k, distance_metric)
            output.append((accuracy, k, distance_metric))
    return max(output, key = lambda entry: entry[0])[1:]
            


## To find the best k and distance metric for 2014 Q2, part B, uncomment:
##print(find_best_k_and_metric(knn_tree_data))


#### Part 2E: More multiple choice #############################################

kNN_ANSWER_1 = 'Overfitting'
kNN_ANSWER_2 = 'Underfitting'
kNN_ANSWER_3 = 4

kNN_ANSWER_4 = 4
kNN_ANSWER_5 = 1 
kNN_ANSWER_6 = 3
kNN_ANSWER_7 = 3


#### SURVEY ####################################################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 4
WHAT_I_FOUND_INTERESTING = "building identification trees"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
