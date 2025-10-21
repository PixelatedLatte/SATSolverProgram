import itertools
import sys
sys.path.append(".")

from SATClass import dpll

def brute_force_sat(clauses, num_vars):
    """
    Brute force search for a satisfying assignment.
    clauses: list[list[int]]
    num_vars: int
    Returns (True, assignment_dict) if satisfiable else (False, None).
    """
    for bits in itertools.product([False, True], repeat=num_vars):
        assignment = {i+1: bits[i] for i in range(num_vars)}
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True, assignment
    return False, None

def run_case(clauses, num_vars, name):
    print("=== Test:", name)
    print("clauses:", clauses)
    expected_sat, expected_assign = brute_force_sat(clauses, num_vars)
    result_sat, result_assign = dpll([list(c) for c in clauses], {})  # clean inputs

    print("Expected SAT:", expected_sat)
    if expected_sat:
        print("Expected example assignment:", expected_assign)
    print("DPLL reported SAT:", result_sat)
    print("DPLL assignment:", result_assign)

    # Normalize result_assign for checking (dpll returns dict var->bool or None)
    if result_sat and result_assign is None:
        print("WARNING: dpll returned True but assignment is None")
    if (expected_sat != result_sat):
        print(">>> MISMATCH: dpll disagree with brute force on satisfiability")
        return False

    if expected_sat and result_sat:
        # verify dpll assignment actually satisfies formula
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = result_assign.get(var)
                if val is None:
                    # some implementations return partial assignments; treat missing var as unknown
                    clause_ok = True
                    break
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                print(">>> MISMATCH: dpll assignment does NOT satisfy clause:", clause)
                return False
    print("OK\n")
    return True

def main():
    tests = []
    # trivial satisfiable: (x1)
    tests.append(([[1]], 1, "single positive literal"))

    # unsatisfiable: (x1) and (not x1)
    tests.append(([[1], [-1]], 1, "unit conflict"))

    # small satisfiable: (x1 or x2) and (not x1 or x2) and (not x2 or x3)
    tests.append(([[1,2], [-1,2], [-2,3]], 3, "small chain satisfiable"))

    # small unsatisfiable: (x1 or x2) AND (not x1 or x2) AND (x1 or not x2) AND (not x1 or not x2)
    # This is unsat (parity-like)
    tests.append(([[1,2], [-1,2], [1,-2], [-1,-2]], 2, "parity unsat"))

    # satisfiable with repeated literals and tautology
    tests.append(([[1, -1, 2], [2, 3], [-3]], 3, "contains tautology clause (first) but satisfiable"))

    # random small tests: generate a few random CNFs to stress
    import random
    random.seed(0)
    for i in range(10):
        num_vars = 4
        clauses = []
        num_clauses = random.randint(1,6)
        for _ in range(num_clauses):
            clause_len = random.randint(1,3)
            clause = []
            for _ in range(clause_len):
                v = random.randint(1, num_vars)
                lit = v if random.choice([True, False]) else -v
                clause.append(lit)
            clauses.append(list(set(clause)))  # remove duplicated same-signed literals
        tests.append((clauses, num_vars, f"random_{i}"))

    all_ok = True
    for clauses, num_vars, name in tests:
        ok = run_case(clauses, num_vars, name)
        if not ok:
            all_ok = False

    if not all_ok:
        print("Some tests failed — see mismatches above.")
    else:
        print("All tests passed on these small cases.")

if __name__ == "__main__":
    main()