"""
Description: A simple SAT solver using the DPLL algorithm, and more
"""
import copy
import glob
import os
import random
from stringprep import in_table_a1
from SATClass import *

def load_cnf_files(folder_path, file_list):
    """
    Recursively search a folder for all .cnf files and append them to file_list.
    """
    for file_path in glob.glob(os.path.join(folder_path, '**', '*.cnf'), recursive=True):
        file_list.append(file_path)
        #print(file_path)
    return file_list


def read_cnf_files(file_list):
    """
    Read CNF files into File class objects and return a list of those objects.
    """
    file_objects = []

    for file_path in file_list:
        clauses = []  # Reset clause list for each file
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('c'):
                    continue

                # Parse the problem line
                if line.startswith('p'):
                    parts = line.split()
                    num_vars = int(parts[2])
                    num_clauses = int(parts[3])
                    continue

                # Parse a clause line
                clause = list(map(int, line.split()))
                if clause[-1] == 0:
                    clause = clause[:-1]  # Remove the trailing 0
                clauses.append(clause)

                # Stop after reading all clauses listed in the header
                if len(clauses) >= num_clauses:
                    break

        # Just adding a dummy values until negation function is called later
        negated_clauses = copy.deepcopy(clauses)

        # Build File object and add to list
        file_info = File(file_path, len(clauses), clauses, negated_clauses)
        file_objects.append(file_info)

        print(f"Loaded File: {file_path:40} | Contains: {len(clauses):3} clauses.")

    return file_objects

def create_negation(formula):
    formula.clausesNegation = copy.deepcopy(formula.clausesRaw)
    for clause in formula.clausesNegation:
            #print(f"Creating negation of {clause}")
            for i in range(len(clause)):
                if clause[i] > 0:
                    clause[i] = 1
                else:
                    clause[i] = 0
    #print("\nAfter negation:")
    #for clause in formula.clausesNegation:
        #print(f"Pos or Neg variable: {clause}")
    for clause in formula.clausesRaw:
        #print(f"Original clause: {clause}")
        for i in range(len(clause)):
            clause[i] = abs(clause[i])
        #print(f"New clause: {clause}")

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

    print(f"Clauses satisfied: {clausesatisfied} out of {formula.numClauses}")
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


    # Evaluate initial assignment
    for i in range(maxflips):
        for j in range(len(assignment)):
            if (assignment[j] == "0"):
                assignmenttemp = assignment[:j] + "1" + assignment[(j+1):]
            else:
                assignmenttemp = assignment[:j] + "0" + assignment[(j+1):]
                numsatisfied = ClausesSatisfied(formula, assignmenttemp)
                satisfiedlist.append(numsatisfied)
                print(f"Initial satisfied clauses: {numsatisfied}")
        maxsatisfied = max(satisfiedlist)
        maxindex = satisfiedlist.index(maxsatisfied)
        print(f"Max satisfied clauses: {maxsatisfied} at index {maxindex}")
            
        if (assignment[maxindex] == "0"):
            assignment = assignment[:maxindex] + "1" + assignment[(maxindex+1):]
        else:
            assignment = assignment[:maxindex] + "0" + assignment[(maxindex+1):]

    finalsatisfied = ClausesSatisfied(formula, assignment)
    print(f"\n\nFINAL ASSIGNMENT: {finalsatisfied} clauses satisfied")
    print(f"Total Clauses: {formula.numClauses}")
    return assignment
     

assignments = {}
easy_files = []
hard_files = []

# Folder paths
easy_folder_path = r'CNF Formulas'
hard_folder_path = r'HARD CNF Formulas'

# Load file paths
easy_files = load_cnf_files(easy_folder_path, easy_files)
hard_files = load_cnf_files(hard_folder_path, hard_files)

# Read and parse CNF files into File class objects
easy_formulas = read_cnf_files(easy_files)
hard_formulas = read_cnf_files(hard_files)

# Create negations of the formulas
for formula in easy_formulas:
    create_negation(formula)

for formula in hard_formulas:
    create_negation(formula)

# Example: Print a specific formula’s clauses
print(f"Hard formula 7: {hard_formulas[7].fileN}\n {hard_formulas[7].clausesRaw}\n")

assignments[pickUnassignedLiteral(hard_formulas[7].clausesRaw, assignments)] = True
# Apply unit propagation
hard_formulas[7].clausesRaw, assignments = dpll(
    hard_formulas[7].clausesRaw, assignments
)


'''
print(
    f"After unit propagation:\n{hard_formulas[7].clausesRaw}\n\n"
    f"Assignments: {assignments}, Conflict: {is_conflict}"
)
'''

#LocalSearch(hard_formulas[7], 30)