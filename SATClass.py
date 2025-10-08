'''
    Desc: Defines the classes used by the SAT solver for DPLL algorithm
'''
from fileinput import filename
import numpy as np

class File:
    def __init__(self, fileN, numClauses, clausesRaw, clausesNegation):
        self.fileN = fileN
        self.numClauses = numClauses
        self.clausesRaw = clausesRaw
        self.clausesNegation = clausesNegation
