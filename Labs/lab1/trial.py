from production import IF, AND, OR, NOT, THEN, DELETE, forward_chain

rule1 = IF( AND( '(?x) has feathers',
                 '(?x) has a beak' ),
            THEN( '(?x) is a bird' ))
rule2 = IF( AND( '(?y) is a bird',
                 '(?y) cannot fly',
                 '(?y) can swim' ),
            THEN( '(?y) is a penguin' ) )



poker_data = ( 'two-pair beats pair',
               'three-of-a-kind beats two-pair',
               'straight beats three-of-a-kind',
               'flush beats straight',
               'full-house beats flush',
               'straight-flush beats full-house' )


print(forward_chain([rule1, rule2], poker_data, verbose=True))
