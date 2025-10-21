import random
import time
import sys
sys.path.append(".")
from SATClass import dpll

def generate_planted_cnf(num_vars, num_clauses, k=3, seed=None):
    """
    Generate k-SAT clauses guaranteed to be satisfied by a random planted assignment.
    Returns (clauses, planted_assignment_dict).
    """
    if seed is not None:
        random.seed(seed)
    planted = {i: random.choice([False, True]) for i in range(1, num_vars+1)}
    clauses = []
    vars_range = list(range(1, num_vars+1))
    for _ in range(num_clauses):
        clause_vars = random.sample(vars_range, min(k, num_vars))
        lits = []
        for v in clause_vars:
            # choose sign randomly; we'll fix later to ensure clause satisfied by planted
            sign = random.choice([1, -1])
            lits.append(sign * v)
        # ensure at least one literal satisfied by planted
        if not any(((lit > 0 and planted[abs(lit)]) or (lit < 0 and not planted[abs(lit)])) for lit in lits):
            v = random.choice(clause_vars)
            # set sign to satisfy planted[v]
            lits = [lit for lit in lits if abs(lit) != v]  # remove any existing same var
            lits.append(v if planted[v] else -v)
        clauses.append(lits)
    return clauses, planted

def generate_unit_heavy_cnf(num_vars, num_units, extra_clauses, seed=None):
    """
    Create a formula that forces many variables via unit clauses (consistent),
    then add some additional clauses satisfied by the forced assignment.
    """
    if seed is not None:
        random.seed(seed)
    planted = {i: random.choice([False, True]) for i in range(1, num_vars+1)}
    clauses = []
    forced_vars = random.sample(list(planted.keys()), min(num_units, num_vars))
    for v in forced_vars:
        clauses.append([v if planted[v] else -v])  # unit clause
    # extra clauses that are satisfied by planted assignment
    for _ in range(extra_clauses):
        k = random.randint(2, 4)
        clause_vars = random.sample(list(planted.keys()), min(k, num_vars))
        lits = []
        for v in clause_vars:
            sign = random.choice([1, -1])
            lits.append(sign * v)
        # guarantee satisfaction by planted
        if not any(((lit > 0 and planted[abs(lit)]) or (lit < 0 and not planted[abs(lit)])) for lit in lits):
            v = random.choice(clause_vars)
            lits = [lit for lit in lits if abs(lit) != v]
            lits.append(v if planted[v] else -v)
        clauses.append(lits)
    return clauses, planted

def verify_with_planted(clauses, dpll_assignment, planted):
    """
    Verify that every clause is satisfied by the combination of
    dpll_assignment (partial) and planted for missing vars.
    Returns (ok, failed_clause_index, failed_clause).
    """
    for idx, clause in enumerate(clauses):
        sat = False
        for lit in clause:
            var = abs(lit)
            if dpll_assignment is not None and var in dpll_assignment:
                val = dpll_assignment[var]
            else:
                val = planted[var]
            if (lit > 0 and val) or (lit < 0 and not val):
                sat = True
                break
        if not sat:
            return False, idx, clause
    return True, None, None

def run_planted_tests(sizes, clauses_per_var_ratio=4, k=3, trials=3, seed_base=0):
    print("Running planted-solution tests (known satisfiable).")
    for n in sizes:
        m = max(1, int(n * clauses_per_var_ratio))
        for t in range(trials):
            seed = seed_base + n + t
            clauses, planted = generate_planted_cnf(n, m, k=k, seed=seed)
            t0 = time.time()
            sat, assign = dpll([list(c) for c in clauses], {})
            t1 = time.time()
            ok = False
            if not sat:
                print(f"[FAIL] n={n} m={m} k={k} trial={t} -> dpll returned UNSAT (expected SAT). time={t1-t0:.3f}s")
                print("  sample clauses (first 8):", clauses[:8])
            else:
                ok, fail_idx, fail_clause = verify_with_planted(clauses, assign or {}, planted)
                if not ok:
                    print(f"[FAIL-ASSIGN] n={n} m={m} trial={t} -> dpll returned SAT but assignment does NOT satisfy all clauses.")
                    print("  failed clause idx:", fail_idx, "clause:", fail_clause)
                    print("  dpll partial assignment (len):", 0 if assign is None else len(assign))
                else:
                    print(f"[OK] n={n} m={m} trial={t} -> SAT verified. time={t1-t0:.3f}s  assigned_vars={0 if assign is None else len(assign)}")
    print("Planted tests done.\n")

