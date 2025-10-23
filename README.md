# SATSolverProgram Using DPLL, Genetic Algorithm, and Local Search
This is a program that uses the below algorithms to solve the SAT formulas in the HARD CNF formulas folder and CNF Formulas folder:
Do note that running times may vary from machine to machine and formula to formula, the SAT Solver in question, DPLL, does not work correctly
on all formulas, the reasoning for this is because the partial assignments are not evaluated correctly after each call and some formulas 
that should be satisfiable are found as unsatisfiable. Besides this, all formulas found as satisfiable should be correct and 
were loosely verified that the DPLL implementation works correctly on satisfiable formulas given the easy formulas. 
## Overview
This program implements three heuristic search techniques to solve the Boolean Satisfiability Problem (SAT):
1. DPLL (Davis-Putnam-Logemann-Loveland) Algorithm
2. Genetic Algorithm
3. Local Search

## How to Run
1. Ensure you have Python installed on your machine.
2. Install pandas library if you don't have it already:
   ```
   pip install pandas
   ```
3. Make sure all CNF Formula Folders are in the folder you run the program from,HARD CNF Formulas is the important one. 
	(Should have 2, "CNF Formulas" and "HARD CNF Formulas")
4. No requirements to install, you can just run SATSolver.py
																			
	Run the program using the command:
		```
	    python SATSolver.py
		```
    or run in an IDE of your choice.
5. Feel free to run the program multiple times to see different results for the Genetic Algorithm and Local Search
   It is currently limited to one run of the Genetic Algorithm and Local Search for time sake, but you can modify the
   for loops range if you want to run it multiple times. DPLL does not have randomness, so additional runs of the code
   yields the same results