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
            print("Conflict in this branch, backtracking...")
            continue  # Conflict, backtrack

        if not clauses:
            print("Found solution!!!")
            return True, assignment  # Solution found

        literal = pickMostConstrained(clauses, assignment)
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
            count[lit] = count.get(lit, 0) + 1
    return count
#Picks the most constraining unassigned literal that has not been chosen yet
def pickMostConstrained(clauses, assignment):
    count = countLiteral(clauses)

    bestLit = None
    bestCount = -1
    for lit, cnt in count.items():
        if abs(lit) in assignment:
            continue # Literal already assigned
        if cnt > bestCount: # If found a better literal
            bestCount = cnt
            bestLit = abs(lit)
        if bestLit is not None: # If the best literal exists
            return bestLit
    return None  # All variables assigned

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

            # If no unassigned literals and clause not satisfied -> conflict
            if len(unassigned_literals) == 0:
                return clauses, assignment, True

            # If exactly one unassigned literal -> unit clause
            if len(unassigned_literals) == 1:
                unit_clause_literal = unassigned_literals[0]
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

        
    print(f"Initial assignment: {assignment}")

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

        print(f"After flip {i}, best assignment has {best_satisfied} clauses satisfied")
    finalsatisfied = ClausesSatisfied(formula, assignment)
    print(f"\n\nFINAL ASSIGNMENT: {finalsatisfied} clauses satisfied")
    print(f"Total Clauses: {formula.numClauses}")
    print(f"Final assignment: {assignment}")
    return assignment


def GeneticAlgorithm(formula, population_size, generations):
    # Initialize assignment
    assignment = ""
    population_group = []
    clauses_satisfied_group = []
    inverted_prob_group = []
    mutation_proportion = 0.02


    for i in range(population_size):
        for j in range(formula.numClauses):
            if random.choice([True, False]) == True:
                assignment += "1"
            else: 
                assignment += "0"

        numsatisfied = ClausesSatisfied(formula, assignment)
        population_group.append(assignment)
        clauses_satisfied_group.append(numsatisfied)

    print(f"Initial population: {population_group}")


    
    return assignment