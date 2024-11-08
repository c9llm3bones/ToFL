from FAdo.fa import *
from FAdo.reex import *
from FAdo.conversions import *

def makeDfaFromTableFado(mainPrefixes, extendedPrefixes, suffixes, table):
    prefixes = mainPrefixes + extendedPrefixes

    def getTableString(prefix):
        return ''.join([table.get((prefix, suffix), '0') for suffix in suffixes])

    allStrings = {}
    for prefix in prefixes:
        tableString = getTableString(prefix)
        allStrings[prefix] = tableString

    tableStringToState = {}
    stateCounter = 0
    for tableString in set(allStrings.values()):
        stateName = stateCounter
        tableStringToState[tableString] = stateName
        stateCounter += 1

    prefixToState = {}
    for prefix in prefixes:
        tableString = allStrings[prefix]
        state = tableStringToState[tableString]
        prefixToState[prefix] = state
        if prefix == 'ε':  # Здесь заменяем 'ε' на '@epsilon' для согласованности
            prefixToState[prefix] = '@epsilon'

    nfa = NFA()
    
    states = set(prefixToState.values())
    for state in states:
        nfa.addState(state)
    
    # Используем '@epsilon' в качестве начального состояния
    initialState = prefixToState.get('@epsilon')
    if initialState is None:
        raise ValueError("Initial state '@epsilon' not found in prefixToState")

    nfa.setInitial({initialState})

    finalStates = set()
    for prefix in prefixes:
        if table.get((prefix, '@epsilon'), '0') == '1':
            finalState = prefixToState[prefix]
            finalStates.add(finalState)
    for finalState in finalStates:
        nfa.addFinal(finalState)
    
    alphabet = {'0', '1', '2', 'a', 'b', 'c'}
    for prefix in prefixes:
        currentState = prefixToState[prefix]
        for symbol in alphabet:
            newPrefix = ('' if prefix == '@epsilon' else prefix) + symbol
            if newPrefix in prefixes:
                nextState = prefixToState[newPrefix]
                nfa.addTransition(currentState, symbol, nextState)

    return nfa.toDFA().minimal()

mainPrefixes = ["@epsilon", "0", "1", "01", "02"]
nonMainPrefixes = ["00", "11", "012", "021", "102", "202"]
suffixes = ["@epsilon", "120", "01", "0"]
tableData = "1 0 0 0 0 0 1 0 1 0 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"

table = {}
tableValues = tableData.split()
index = 0
for prefix in mainPrefixes + nonMainPrefixes:
    for suffix in suffixes:
        table[(prefix, suffix)] = tableValues[index]
        index += 1

dfa = makeDfaFromTableFado(mainPrefixes, nonMainPrefixes, suffixes, table)

#dfa.display()

reg = FA2regexpCG(dfa)
#print(reg.toNFA().toDFA() == dfa)
#reg.toNFA().toDFA().display()
