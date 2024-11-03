from FAdo.fa import *

def members(dfa, word):
    sigma = set(x for x in word)
    if not (sigma & dfa.Sigma) or sigma - dfa.Sigma:
       return False

    return dfa.evalWordP(word)

def generateRandomWord(dfa):
    return dfa.witness()

def checkEquvivalence(dfa1, dfa2):
    if dfa1 == dfa2:
        return True

    dfaDif = dfa1 & dfa2

    if dfaDif.isEmpty():
        difDfa = dfa2 & dfa1
        return generateRandomWord(difDfa)

    return generateRandomWord(dfaDif)

    