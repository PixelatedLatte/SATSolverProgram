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
2. Make sure all CNF Formula Folders are in the folder you run the program from. 
	(Should have 2, "CNF Formulas" and "HARD CNF Formulas")
3. No requirements to install, you can just run SATSolver.py
																			
	Run the program using the command:
		```
	    python SATSolver.py
		```
    or run in an IDE of your choice.