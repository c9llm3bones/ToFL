from FAdo.fa import *
import random
from time import time

def members(dfa, word):
    sigma = set(word)
    if not sigma.issubset(dfa.Sigma):
        return False
    return dfa.evalWordP(word)

def generateRandomWord(dfa, max_length=150, max_attempts=1000000):
    print("Generating word via random walks...")
    start = time()
    for attempt in range(max_attempts):
        current_state = dfa.Initial
        word = ''
        steps = 0
        while steps < max_length:
            steps += 1
            transitions = dfa.delta[current_state]
            if not transitions:
                break  
            symbol = random.choice(list(transitions.keys()))
            current_state = transitions[symbol]
            word += symbol
            if current_state in dfa.Final:
                #print(f"Generated word: {word} for {attempt+1} attempts and {time() - start} sec")
                return word
     
    print("Failed to generate a word via random walks.")
    return ''



def checkEquivalenceDFA(dfaMAT, dfaLearner):
    alphabet = set(dfaMAT.Sigma).union(set(dfaLearner.Sigma))
    dfaMAT.Sigma = alphabet
    dfaLearner.Sigma = alphabet
    
    if dfaMAT == dfaLearner:
def generateRandomWord(dfa):
    ln = random.randint(3, 50)
    words = dfa.enumDFA(idx)
    idx = random.randint(0, len(words))
    return words[idx]

def checkEquivalence(dfaMAT, dfaLearner):
    if dfaMAT == dfaLearner:
        return True, ''

    
    dfaMATComplete = dfaMAT.complete()
    dfaLearnerComplete = dfaLearner.complete()
    
    dfaDif = dfaMATComplete & (~dfaLearnerComplete)

    #dfaMAT.display()
    #dfaLearner.display()
    #dfaDif.display()
    if dfaDif.countTransitions() == 0:
        # dfaMAT - подавтомат dfaLearner
        difDfa = dfaLearnerComplete & (~dfaMATComplete)
    dfaDif = dfaMAT & (~dfaLearner)

    if dfaDif.countTransitions() == 0:
        # dfaMAT - подавтомат dfaLearner
        difDfa = dfa2 & (~dfa1)
        return False, generateRandomWord(difDfa)

    return False, generateRandomWord(dfaDif)
