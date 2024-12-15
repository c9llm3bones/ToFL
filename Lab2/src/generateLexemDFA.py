import random
from FAdo.fa import *
from FAdo.reex import *
from time import time

countGens, countChecks = 0, 0

alphabetBF = {'a', 'b', 'c', '0', '1', '2'}

alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '|', '(', ')'}

class Lexema:
    def __init__(self, name):
        self.name = name
        self.sigma = set()
        self.dfa = None
        self.sigmaLen = 0

def checkIntersection(dfa1, dfa2):
    intersection_dfa = dfa1 & dfa2
    return intersection_dfa.Final

def setAlphabetsLen(lexemObjects):
  hasTwo = False
  i = 0
  while (not hasTwo) and i < 4:
    curLen = random.randint(1, 2)
    if curLen == 2:
      hasTwo = True
    lexemObjects[i].sigmaLen = curLen
    i += 1
  
  if not hasTwo:
    lexemObjects[random.randint(0, 3)].sigmaLen = 2
    
  for j in range(i, len(lexemObjects)):
    lexemObjects[j].sigmaLen = 1
    
def generate_random_automaton(alphabet, min_states=3, max_states=10):
    num_states = random.randint(min_states, max_states)
    
    nfa = NFA()
    for sym in alphabet:
        nfa.setSigma(nfa.Sigma | {sym})
    
    for s in range(num_states):
        nfa.addState(s)
    
    initial_state = random.randint(0, num_states-1)
    nfa.setInitial({initial_state})
    
    num_final_states = random.randint(1, num_states)  
    final_states = random.sample(range(num_states), num_final_states)
    for fs in final_states:
        nfa.addFinal(fs)
    
    for state in range(num_states):
        for sym in alphabet:
            transitions_count = random.randint(0, 2)  
            for _ in range(transitions_count):
                target_state = random.randint(0, num_states - 1)
                nfa.addTransition(state, sym, target_state)
    
    return nfa


def generate_finite_automaton(alphabet, min_states=3, max_states=10):
    
    num_states = random.randint(min_states, max_states)
    nfa = NFA()
    
    for sym in alphabet:
        nfa.setSigma(nfa.Sigma | {sym})
    
    for s in range(num_states):
        nfa.addState(s)
    
    initial_state = 0
    nfa.setInitial({initial_state})
    
    num_final_states = random.randint(1, min(num_states, 3)) 
    final_states = random.sample(range(1, num_states), num_final_states)
    for fs in final_states:
        nfa.addFinal(fs)
    
    for state in range(num_states - 1):
        for sym in alphabet:
            transitions_count = random.randint(0, 2)
            for _ in range(transitions_count):
                target_state_candidates = [x for x in range(state+1, num_states)]
                if target_state_candidates:
                    target_state = random.choice(target_state_candidates)
                    nfa.addTransition(state, sym, target_state)
    
    return nfa


def generate_infinite_automaton(alphabet, min_states=3, max_states=10):
    num_states = random.randint(min_states, max_states)
    nfa = NFA()
    for sym in alphabet:
        nfa.setSigma(nfa.Sigma | {sym})
    
    for s in range(num_states):
        nfa.addState(s)
    
    initial_state = 0
    nfa.setInitial({initial_state})
    
    num_final_states = random.randint(1, min(num_states, 3))
    final_states = random.sample(range(num_states), num_final_states)
    for fs in final_states:
        nfa.addFinal(fs)
    
    for state in range(num_states):
        for sym in alphabet:
            transitions_count = random.randint(0, 2)
            for _ in range(transitions_count):
                target_state = random.randint(0, num_states - 1)
                nfa.addTransition(state, sym, target_state)
    
    if final_states:
        cycle_state = final_states[0]
        sym = random.choice(list(alphabet))
        nfa.addTransition(cycle_state, sym, cycle_state)
    else:
        sym = random.choice(list(alphabet))
        nfa.addTransition(initial_state, sym, initial_state)
    
    return nfa

def generateSigma(ln, alphabet):
    return list(random.sample(list(alphabet), k=ln))
    if len(alphabet) == 0 or num_states < 2:
        raise ValueError("")

    automaton = DFA()
    automaton.setSigma(set(alphabet))

    states = [automaton.addState() for _ in range(num_states)]
    automaton.setInitial(states[0])

    for i in range(num_states - 1):
        symbol = random.choice(alphabet)
        automaton.addTransition(states[i], symbol, states[i + 1])

    automaton.addFinal(states[-1])

    if is_cyclic:
        symbol = random.choice(alphabet)
        automaton.addTransition(states[-1], symbol, states[0])

    automaton.minimal()
    return automaton

