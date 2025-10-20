'''
    Desc: Defines the classes used by the SAT solver for DPLL algorithm
'''
import copy
import glob
import os
import random
from re import A
from stringprep import in_table_a1
#from sympy import *
'''
    File Class:
        fileN: Name of the file
        numClauses: Number of clauses in the file
        clausesRaw: Clauses as they are in the file
        clausesNegation: Negated clauses for DPLL algorithm
'''
class File:
    def __init__(self, fileN, numClauses, clausesRaw, clausesNegation, clausesOriginal):
        self.fileN = fileN
        self.numClauses = numClauses
        self.clausesRaw = clausesRaw
        self.clausesNegation = clausesNegation
        self.clausesOriginal = clausesOriginal


'''
Node Class:
Parent: Parent node of current
clauses: the clause set at this node
assignment: Current assignment of variables
'''
class Node:
    def __init__(self, parent, clauses, assignment):
        self.parent = parent
        self.clauses = clauses
        self.assignment = assignment

# dpll Algorithm using a stack instead of recursion, too many resources used when recurring too much
def dpll(clauses, assignment):
    stack = []
    root = Node(None, clauses, assignment)
    stack.append(root)

    while stack:
        node = stack.pop()
        clauses, assignment = node.clauses, node.assignment

        # Unit propagation
        clauses, assignment, isConflict = unitPropagation(clauses, assignment)
        if isConflict:
            continue  # Conflict, backtrack

        if not clauses:
            print("Found solution!!!")
            return True, assignment  # Solution found

        literal = pickMostConstraining(clauses, assignment)
        if literal is None:
            print("No assigned literals left here, backtracking...")
            continue  # No unassigned literals, backtrack

        # Try literal = False first, so True is explored first
        new_assignment_false = assignment.copy()
        new_assignment_false[literal] = False
        stack.append(Node(node, simplify(clauses, -literal), new_assignment_false))

        new_assignment_true = assignment.copy()
        new_assignment_true[literal] = True
        stack.append(Node(node, simplify(clauses, literal), new_assignment_true))

    print("Did not find Solution...Conflict in all branches")
    return False, None  # GLOBAL unsatisfiability

#Simplify all clauses in formula by removing clauses satisfied by literals
def simplify(clauses, literal):
    if literal is None:
        return [list(clause) for clause in clauses] # Avoids mutating input

    new_clauses = []
    for clause in clauses:
        # If clause is satisfied by literal, drop it
        if literal in clause:
            continue
        # Otherwise remove the falsified literal (-literal) from the clause
        reduced = [lit for lit in clause if lit != -literal]
        new_clauses.append(reduced)

    return new_clauses
    
#Counts the number of times a literal shows up in each clause for picking the unassigned literal
def countLiteral(clauses):
    count = {}
    for clause in clauses:
        for lit in clause:
            v = abs(lit)
            count[v] = count.get(v, 0) + 1
    return count
#Picks the most constraining unassigned literal that has not been chosen yet
def pickMostConstraining(clauses, assignment):
    count = countLiteral(clauses)

    bestLit = None
    bestCount = -1
    for lit, cnt in count.items():
        if lit in assignment:
            continue # Literal already assigned
        if cnt > bestCount: # If found a better literal
            bestCount = cnt
            bestLit = lit
    return bestLit # All variables assigned

def unitPropagation(clauses, assignment):
    clauses = [list(clause) for clause in clauses]   # avoid mutating input
    if assignment is None:
        assignment = {}
    else:
        assignment = assignment.copy()

    while True:
        unit_clause_literal = None

        # Look for a unit clause or an immediate conflict
        for clause in clauses:
            # tautology clause, skip it
            s = set(clause)
            if any(-lit in s for lit in s):
                continue

            # If clause already satisfied by current assignment, skip it
            clause_satisfied = False
            for lit in clause:
                if abs(lit) in assignment:
                    val = assignment[abs(lit)]
                    if (lit > 0 and val) or (lit < 0 and not val):
                        clause_satisfied = True
                        break
            if clause_satisfied:
                continue

            # collect literals with unassigned variables
            unassigned_literals = [lit for lit in clause if abs(lit) not in assignment]
            unique_unassigned = set(unassigned_literals)

            # If no unassigned literals and clause not satisfied -> conflict
            if len(unique_unassigned) == 0:
                return clauses, assignment, True

            # If exactly one unassigned literal -> unit clause
            if len(unique_unassigned) == 1:
                unit_clause_literal = next(iter(unique_unassigned))
                break

        if unit_clause_literal is None:
            # no unit clause found -> fixpoint
            break

        # apply assignment forced by unit clause (preserve sign)
        var = abs(unit_clause_literal)
        value = unit_clause_literal > 0
        # If var already assigned inconsistently -> conflict
        if var in assignment:
            if assignment[var] != value:
                return clauses, assignment, True
            # else already set to same value -> continue
        else:
            assignment[var] = value

        # simplify formula with that literal set true
        clauses = simplify(clauses, unit_clause_literal)

        # After simplification if any empty clause exists -> conflict
        for c in clauses:
            if len(c) == 0:
                return clauses, assignment, True

    return clauses, assignment, False

