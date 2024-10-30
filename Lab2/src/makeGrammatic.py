from FAdo.fa import *
from FAdo.reex import *
import generateLexem.py



def create_grammar_automaton(lexemObjects):
    # Автомат для [eol]*([definition][eol]+)+
    program_nfa = NFA()
    eol_dfa = lexemObjects[0].dfa  # DFA для [eol]
    definition_dfa = create_definition_automaton(lexemObjects)  # Автомат для [definition]
    
    program_nfa = eol_dfa.star()  # [eol]*
    program_nfa.concat(definition_dfa.concat(eol_dfa.plus()).plus())  # ([definition][eol]+)+
    
    return program_nfa.toDFA()

def create_definition_automaton(lexemObjects):
    definition_nfa = NFA()
    const_dfa = lexemObjects[4].dfa  # DFA для [const]
    lbr1_dfa = lexemObjects[6].dfa   # DFA для [lbr-1]
    rbr1_dfa = lexemObjects[9].dfa   # DFA для [rbr-1]
    
    sentence_dfa = create_sentence_automaton(lexemObjects)  # Автомат для [sentence]
    eol_dfa = lexemObjects[0].dfa  # DFA для [eol]
    
    definition_nfa.concat(const_dfa)  # [const]
    definition_nfa.concat(lbr1_dfa)   # [lbr-1]
    definition_nfa.concat(eol_dfa.star().concat(sentence_dfa).star())  # ([eol]*[sentence])*
    definition_nfa.concat(eol_dfa.star())  # [eol]*
    definition_nfa.concat(rbr1_dfa)   # [rbr-1]
    
    return definition_nfa.toDFA()

def create_sentence_automaton(lexemObjects):
    sentence_nfa = NFA()
    pattern_dfa = create_pattern_automaton(lexemObjects)  # Автомат для [pattern]
    equal_dfa = lexemObjects[2].dfa   # DFA для [equal]
    expression_dfa = create_expression_automaton(lexemObjects)  # Автомат для [expression]
    sep_dfa = lexemObjects[3].dfa     # DFA для [sep]
    
    sentence_nfa.concat(pattern_dfa)  # [pattern]
    sentence_nfa.concat(equal_dfa)    # [equal]
    sentence_nfa.concat(expression_dfa)  # [expression]
    sentence_nfa.concat(sep_dfa)      # [sep]
    
    return sentence_nfa.toDFA()

def create_pattern_automaton(lexemObjects):
    pattern_nfa = NFA()
    lbr3_dfa = lexemObjects[8].dfa   # DFA для [lbr-3]
    rbr3_dfa = lexemObjects[11].dfa  # DFA для [rbr-3]
    blank_dfa = lexemObjects[1].dfa  # DFA для [blank]
    var_dfa = lexemObjects[5].dfa    # DFA для [var]
    const_dfa = lexemObjects[4].dfa  # DFA для [const]
    
    # [lbr-3][pattern][rbr-3]
    pattern_nfa.union(lbr3_dfa.concat(create_pattern_automaton(lexemObjects)).concat(rbr3_dfa))
    # [pattern][blank][pattern]
    pattern_nfa.union(create_pattern_automaton(lexemObjects).concat(blank_dfa).concat(create_pattern_automaton(lexemObjects)))
    # [var] | [const]
    pattern_nfa.union(var_dfa).union(const_dfa)
    
    return pattern_nfa.toDFA()

def create_expression_automaton(lexemObjects):
    expression_nfa = NFA()
    var_dfa = lexemObjects[5].dfa    # DFA для [var]
    const_dfa = lexemObjects[4].dfa  # DFA для [const]
    blank_dfa = lexemObjects[1].dfa  # DFA для [blank]
    lbr2_dfa = lexemObjects[7].dfa   # DFA для [lbr-2]
    rbr2_dfa = lexemObjects[10].dfa  # DFA для [rbr-2]
    lbr3_dfa = lexemObjects[8].dfa   # DFA для [lbr-3]
    rbr3_dfa = lexemObjects[11].dfa  # DFA для [rbr-3]

    # [var] | [const]
    expression_nfa.union(var_dfa).union(const_dfa)
    # [expression][blank][expression]
    expression_nfa.union(create_expression_automaton(lexemObjects).concat(blank_dfa).concat(create_expression_automaton(lexemObjects)))
    # [lbr-3][expression][rbr-3]
    expression_nfa.union(lbr3_dfa.concat(create_expression_automaton(lexemObjects)).concat(rbr3_dfa))
    # [lbr-2][const][blank][expression][rbr-2]
    expression_nfa.union(lbr2_dfa.concat(const_dfa).concat(blank_dfa).concat(create_expression_automaton(lexemObjects)).concat(rbr2_dfa))
    
    return expression_nfa.toDFA()



# Пример использования:
program_dfa = create_grammar_automaton(lexemObjects)

