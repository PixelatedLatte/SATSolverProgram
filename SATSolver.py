"""
Description: A simple SAT solver using the DPLL algorithm, and more
"""
import copy
import glob
import os
import random
import time
import csv
import numpy as np
from re import A
from stringprep import in_table_a1
from SATClass import *
import SATClass

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

        # creating original clauses copy for DPLL use
        original_clauses = copy.deepcopy(clauses)

        # Build File object and add to list
        file_info = File(file_path, len(clauses), num_vars, clauses, negated_clauses, original_clauses)
        file_objects.append(file_info)

        print(f"Loaded File: {file_path:40} | Contains: {len(clauses):3} clauses.")

    return file_objects

def create_negation(formula):
    formula.clausesNegation = copy.deepcopy(formula.clausesRaw)
    for clause in formula.clausesNegation:
            for i in range(len(clause)):
                if clause[i] > 0:
                    clause[i] = 1
                else:
                    clause[i] = 0
    for clause in formula.clausesRaw:
        for i in range(len(clause)):
            clause[i] = abs(clause[i])
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

'''
startTime = time.time()
for formula in easy_formulas:
    print(f"Easy Formula: {formula.fileN}\n {formula.clausesOriginal}\n")

    formula.clausesOriginal, assignments = dpll(formula.clausesOriginal, assignments)

    print(f"Assignments: {assignments}")
endTime = time.time()
print(f"Time taken to create negations for hard formulas: {endTime - startTime} seconds")
'''
population_size = 100
generations = 150
# 1% chance for an assignement to mutate 1 bit, 1/3 of population will be culled each generation
mutation_proportion = .02
crossover_amount = int(population_size / 3)
FormulasCompleted = []
ClausesSatisfiedLocalSearchList = []
ClausesSatisfiedGeneticAlgList = []
ProportionClauses = []
totalTimes = []
for formula in hard_formulas:
    startTime = time.time()
    LocalSearchBest = SATClass.LocalSearch(formula)
    endTime = time.time()
    print(f"Time taken for Local Search on {formula.fileN}: {endTime - startTime:.3f} seconds")
    totalTimes.append(endTime-startTime)

    localBestCount = ClausesSatisfied(formula, LocalSearchBest)
    print(f"Proportion of clauses satisfied by Local Search on {formula.fileN}: {localBestCount/formula.numClauses:.2f}")
    ProportionClauses.append(localBestCount/formula.numClauses)

    startTime = time.time()
    GeneticAlgBest = SATClass.GeneticAlgorithm(formula, population_size, generations, mutation_proportion, crossover_amount)
    endTime = time.time()
    print(f"Time taken for Genetic Algorithm on {formula.fileN}: {endTime - startTime:.3f} seconds")
    totalTimes.append(endTime-startTime)

    geneticBestCount = ClausesSatisfied(formula, GeneticAlgBest)
    print(f"Proportion of clauses satisfied by Genetic Algorithm on {formula.fileN}: {geneticBestCount/formula.numClauses:.2f}")


    print(f"\nLocal Search Best Assignment for {formula.fileN}: {SATClass.ClausesSatisfied(formula, LocalSearchBest)}/{formula.numClauses}")
    print(f"Genetic Algorithm Best Assignment for {formula.fileN}: {SATClass.ClausesSatisfied(formula, GeneticAlgBest)}/{formula.numClauses}")
    FormulasCompleted.append(formula.fileN)
    ClausesSatisfiedLocalSearchList.append(SATClass.ClausesSatisfied(formula, LocalSearchBest))
    ClausesSatisfiedGeneticAlgList.append(SATClass.ClausesSatisfied(formula, GeneticAlgBest))
