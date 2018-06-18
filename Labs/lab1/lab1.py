# MIT 6.034 Lab 1: Rule-Based Systems
# Written by 6.034 staff

from production import IF, AND, OR, NOT, THEN, DELETE, forward_chain
from data import *
import pprint

pp = pprint.PrettyPrinter(indent=1)
pprint = pp.pprint

#### Part 1: Multiple Choice #########################################

ANSWER_1 = '2'

ANSWER_2 = '4'

ANSWER_3 = '2'

ANSWER_4 = '0'

ANSWER_5 = '3'

ANSWER_6 = '1'

ANSWER_7 = '0'

#### Part 2: Transitive Rule #########################################

# Fill this in with your rule 
transitive_rule = IF( AND( '(?x) beats (?y)',
                           '(?y) beats (?z)'),
                      THEN('(?x) beats (?z)'))

# You can test your rule by uncommenting these pretty print statements
#  and observing the results printed to your screen after executing lab1.py
#pprint(forward_chain([transitive_rule], abc_data))
#pprint(forward_chain([transitive_rule], poker_data))
#pprint(forward_chain([transitive_rule], minecraft_data))


#### Part 3: Family Relations #########################################

# Define your rules here. We've given you an example rule whose lead you can follow:
#friend_rule = IF( AND("person (?x)", "person (?y)"), THEN ("friend (?x) (?y)", "friend (?y) (?x)") )
same_person = IF("parent (?y) (?x)", THEN ("samePerson (?x) (?x)"))

sibling_rule = IF( AND("parent (?x) (?y)",
                       "parent (?x) (?z)",
                       NOT("samePerson (?y) (?z)")),
                   THEN ("sibling (?y) (?z)"))

child_rule = IF( "parent (?x) (?y)", THEN ("child (?y) (?x)"))

cousin_rule = IF (AND("sibling (?x) (?y)",
                       "parent (?x) (?z)",
                      "parent (?y) (?w)",
                      NOT ("samePerson (?z) (?w)")),
                  THEN ("cousin (?z) (?w)"))
                  
gp_rule = IF (OR (AND("parent (?x) (?y)", "parent (?y) (?z)"),
                  AND("child (?z) (?y)", "child (?y) (?x)")),
              THEN ("grandparent (?x) (?z)"))

gc_rule = IF (OR (AND("parent (?x) (?y)", "parent (?y) (?z)"),
                  AND("child (?z) (?y)", "child (?y) (?x)")),
              THEN ("grandchild (?z) (?x)"))
#clean = IF ( "sibling (?x) (?x)", DELETE( "sibling (?x) (?x)"))

### Add your rules to this list:
family_rules = [same_person, sibling_rule, child_rule,cousin_rule, gp_rule, gc_rule]
##
### Uncomment this to test your data on the Simpsons family:
### pprint(forward_chain(family_rules, simpsons_data, verbose=False))
##
### These smaller datasets might be helpful for debugging:
##pprint(forward_chain(family_rules, sibling_test_data, verbose=True))
##pprint(forward_chain(family_rules, grandparent_test_data, verbose=True))
##
### The following should generate 14 cousin relationships, representing 7 pairs
### of people who are cousins:
##black_family_cousins = [
##    relation for relation in
##    forward_chain(family_rules, black_data, verbose=False)
##    if "cousin" in relation ]

### To see if you found them all, uncomment this line:
##pprint(black_family_cousins)


#### Part 4: Backward Chaining #########################################

# Import additional methods for backchaining
from production import PASS, FAIL, match, populate, simplify, variables

tree = ''

