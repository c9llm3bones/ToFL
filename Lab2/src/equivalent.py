from FAdo.fa import *
import random
from time import time
from FAdo.reex import *

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
        return False, generateRandomWord(difDfa)

    return False, generateRandomWord(dfaDif)


r1 = str2regexp("a(aa)*")  
r2 = str2regexp("a(aa)*")  
intersection = r1.toDFA().minimal() & (r2.toDFA().minimal())
print(intersection.Final)
#intersection.display()
#r1.toDFA().minimal().display()
#r2.toDFA().minimal().display()
