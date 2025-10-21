'''
    Desc: Defines the classes used by the SAT solver for DPLL algorithm
'''
import copy
import glob
import os
import random
from re import A, S
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
    def __init__(self, fileN, numClauses, numVars, clausesRaw, clausesNegation, clausesOriginal):
        self.fileN = fileN
        self.numClauses = numClauses
        self.numVars = numVars
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
    def formula_fully_satisfied(clauses, assignment):
        # Return True iff every clause has at least one literal satisfied by assignment.
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var]
                    if (lit > 0 and val) or (lit < 0 and not val):
                        satisfied = True
                        break
            if not satisfied:
                return False
        return True

    stack = []
    root = Node(None, [list(c) for c in clauses], {} if assignment is None else assignment.copy())
    stack.append(root)

    while stack:
        node = stack.pop()
        # work on fresh copies to avoid shared mutation
        clauses = [list(c) for c in node.clauses]
        assignment = {} if node.assignment is None else node.assignment.copy()

        # Unit propagation
        clauses, assignment, isConflict = unitPropagation(clauses, assignment)
        if isConflict:
            continue  # Conflict, backtrack

        # If any empty clause exists -> conflict
        if any(len(c) == 0 for c in clauses):
            continue

        # If every clause is satisfied by the current (possibly partial) assignment -> success
        if formula_fully_satisfied(clauses, assignment):
            return True, assignment

        # Need to pick a variable to branch on
        literal = pickMostConstraining(clauses, assignment)
        if literal is None:
            # No unassigned variables appear in remaining clauses and formula wasn't fully satisfied -> treat as backtrack
            continue

        # Push False then True so True is popped/explored first
        new_assignment_false = assignment.copy()
        new_assignment_false[literal] = False
        stack.append(Node(node, simplify(clauses, -literal), new_assignment_false))

        new_assignment_true = assignment.copy()
        new_assignment_true[literal] = True
        stack.append(Node(node, simplify(clauses, literal), new_assignment_true))

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
    # If assignment length does not match number of variables, error + exit
    if (len(assignment) != formula.numVars):
        print("Error: Assignment length does not match number of variables.")
        return -1
    clausesatisfied = 0;
    clausenum = -1

    # For each clause in formula, check if satisfied by assignment
    for clause in formula.clausesRaw:
        clausenum += 1
        varnum = -1
        varsatisfied = 0
        # use clauseNegation (same size as clauseRaw), 
        # which replaces values such as [1, -3, 4] with [1, 0, 1] for easier checking]
        for var in clause:
            varnum += 1
            assignmentsign = assignment[var-1]
            clausesign = formula.clausesNegation[clausenum][varnum]
            assignmentsign = int(assignmentsign)
            if (assignmentsign == clausesign):
                varsatisfied = 1
        # if at least one variable evals to true, increment, clause is satisfied
        if (varsatisfied >= 1):
            clausesatisfied += 1
        else:
            pass
    return clausesatisfied
           
            

def LocalSearch(formula):
    # Initialize assignment: 50-50 for each var being a 1 or 0
    assignment = ""
    for i in range(formula.numVars):
        if random.choice([True, False]) == True:
            assignment += "1"
        else: 
            assignment += "0"
    
    # set best assignemnt and best satisfied clauses to be initial
    best_assignment = assignment
    best_satisfied = ClausesSatisfied(formula, assignment)
    improved = True

    # As long as we can improve number of clauses statisfied with only 1 bit flip, keep going
    while (improved == True):
        improved = False
        for j in range(len(assignment)):
            # Flip each individual bit and check if better
            if assignment[j] == "0":
                flipped = "1" 
            else:
                flipped = "0"
            assignmenttemp = assignment[:j] + flipped + assignment[j+1:]
            numsatisfied = ClausesSatisfied(formula, assignmenttemp)
            
            # if better, update bests and break to restart from beginning (no need to check rest of bitflip possibilities)
            if numsatisfied > best_satisfied:
                improved = True
                best_satisfied = numsatisfied
                assignment = assignmenttemp
                best_assignment = assignmenttemp
                break
    return best_assignment

