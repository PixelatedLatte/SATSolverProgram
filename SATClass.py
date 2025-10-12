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
    def init(self, parent, clause):
        self.parent = parent
        self.clause = clause

def dpll(clauses, assignment):
    clauses, assignment, isConflict = unitPropagation(clauses, assignment)

    # Local contradiction
    if isConflict:
        return False, None   # conflict -> backtrack

    # Fully satisfied
    if not clauses:
        return True, assignment

    literal = pickUnassignedLiteral(clauses, assignment)

    # Try literal = True
    result, solution = dpll(to_cnf(clauses), {**assignment, literal: True})
    if result:
        return True, solution

    # If first branch failed (conflict in every subpath), try False
    result, solution = dpll(to_cnf(clauses), {**assignment, literal: False})
    if result:
        return True, solution

    # Both branches failed (conflicts everywhere)
    return False, None   # GLOBAL unsatisfiability
    
#def simplify(clauses, literal):
    

def pickUnassignedLiteral(clauses, assignment):
    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                return var
    return None  # All variables assigned

def unitPropagation(clauses, assignment):
    changed = True

    while changed:
        changed = False
        unit_clause_literal = None

        # Step 1: Find a unit clause
        for clause in clauses:
            # Track clause satisfaction and remaining unassigned literals
            unassigned_literals = []
            clause_satisfied = False

            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    # Clause satisfied if literal matches current assignment
                    if (lit > 0 and assignment[var]) or (lit < 0 and not assignment[var]):
                        clause_satisfied = True
                        break
                    # Otherwise, literal is false under current assignment
                else:
                    unassigned_literals.append(lit)

            if clause_satisfied:
                continue

            # Clause contradicted: all literals false under current assignment
            if len(unassigned_literals) == 0:
                return clauses, assignment, True  # conflict detected

            # Unit clause found
            if len(unassigned_literals) == 1:
                unit_clause_literal = unassigned_literals[0]
                break

        # Step 2: If no unit clauses remain, propagation is done
        if unit_clause_literal is None:
            break

        # Step 3: Apply the forced assignment
        val = unit_clause_literal > 0
        assignment[abs(unit_clause_literal)] = val
        changed = True

        # Step 4: Simplify the formula
        new_clauses = []
        for clause in clauses:
            # Clause satisfied — skip
            if unit_clause_literal in clause:
                continue
            # Remove falsified literal from other clauses
            if -unit_clause_literal in clause:
                new_clause = [lit for lit in clause if lit != -unit_clause_literal]
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)
        clauses = new_clauses

    return clauses, assignment, False