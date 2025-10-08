'''
    Desc: Defines the classes used by the SAT solver for DPLL algorithm
'''
from fileinput import filename
import numpy as np

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
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value