def ClausesSatisfied(formula, assignment):
    if (len(assignment) != formula.numClauses):
        print("Error: Assignment length does not match number of clauses.")
        return -1
    clausesatisfied = 0;
    clausenum = -1
    #print(f"Assignment is {assignment}")
    for clause in formula.clausesRaw:
        clausenum += 1
        varnum = -1
        varsatisfied = 0
        for var in clause:
            varnum += 1
            assignmentsign = assignment[var-1]
            clausesign = formula.clausesNegation[clausenum][varnum]
            #print(f"Var: {var}, Assignmentsign: {assignmentsign}, Clausesign: {clausesign}")
            assignmentsign = int(assignmentsign)
            if (assignmentsign == clausesign):
                #print("Variable Satisfied")
                varsatisfied = 1
        if (varsatisfied >= 1):
            clausesatisfied += 1
            #print(f"Clause {clausenum} satisfied")
        else:
            pass
            #print(f"Clause {clausenum} not satisfied")

    #print(f"Clauses satisfied: {clausesatisfied} out of {formula.numClauses}")
    return clausesatisfied
           
            

def LocalSearch(formula, maxflips):
    # Initialize assignment: "1 or 0" for each variable
    assignment = ""
    satisfiedlist = []
    for i in range(formula.numClauses):
        if random.choice([True, False]) == True:
            assignment += "1"
        else: 
            assignment += "0"

        
    #print(f"Initial assignment: {assignment}")

    best_assignment = assignment
    best_satisfied = ClausesSatisfied(formula, assignment)

    for i in range(maxflips):
        improved = False
        for j in range(len(assignment)):
            # flip bit j
            flipped = '1' if assignment[j] == '0' else '0'
            assignmenttemp = assignment[:j] + flipped + assignment[j+1:]
            numsatisfied = ClausesSatisfied(formula, assignmenttemp)

            # keep best found so far
            if numsatisfied > best_satisfied:
                best_satisfied = numsatisfied
                best_assignment = assignmenttemp
                improved = True

        # update assignment if we found a better one
        if improved:
            assignment = best_assignment

        #print(f"After flip {i}, best assignment has {best_satisfied} clauses satisfied")
    finalsatisfied = ClausesSatisfied(formula, assignment)
    #print(f"\n\nFINAL ASSIGNMENT: {finalsatisfied} clauses satisfied")
    #print(f"Total Clauses: {formula.numClauses}")
    #print(f"Final assignment: {assignment}")
    return assignment


def GeneticAlgorithm(formula, population_size, generations):
    
    # Initialize afflicting vars
    assignment = ""
    population_group = []
    clauses_satisfied_group = []
    inverted_prob_group = []
    mutation_proportion = 0.01

    # Creating the amount of population to reproduce each generation
    # 20% will be culled, and the rest will reproduce to maintain population size
    crossover_amount = int(population_size / 3)

    # Create initial population
    for i in range(population_size):
        assignment = ""  # reset each time
        for j in range(formula.numClauses):  # or formula.numVariables if that's what you meant
            if random.choice([True, False]) == True:
                assignment += "1"
            else: 
                assignment += "0"

        numsatisfied = ClausesSatisfied(formula, assignment)
        population_group.append(assignment)
        clauses_satisfied_group.append(numsatisfied)
    

    # Cull and breed over generations
    for gen in range(generations):  # changed i -> gen to avoid reusing

        # Generate new population from current population (Random assignment selection)
        for x in range(crossover_amount):  

            # Tournament selection for parents
            tournament_size = 3
            tournament_selection = []
            for t in range(tournament_size):
                rand_index = random.randint(0, len(population_group) - 1)
                tournament_selection.append((population_group[rand_index], clauses_satisfied_group[rand_index]))
            father = max(tournament_selection, key=lambda item: item[1])[0]
            tournament_selection = []
            for t in range(tournament_size):
                rand_index = random.randint(0, len(population_group) - 1)
                tournament_selection.append((population_group[rand_index], clauses_satisfied_group[rand_index]))
            mother = max(tournament_selection, key=lambda item: item[1])[0]


            assignment = ""  # reset before building new one
            # 50% chance for each bit to come from either parent
            for j in range(len(father)):
                if random.choice([True, False]) == True:
                    assignment += father[j]
                else: 
                    assignment += mother[j]

            # Adding other data of assignment to array
            numsatisfied = ClausesSatisfied(formula, assignment)
            population_group.append(assignment)
            clauses_satisfied_group.append(numsatisfied)
        
        # Create inverted probabilities for culling
        inverted_prob_group = []  # reset this list each generation
        for j in range(len(population_group)):
            inverted_prob = formula.numClauses - clauses_satisfied_group[j]
            inverted_prob_group.append(inverted_prob)

        # Mutate some assignments in population
        for j in range(len(population_group)):
            bits = list(population_group[j])  # convert to list for mutability
            for k in range(len(bits)):
                if random.random() <= mutation_proportion:
                    # Flip bit
                    bits[k] = '1' if bits[k] == '0' else '0'
            population_group[j] = ''.join(bits)
            # Update clauses satisfied after mutation
            clauses_satisfied_group[j] = ClausesSatisfied(formula, population_group[j])

        # Cull the assignments from population (Weighted to remove assignments that satisfy less clauses)
        for j in range(crossover_amount):
            total_satisfied_gen = sum(inverted_prob_group)
            chosen_assignment = random.randint(1, total_satisfied_gen)  # fixed random.randint
            i = 0
            while(chosen_assignment > inverted_prob_group[i]):
                chosen_assignment -= inverted_prob_group[i]
            del population_group[i]
            del clauses_satisfied_group[i]
            del inverted_prob_group[i]
        max_satisfied_index = clauses_satisfied_group.index(max(clauses_satisfied_group))
        #print(f"Final best assignment: {population_group[max_satisfied_index]} \nWith {max(clauses_satisfied_group)} clauses satisfied \nOut of {formula.numClauses}")

    return population_group[max_satisfied_index]