def generate_lexeme_automaton_with_dfs(alphabet, num_states, is_finite=True):
    if len(alphabet) == 0 or num_states < 2:
        raise ValueError("")

    nfa = NFA()
    nfa.setSigma(set(alphabet))

    states = [nfa.addState() for _ in range(num_states)]
    nfa.setInitial({states[0]})

    visited = set()
    stack = [states[0]]
    visited.add(states[0])

    def generate_transitions(current_state):
        transitions_count = random.randint(1, num_states - 1)

        possible_targets = list(set(states) - {current_state})
        if is_finite:
            possible_targets = [st for st in possible_targets if st not in visited]

        if not possible_targets and is_finite:
            return

        for _ in range(transitions_count):
            if not possible_targets and not is_finite:
                target = random.choice(states)
            elif not possible_targets:
                break
            else:
                target = random.choice(possible_targets)
                possible_targets.remove(target)

            symbol = random.choice(alphabet)
            nfa.addTransition(current_state, symbol, target)
            if target not in visited:
                visited.add(target)
                stack.append(target)

    while stack:
        current = stack.pop()
        generate_transitions(current)

    if len(visited ) < 2:
        return generate_lexeme_automaton_with_dfs(alphabet, num_states, is_finite)
    final_states = random.sample(list(visited)[1:], random.randint(1, min(len(visited)-1, 3)))
    for fs in final_states:
        nfa.addFinal(fs)

    nfa.minimal()
    return nfa


def add_double_symbol_cycle(dfa, state, symbol):
    
    extra = dfa.addState()
    dfa.addTransition(state, symbol, extra)
    dfa.addTransition(extra, symbol, state)
    return dfa

def generate_var_dfa(symbol='a', start_length=50):
    if start_length % 2 != 0:
        raise ValueError("start_length для var должен быть чётным")

    dfa = DFA()
    dfa.setSigma({symbol})

    states = [dfa.addState() for _ in range(start_length+1)]
    dfa.setInitial(states[0])

    for i in range(start_length):
        dfa.addTransition(states[i], symbol, states[i+1])

    dfa.addFinal(states[start_length])

    dfa = add_double_symbol_cycle(dfa, states[start_length], symbol)

    return dfa

def generate_const_dfa(symbol='a', start_length=51):
    if start_length % 2 == 0:
        raise ValueError("start_length для const должен быть нечётным")

    dfa = DFA()
    dfa.setSigma({symbol})

    states = [dfa.addState() for _ in range(start_length+1)]
    dfa.setInitial(states[0])

    for i in range(start_length):
        dfa.addTransition(states[i], symbol, states[i+1])

    dfa.addFinal(states[start_length])
    dfa = add_double_symbol_cycle(dfa, states[start_length], symbol)

    return dfa

from FAdo.fa import DFA

def generate_single_string_dfa(symbol, length):
    dfa = DFA()
    dfa.setSigma({symbol})
    states = [dfa.addState() for _ in range(length + 1)]
    dfa.setInitial(states[0])
    for i in range(length):
        dfa.addTransition(states[i], symbol, states[i+1])
    dfa.addFinal(states[-1])
    return dfa

def generate_brackets_automata(symbol):
    brackets = {
        '(': 3,
        ')': 5,
        '{': 7,
        '}': 9,
        '[': 11,
        ']': 13
    }
    automata = {}
    for br, length in brackets.items():
        automata[br] = generate_single_string_dfa(symbol, length)
    return automata


def generateAutomatas(lexemObjects, alphabetBF):
    global countGens 
    countGens+=1
    for lexem in lexemObjects:
        if not alphabetBF:
            return False, lexemObjects
        minStates = 5
        maxStates = 10
        
        if lexem.name in ('eol', 'blank'):
            lexem.sigma = generateSigma(lexem.sigmaLen, alphabetBF)
            lexem.dfa = generate_lexeme_automaton_with_dfs(lexem.sigma, random.randint(minStates, maxStates), True)
            alphabetBF = alphabetBF - set(lexem.sigma)
        elif lexem.name in ('sep', 'equal'):
            lexem.sigma = generateSigma(lexem.sigmaLen, alphabetBF)
            lexem.dfa = generate_lexeme_automaton_with_dfs(lexem.sigma, random.randint(minStates, maxStates), True)
            alphabetBF = alphabetBF - set(lexem.sigma)
        elif lexem.name in ('const'):
            lexem.sigma = generateSigma(lexem.sigmaLen, alphabetBF)
            lexem.dfa = generate_const_dfa(list(lexem.sigma)[0])
        elif lexem.name in ('var'):
            lexem.sigma = generateSigma(lexem.sigmaLen, alphabetBF)
            lexem.dfa = generate_var_dfa(list(lexem.sigma)[0])
            
        elif lexem.name in ('lbr-1'):
            bracket_automata = generate_brackets_automata(list(lexemObjects[5].sigma)[0])
            i = 6
            for br in bracket_automata.values():
                lexemObjects[i].dfa = br
                i+=1
        else:
            continue
    return lexemObjects
def generateLexems():
    global alphabetBF, alphabetRegex
    lexemObjects = [
        Lexema('eol'),
        Lexema('blank'),
        Lexema('equal'),
        Lexema('sep'),
        Lexema('const'),
        Lexema('var'),
        Lexema('lbr-1'),
        Lexema('lbr-2'),
        Lexema('lbr-3'),
        Lexema('rbr-1'),
        Lexema('rbr-2'),
        Lexema('rbr-3')
    ]
    
    start = time()
    print("Starting...\n")
    print('Generating random lexems...\n')
    setAlphabetsLen(lexemObjects)
    
    #for lexem in lexemObjects:
      #  print(lexem.name, ' ', lexem.sigmaLen)
        
    return generateAutomatas(lexemObjects, alphabetBF)
    


    