def GeneticAlgorithm(formula, population_size, generations, mutation_proportion, crossover_amount):
    
    # Initialize empty arrays and first set of assignemnts
    assignment = ""
    population_group = []
    clauses_satisfied_group = []
    inverted_prob_group = []

    # Create initial population
    for i in range(population_size):
        assignment = ""  # reset each time
        for i in range(formula.numVars):  # Generates random string assignment that is the size of the # of vars in formula
            if random.choice([True, False]) == True:
                assignment += "1"
            else: 
                assignment += "0"

        numsatisfied = ClausesSatisfied(formula, assignment) # Also append their # of clauses satisfied + the actual assignment
        # Also append their # of clauses satisfied + the actual assignment
        population_group.append(assignment)
        clauses_satisfied_group.append(numsatisfied)
    
    # Breed to get pop + cullnum
    for gen in range(generations):
        # Generate new population from current population (Tournament selection for parents)
        for x in range(crossover_amount):  
            tournament_size = 3
            tournament_selection = []
            # Pick X num of random assigments, let the best fit once be the Father
            for t in range(tournament_size):
                rand_index = random.randint(0, len(population_group) - 1)
                tournament_selection.append((population_group[rand_index], clauses_satisfied_group[rand_index]))
            father = max(tournament_selection, key=lambda item: item[1])[0]
            # Reset and rerun for mom
            tournament_selection = []
            for t in range(tournament_size):
                rand_index = random.randint(0, len(population_group) - 1)
                tournament_selection.append((population_group[rand_index], clauses_satisfied_group[rand_index]))
            mother = max(tournament_selection, key=lambda item: item[1])[0]

            assignment = ""
            # 50% chance for each bit to come from either parent
            for j in range(len(father)):
                if random.choice([True, False]) == True:
                    assignment += father[j]
                else: 
                    assignment += mother[j]

            # Adding new assignments to population array
            numsatisfied = ClausesSatisfied(formula, assignment)
            population_group.append(assignment)
            clauses_satisfied_group.append(numsatisfied)

        # Mutate some assignments in population
        for pos in range(len(population_group)):
            if random.random() <= mutation_proportion:
                mutatepos = random.randint(0,formula.numVars-1)
                # Flip bit
                if population_group[pos][mutatepos] == "0":
                    flipped = "1"
                else:
                    flipped = "0"
                population_group[pos] = population_group[pos][:mutatepos] + flipped + population_group[pos][mutatepos+1:]
            # Update clauses satisfied after mutation
            clauses_satisfied_group[j] = ClausesSatisfied(formula, population_group[j])
        
        # Create inverted probabilities, which is the number of clauses NOT satisfied,
        # Divides by the total sum of clauses not satisfied from the whole population
        inverted_prob_group = []
        for j in range(len(population_group)):
            inverted_prob = formula.numClauses - clauses_satisfied_group[j]
            inverted_prob_group.append(inverted_prob)

        # Cull the assignments from population (Weighted to remove assignments that satisfy less clauses)
        for j in range(crossover_amount):
            total_satisfied_gen = sum(inverted_prob_group)
            chosen_assignment = random.randint(1, total_satisfied_gen)
            i = 0
            while i < len(inverted_prob_group) - 1 and chosen_assignment > inverted_prob_group[i]:
                chosen_assignment -= inverted_prob_group[i]
                i += 1
            # Remove selected weak individual
            del population_group[i]
            del clauses_satisfied_group[i]
            del inverted_prob_group[i]
        
        # return the best assignment after all generations complete
        max_satisfied_index = clauses_satisfied_group.index(max(clauses_satisfied_group))

    return population_group[max_satisfied_index]

