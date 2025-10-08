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
        print(f"Loaded {len(clauses)} clauses with {num_vars} variables.")
        print("Example clause:", clauses[0])


import glob
import os

easyfiles = []
hardfiles = []
clauses = []
# glob.glob() return a list of file name with specified pathname
easy_folder_path = r'CNF Formulas'
hard_folder_path = r'HARD CNF Formulas'

easyfiles = load_cnf_files(easy_folder_path, easyfiles)
hardfiles = load_cnf_files(hard_folder_path, hardfiles)

read_cnf_files(easyfiles)
read_cnf_files(hardfiles)