def run_unit_heavy_tests(sizes, num_units_fraction=0.5, extra_clauses=50, trials=3, seed_base=1000):
    print("Running unit-heavy tests (many forced assignments).")
    for n in sizes:
        num_units = int(n * num_units_fraction)
        for t in range(trials):
            seed = seed_base + n + t
            clauses, planted = generate_unit_heavy_cnf(n, num_units, extra_clauses, seed=seed)
            t0 = time.time()
            sat, assign = dpll([list(c) for c in clauses], {})
            t1 = time.time()
            if not sat:
                print(f"[FAIL-UNIT] n={n} units={num_units} trial={t} -> dpll returned UNSAT (expected SAT). time={t1-t0:.3f}s")
            else:
                ok, fail_idx, fail_clause = verify_with_planted(clauses, assign or {}, planted)
                if not ok:
                    print(f"[FAIL-ASSIGN-UNIT] n={n} units={num_units} trial={t} -> SAT but assignment invalid for clause {fail_idx}: {fail_clause}")
                else:
                    print(f"[OK-UNIT] n={n} units={num_units} trial={t} SAT verified. time={t1-t0:.3f}s assigned_vars={0 if assign is None else len(assign)}")
    print("Unit-heavy tests done.\n")

def run_random_density_tests(sizes, density_factors, trials=3, seed_base=2000):
    """
    Random CNFs without planted solution: only sanity checks (if dpll says SAT, verify assignment).
    density_factors: list of m/n multipliers
    """
    print("Running random density tests (sanity checks).")
    for n in sizes:
        for dens in density_factors:
            m = max(1, int(n * dens))
            for t in range(trials):
                random.seed(seed_base + n + t)
                clauses = []
                for _ in range(m):
                    k = 3
                    vs = random.sample(range(1, n+1), min(k, n))
                    clause = []
                    for v in vs:
                        clause.append(v if random.choice([True, False]) else -v)
                    clauses.append(clause)
                t0 = time.time()
                sat, assign = dpll([list(c) for c in clauses], {})
                t1 = time.time()
                if sat:
                    # Verify returned assignment actually satisfies clauses (treat missing as unknown -> fail if any clause unsatisfied)
                    ok = True
                    for clause in clauses:
                        clause_ok = False
                        for lit in clause:
                            var = abs(lit)
                            if assign is None or var not in assign:
                                # cannot fully verify; skip this check for completeness
                                clause_ok = True
                                break
                            val = assign[var]
                            if (lit > 0 and val) or (lit < 0 and not val):
                                clause_ok = True
                                break
                        if not clause_ok:
                            ok = False
                            print(f"[RANDOM-MISMATCH] n={n} m={m} trial={t} -> dpll says SAT but assignment doesn't satisfy clause {clause}")
                            break
                    if ok:
                        print(f"[RANDOM-SAT] n={n} m={m} dens={dens:.2f} trial={t} -> SAT verified (partial). time={t1-t0:.3f}s assigned_vars={0 if assign is None else len(assign)}")
                else:
                    print(f"[RANDOM-UNSAT] n={n} m={m} dens={dens:.2f} trial={t} -> UNSAT. time={t1-t0:.3f}s")
    print("Random density tests done.\n")

if __name__ == "__main__":
    # sizes and parameters — tune up to your machine limits.
    planted_sizes = [20, 50, 100, 200]   # variable counts
    unit_sizes = [50, 100, 200]
    random_sizes = [50, 100]
    try:
        run_planted_tests(planted_sizes, clauses_per_var_ratio=4, k=3, trials=3)
        run_unit_heavy_tests(unit_sizes, num_units_fraction=0.6, extra_clauses=200, trials=2)
        run_random_density_tests(random_sizes, density_factors=[3.0, 4.5], trials=2)
    except KeyboardInterrupt:
        print("Interrupted by user.")