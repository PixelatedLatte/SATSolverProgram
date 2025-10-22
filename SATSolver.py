"""
Description: A simple SAT solver using the DPLL algorithm, and more
"""
import copy
import glob
import os
import random
import time
import csv
import pandas as pd
from re import A
from stringprep import in_table_a1
from SATClass import *
import SATClass

def load_cnf_files(folder_path, file_list):
    # Search for all .cnf files in the specified folder and its subfolders (in github repo)
    for file_path in glob.glob(os.path.join(folder_path, '**', '*.cnf'), recursive=True):
        file_list.append(file_path)
    return file_list


def read_cnf_files(file_list):
    #Read CNF files into File class objects and return a list of those objects.

    file_objects = []

    for file_path in file_list:
        clauses = []  # Reset clause list for each file
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('c'):
                    continue
                # Grab the p line data
                if line.startswith('p'):
                    parts = line.split()
                    num_vars = int(parts[2])
                    num_clauses = int(parts[3])
                    continue
                # Grab a clause line (formatted as space-separated integers ending with 0)
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

        # Build File object and add to list (This is our meat and taters) and append to array
        file_info = File(file_path, len(clauses), num_vars, clauses, negated_clauses, original_clauses)
        file_objects.append(file_info)

        print(f"Loaded File: {file_path:40} | Contains: {len(clauses):3} clauses.")

    return file_objects

def create_negation(formula):
    # Create the negation of the formula by flipping the literals in each clause ([1,-2,3] becomes [1,2,3] and [1,0,1])])
    # Will also convert all literals to their absolute values for easier processing later (makes it easier to grab variable)
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

def update_running_avg(run, avg, run_index):
    # run_index: number of previous runs already included (0-based)
    for i, v in enumerate(run):
        if i >= len(avg):
            avg.append(v)
        else:
            avg[i] = (avg[i] * run_index + v) / (run_index + 1)
def main():
    # initialize variables
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


    dpllTimes = []
    for formula in hard_formulas:
        startTime = time.time()
        print(f"Hard Formula: {formula.fileN}\n {formula.clausesOriginal}\n")

        formula.clausesOriginal, assignments = dpll(formula.clausesOriginal, assignments)

        print(f"Assignments: {assignments}")
        endTime = time.time()
        print(f"Time to solve {formula.fileN} using DPLL: {endTime - startTime} seconds\n")
        dpllTimes.append(endTime-startTime)

    # Genetic alg initializers
    population_size = 100
    generations = 150
    # 1% chance for an assignement to mutate 1 bit, 1/3 of population will be culled each generation
    mutation_proportion = .02
    crossover_amount = int(population_size / 3)

    # Creates lists to hold average results + times
    FormulasCompleted = []
    ClausesSatisfiedLocalSearchList = []
    ClausesSatisfiedGeneticAlgList = []
    AverageClausesLocal = []
    AverageTimeLocal = []
    AverageClausesGenetic = []
    AverageTimeGenetic = []
    for i in range(0,5):
        ProportionClausesLocal = []
        ProportionClausesGenetic = []
        TotalTimesLocal = []
        TotalTimesGenetic = []
        for formula in hard_formulas:
            startTime = time.time()
            LocalSearchBest = SATClass.LocalSearch(formula)
            endTime = time.time()
            LocalSearchTime = endTime - startTime
            print(f"Time taken for Local Search on {formula.fileN}: {LocalSearchTime:.3f} seconds")
            TotalTimesLocal.append(LocalSearchTime)

            localBestCount = ClausesSatisfied(formula, LocalSearchBest)
            print(f"Proportion of clauses satisfied by Local Search on {formula.fileN}: {localBestCount/formula.numClauses:.2f}\n")
            ProportionClausesLocal.append(localBestCount/formula.numClauses)

            startTime = time.time()
            GeneticAlgBest = SATClass.GeneticAlgorithm(formula, population_size, generations, mutation_proportion, crossover_amount)
            endTime = time.time()
            GeneticAlgTime = endTime - startTime
            print(f"Time taken for Genetic Algorithm on {formula.fileN}: {GeneticAlgTime:.3f} seconds\n")
            TotalTimesGenetic.append(GeneticAlgTime)

            geneticBestCount = ClausesSatisfied(formula, GeneticAlgBest)
            print(f"Proportion of clauses satisfied by Genetic Algorithm on {formula.fileN}: {geneticBestCount/formula.numClauses:.2f}\n")
            ProportionClausesGenetic.append(geneticBestCount/formula.numClauses)

            print(f"\nLocal Search Best Assignment for {formula.fileN}: {SATClass.ClausesSatisfied(formula, LocalSearchBest)}/{formula.numClauses}\n")
            print(f"Genetic Algorithm Best Assignment for {formula.fileN}: {SATClass.ClausesSatisfied(formula, GeneticAlgBest)}/{formula.numClauses}\n")
            FormulasCompleted.append(formula.fileN)
            ClausesSatisfiedLocalSearchList.append(SATClass.ClausesSatisfied(formula, LocalSearchBest))
            ClausesSatisfiedGeneticAlgList.append(SATClass.ClausesSatisfied(formula, GeneticAlgBest))
        update_running_avg(ProportionClausesLocal, AverageClausesLocal, i)
        update_running_avg(TotalTimesLocal, AverageTimeLocal, i)
        update_running_avg(ProportionClausesGenetic, AverageClausesGenetic, i)
        update_running_avg(TotalTimesGenetic, AverageTimeGenetic, i)

    n = len(TotalTimesLocal)
    # build the rows
    rows = []
    for i in range(n):
        # Local Search row for formula i
        rows.append({
            "Formula": i,                      # number starting at 0
            "Algorithm": "Local Search",
            "Clauses Prop": AverageClausesLocal[i],
            "Time": AverageTimeLocal[i]
        })
        # Genetic row for formula i
        rows.append({
            "Formula": i,
            "Algorithm": "Genetic",
            "Clauses Prop": AverageClausesGenetic[i],
            "Time": AverageTimeGenetic[i]
        })

        rows.append({
            "Formula": i,
            "Algorithm": "DPLL",
            "Clauses Prop": None,
            "Time": dpllTimes[i]
         })

    # create DataFrame and save to CSV
    df = pd.DataFrame(rows, columns=["Formula", "Algorithm", "Clauses Prop", "Time"])
    df["Clauses Prop"] = df["Clauses Prop"].round(4)
    df["Time"] = df["Time"].round(4)
    df.to_csv("results_by_formula.csv", index=False)

    print("Saved results_by_formula.csv with", len(df), "rows.")
    print(df)

main()