def backchain_to_goal_tree(rules, hypothesis):
    """
    Takes a hypothesis (string) and a list of rules (list
    of IF objects), returning an AND/OR tree representing the
    backchain of possible statements we may need to test
    to determine if this hypothesis is reachable or not.

    This method should return an AND/OR tree, that is, an
    AND or OR object, whose constituents are the subgoals that
    need to be tested. The leaves of this tree should be strings
    (possibly with unbound variables), *not* AND or OR objects.
    Make sure to use simplify(...) to flatten trees where appropriate.
    """
    #print ('HYPOTHESIS: ', hypothesis)
    tree = [hypothesis]
    for rule in rules:
        consequent = rule.consequent()
        bindings = match(consequent, hypothesis)
        #print ('BINDINGS: ', bindings)
        #found a matching rule
        if bindings != None:
            antecedent = rule.antecedent()
            #if the antecedent is a statement, add it to the tree and recurse on it as the new hypothesis
            if isinstance(antecedent, str):
                new_hypothesis = populate(antecedent, bindings)
                tree.append(new_hypothesis)
                tree.append(backchain_to_goal_tree(rules, new_hypothesis)) 
                
            #if not, go through each statement in antecedent, and recurse on them, build their subtree and add to the tree
            else:
                statements = [populate(statement, bindings) for statement in antecedent]
                subtree = []
                for statement in statements:
                    subtree.append(backchain_to_goal_tree(rules, statement))
                #print ('SUBTREE: ', subtree)

                #for an AND antecedent
                if isinstance(antecedent, AND):
                    tree.append(AND(subtree))
                #for an OR antecedent
                else: 
                    tree.append(OR(subtree))
    #print ('TREE: ', tree)
    return simplify(OR(tree))


# Uncomment this to test out your backward chainer:
#RULES:
#IF(AND('(?x) has hair'), THEN('(?x) is a mammal'))
#IF(AND('(?x) gives milk'), THEN('(?x) is a mammal'))
#IF(AND('(?x) has feathers'), THEN('(?x) is a bird'))
#IF(AND('(?x) flies', '(?x) lays eggs'), THEN('(?x) is a bird'))
#IF(AND('(?x) is a mammal', '(?x) eats meat'), THEN('(?x) is a carnivore'))
#IF(AND('(?x) is a mammal', '(?x) has pointed teeth', '(?x) has claws', '(?x) has forward-pointing eyes'), THEN('(?x) is a carnivore'))
#IF(AND('(?x) is a mammal', '(?x) has hoofs'), THEN('(?x) is an ungulate'))
#IF(AND('(?x) is a mammal', '(?x) chews cud'), THEN('(?x) is an ungulate'))
#IF(AND('(?x) is a carnivore', '(?x) has tawny color', '(?x) has dark spots'), THEN('(?x) is a cheetah'))
#IF(AND('(?x) is a carnivore', '(?x) has tawny color', '(?x) has black stripes'), THEN('(?x) is a tiger'))
#IF(AND('(?x) is an ungulate', '(?x) has long legs', '(?x) has long neck', '(?x) has tawny color', '(?x) has dark spots'), THEN('(?x) is a giraffe'))
#IF(AND('(?x) is an ungulate', '(?x) has white color', '(?x) has black stripes'), THEN('(?x) is a zebra'))
#IF(AND('(?x) is a bird', '(?x) does not fly', '(?x) has long legs', '(?x) has long neck', '(?x) has black and white color'), THEN('(?x) is an ostrich'))
#IF(AND('(?x) is a bird', '(?x) does not fly', '(?x) swims', '(?x) has black and white color'), THEN('(?x) is a penguin'))
#IF(AND('(?x) is a bird', '(?x) is a good flyer'), THEN('(?x) is an albatross')))

##result = backchain_to_goal_tree(zookeeper_rules, 'opus is a penguin')
##print(result)
##expected = OR('opus is a penguin',
##              AND(OR('opus is a bird', 'opus has feathers',
##                     AND('opus flies', 'opus lays eggs')),
##                  'opus does not fly',
##                  'opus swims',
##                  'opus has black and white color' ))
##print (result == expected)




#### Survey #########################################

NAME = "Faaya Abate Fulas"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = "Building the and/or tree"
WHAT_I_FOUND_BORING = "Family relations was tedious" 
SUGGESTIONS = "Maybe production.py could have been written such that aliasing bindings isn't allowed"


###########################################################
### Ignore everything below this line; for testing only ###
###########################################################

# The following lines are used in the tester. DO NOT CHANGE!
transitive_rule_poker = forward_chain([transitive_rule], poker_data)
transitive_rule_abc = forward_chain([transitive_rule], abc_data)
transitive_rule_minecraft = forward_chain([transitive_rule], minecraft_data)
family_rules_simpsons = forward_chain(family_rules, simpsons_data)
family_rules_black = forward_chain(family_rules, black_data)
family_rules_sibling = forward_chain(family_rules, sibling_test_data)
family_rules_grandparent = forward_chain(family_rules, grandparent_test_data)
family_rules_anonymous_family = forward_chain(family_rules, anonymous_family_test_data)
