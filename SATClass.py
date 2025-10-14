'''
    Desc: Defines the classes used by the SAT solver for DPLL algorithm
'''
from sympy import *
'''
    File Class:
        fileN: Name of the file
        numClauses: Number of clauses in the file
        clausesRaw: Clauses as they are in the file
        clausesNegation: Negated clauses for DPLL algorithm
'''
class File:
    def __init__(self, fileN, numClauses, clausesRaw, clausesNegation):
        self.fileN = fileN
        self.numClauses = numClauses
        self.clausesRaw = clausesRaw
        self.clausesNegation = clausesNegation


'''
Node Class:
Parent: Parent node of current
value: Individual variable of current node
'''
class Node:
    def __init__(self, parent, clauses, assignment):
        self.parent = parent
        self.clauses = clauses
        self.assignment = assignment
'''
def dpll(clauses, assignment):
    clauses, assignment, isConflict = unitPropagation(clauses, assignment)

    # Local contradiction
    if isConflict:
        print("Did not find Solution...Conflict in this branch")
        return False, None   # conflict -> backtrack

    # Fully satisfied
    if not clauses:
        print("Found solution!!!")
        return True, assignment
    
    literal = pickUnassignedLiteral(clauses, assignment)

    # Try literal = True
    result, solution = dpll(simplify(clauses, literal), {**assignment, literal: True})
    if result:
        print("Found solution!!!")
        return True, solution

    # If first branch failed (conflict in every subpath), try False
    result, solution = dpll(simplify(clauses, literal), {**assignment, literal: False})
    if result:
        print("Found solution!!!")
        return True, solution

    # Both branches failed (conflicts everywhere)
    print("Did not find Solution...Conflict in all branches")
    return False, None   # GLOBAL unsatisfiability
'''
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

        literal = pickUnassignedLiteral(clauses, assignment)
        if literal is None:
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
    #given an assigned literal, remove all clauses in the formula that are satisfied by that literal
    if literal is None:
        return clauses

    #If the literal is positive, remove all clauses containing that literal
    if literal > 0:
        clauses = [clause for clause in clauses if literal not in clause]
    elif literal < 0:
        clauses = [[lit for lit in clause if lit >= 0] for clause in clauses]
    
    return clauses
    
def pickUnassignedLiteral(clauses, assignment):
    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                return var
    return None  # All variables assigned

def unitPropagation(clauses, assignment):
    assignment = assignment.copy()  # Avoid mutating input assignment
    while True:
        unit_clause_literal = None

        # Step 1: Find a unit clause
        for clause in clauses:
            unassigned_literals = [lit for lit in clause if abs(lit) not in assignment]
            clause_satisfied = any(
                (lit > 0 and assignment.get(abs(lit), None) is True) or
                (lit < 0 and assignment.get(abs(lit), None) is False)
                for lit in clause if abs(lit) in assignment
            )

            if clause_satisfied:
                continue

            if len(unassigned_literals) == 0:
                return clauses, assignment, True  # conflict detected

            if len(unassigned_literals) == 1:
                unit_clause_literal = unassigned_literals[0]
                break

        if unit_clause_literal is None:
            break  # No more unit clauses

        # Step 3: Apply the forced assignment
        assignment[abs(unit_clause_literal)] = unit_clause_literal > 0
        assignment[abs(unit_clause_literal)] = unit_clause_literal > 0

        # Step 4: Simplify the formula
        clauses = simplify(clauses, unit_clause_literal)

    return clauses, assignment, False