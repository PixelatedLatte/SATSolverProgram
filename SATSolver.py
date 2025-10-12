'''
    Description: A simple SAT solver using the DPLL algorithm, and more
'''


# Search recursively for all .cnf files
def load_cnf_files(folder_path, filearray):
    for file in glob.glob(os.path.join(folder_path, '**', '*.cnf'), recursive=True):
        filearray.append(file)
        print(file)
    return filearray

def read_cnf_files(filearray):
    # Variable to store all files objects and return them
    fileObjects = []
    for file in filearray:
        with open(file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('c'):
                    continue
                # Read the problem line
                if line.startswith('p'):
                    parts = line.split()
                    num_vars = int(parts[2])
                    num_clauses = int(parts[3])
                    continue
                # Parse a clause
                clause = list(map(int, line.split()))
                if clause[-1] == 0:
                    clause = clause[:-1]  # Remove the trailing 0
                clauses.append(clause)
                # Stop after reading all clauses listed in the header
                if len(clauses) >= num_clauses:
                    break
        #Clauses negation for File class
        clauseNegation = [[-lit for lit in clause] for clause in clauses]

        #Build File object and input into fileObjects array
        fileInfo = File(file, len(clauses), clauses, clauseNegation)
        fileObjects.append(fileInfo)

        print(f"Loaded {len(clauses)} clauses with {num_vars} variables.")
        print("Example clause:", clauses[0])
    return fileObjects

import glob
import os
from SATClass import *

assignments = {}
easyfiles = []
hardfiles = []
clauses = []
# glob.glob() return a list of file name with specified pathname
easy_folder_path = r'CNF Formulas'
hard_folder_path = r'HARD CNF Formulas'

easyfiles = load_cnf_files(easy_folder_path, easyfiles)
hardfiles = load_cnf_files(hard_folder_path, hardfiles)

#easy and hard formulas are File class objects
easyFormulas = read_cnf_files(easyfiles)
hardFormulas = read_cnf_files(hardfiles)

print(f"Hard formula 0: {hardFormulas[7].clausesRaw}\n\n")

hardFormulas[7].clausesRaw, assignments, isConflict = unitPropagation(hardFormulas[7].clausesRaw, assignments)

print(f"After unit propagation: {hardFormulas[7].clausesRaw} \n\nand assignments: {assignments}, conflict: {isConflict}")