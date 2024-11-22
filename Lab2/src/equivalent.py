from FAdo.fa import *

def members(dfa, word):
    sigma = set(x for x in word)
    if not (sigma & dfa.Sigma) or sigma - dfa.Sigma:
       return False

    return dfa.evalWordP(word)

def generateRandomWord(dfa):
    ln = random.randint(3, 50)
    words = dfa.enumDFA(idx)
    idx = random.randint(0, len(words))
    return words[idx]

def checkEquivalence(dfaMAT, dfaLearner):
    if dfaMAT == dfaLearner:
        return True, ''

    dfaDif = dfaMAT & (~dfaLearner)

    if dfaDif.countTransitions() == 0:
        # dfaMAT - подавтомат dfaLearner
        difDfa = dfa2 & (~dfa1)
        return False, generateRandomWord(difDfa)

    return False, generateRandomWord(dfaDif)