from FAdo.fa import *
from FAdo.reex import *
from FAdo.conversions import *

def makeDfaFromTableFado(prefixes, suffixes, table):
    def getTableString(prefix):
        return ''.join([table.get((prefix, suffix), '0') for suffix in suffixes])
    
    prefixToRowStr = {prefix: getTableString(prefix) for prefix in prefixes}
    uniqueRows = set(prefixToRowStr.values())
    tableStringToState = {rowStr: idx for idx, rowStr in enumerate(uniqueRows)}
    prefixToState = {prefix: tableStringToState[rowStr] for prefix, rowStr in prefixToRowStr.items()}
    alph = ['a', 'b', 'c', '0', '1', '2']
    transitions = {}
    
    for prefix in prefixes:
        currentState = prefixToState[prefix]
        transitions.setdefault(currentState, {})
        for symbol in alph:
            newPrefix = ('' if prefix == '@epsilon' else prefix) + symbol
            if newPrefix in prefixToState:
                nextState = prefixToState[newPrefix]
                transitions[currentState][symbol] = nextState
    
    initialState = prefixToState.get('@epsilon')
    if initialState is None:
        raise ValueError("Initial state '@epsilon' not found.")
    
    finalStates = {prefixToState[prefix] for prefix in prefixes if table.get((prefix, '@epsilon'), '0') == '1'}
    dfa = DFA()
    dfa.setSigma(set(alph))
    for state in range(len(uniqueRows)):
        dfa.addState(state)
    dfa.setInitial(initialState)
    for state in finalStates:
        dfa.addFinal(state)
    for state, transDict in transitions.items():
        for symbol, nextState in transDict.items():
            dfa.addTransition(state, symbol, nextState)
    

    print("Переходы:", transitions)
    print("Конечные состояния:", finalStates)
    print("Начальное состояние:", initialState)
    #dfa.display()
    return dfa.minimal()


#prefixes = ['@epsilon', '0', '1', '00', '01', '10', '11']
#suffixes = ['@epsilon']
"""
table = {
    ('@epsilon', '@epsilon'): '0',
    ('0', '@epsilon'): '0',
    ('1', '@epsilon'): '1',
    ('00', '@epsilon'): '0',
    ('01', '@epsilon'): '1',
    ('10', '@epsilon'): '1',    
    ('11', '@epsilon'): '1'
}
"""
#prefixes = ['1c', '11', '@epsilon']
#suffixes = ['1', 'c', '1c', '@epsilon', '11']
"""
table = {
    ('11', '1'): '0',
    ('11', '@epsilon'): '1',
    ('11', '11'): '0',
    ('11', '1c'): '0',
    ('11', 'c'): '0',
    ('1c', '1'): '0',
    ('1c', '@epsilon'): '1',
    ('1c', '11'): '0',
    ('1c', '1c'): '0',
    ('1c', 'c'): '0',
    ('@epsilon', '@epsilon'): '1'
}
"""
#dfa = makeDfaFromTableFado(prefixes, suffixes, table)


"""
table = {}
tableValues = tableData.split()
index = 0
for prefix in mainPrefixes + nonMainPrefixes:
    for suffix in suffixes:
        table[(prefix, suffix)] = tableValues[index]
        index += 1
"""
