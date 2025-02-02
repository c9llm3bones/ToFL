import random
from FAdo.fa import *
from FAdo.reex import *
from time import time
import generateLexemRegexpr
from equivalent import checkEquivalenceDFA, generateRandomWord, members


def generateGrammar(lexemObjects, option):
    
    lexem_dict = {lex.name: lex for lex in lexemObjects}
    grammar_automata = {}

    print('Minimalizing grammar...')

    def createRuleAutomataDFA(lexem_dict):
        # pattern
        pattern_dfa = lexem_dict["var"].dfa.union(
            lexem_dict["const"].dfa).toDFA().minimal()

        grammar_automata["pattern"] = pattern_dfa.union(
            lexem_dict["lbr-3"].dfa.concat(pattern_dfa).concat(lexem_dict["rbr-3"].dfa).union(
                pattern_dfa.concat(lexem_dict["blank"].dfa).concat(pattern_dfa)
            ).toDFA()
        ).toDFA().minimal()

        # expression
        expression_dfa = lexem_dict["var"].dfa.union(
            lexem_dict["const"].dfa).toDFA().minimal()

        grammar_automata["expression"] = expression_dfa.union(
            expression_dfa.concat(lexem_dict["blank"].dfa).concat(expression_dfa)).union(
                lexem_dict["lbr-3"].dfa.concat(expression_dfa).concat(lexem_dict["rbr-3"].dfa)).union(
                    lexem_dict["lbr-2"].dfa.concat(lexem_dict["const"].dfa).concat(lexem_dict["blank"].dfa).concat(
                        expression_dfa).concat(lexem_dict["rbr-2"].dfa)
        ).toDFA().minimal()

        # sentence
        grammar_automata["sentence"] = grammar_automata["pattern"].concat(
            lexem_dict["equal"].dfa).concat(grammar_automata["expression"]).concat(
                lexem_dict["sep"].dfa).toDFA().minimal()

        # definition
        grammar_automata["definition"] = lexem_dict["const"].dfa.concat(
            lexem_dict["lbr-1"].dfa).concat(
                lexem_dict["eol"].dfa.star().concat(grammar_automata["sentence"]).star()).concat(
                    lexem_dict["eol"].dfa.star()).concat(lexem_dict["rbr-1"].dfa).toDFA().minimal()
        
        # program
        grammar_automata["program"] = lexem_dict["eol"].dfa.star().concat(
            grammar_automata["definition"].concat(lexem_dict["eol"].dfa.plus()).plus()
        ).toDFA().minimal()

        return grammar_automata

    def createRuleAutomataReg(lexem_dict):
        grammar_automata = {}

        # pattern
        pattern_re_str = f"({lexem_dict['var'].regStr}|{lexem_dict['const'].regStr})"
        grammar_automata["pattern"] = f"{pattern_re_str}|{lexem_dict['lbr-3'].regStr}{pattern_re_str}{lexem_dict['rbr-3'].regStr}|{pattern_re_str}{lexem_dict['blank'].regStr}{pattern_re_str}"
        grammar_automata["pattern"] = str2regexp(grammar_automata["pattern"]).reduced()
        
        # expression
        expression_re_str = f"({lexem_dict['var'].regStr}|{lexem_dict['const'].regStr})"
        grammar_automata["expression"] = f"{expression_re_str}|{expression_re_str}{lexem_dict['blank'].regStr}{expression_re_str}|{lexem_dict['lbr-3'].regStr}{expression_re_str}{lexem_dict['rbr-3'].regStr}|{lexem_dict['lbr-2'].regStr}{lexem_dict['const'].regStr}{lexem_dict['blank'].regStr}{expression_re_str}{lexem_dict['rbr-2'].regStr}"
        grammar_automata["expression"] = str2regexp(grammar_automata["expression"]).reduced()
        
        # sentence
        grammar_automata["sentence"] = f"{grammar_automata['pattern']}{lexem_dict['equal'].regStr}{grammar_automata['expression']}{lexem_dict['sep'].regStr}"
        grammar_automata["sentence"] = str2regexp(grammar_automata["sentence"])

        # definition
        grammar_automata["definition"] = f"{lexem_dict['const'].regStr}{lexem_dict['lbr-1'].regStr}({lexem_dict['eol'].regStr}*{grammar_automata['sentence']})*{lexem_dict['eol'].regStr}*{lexem_dict['rbr-1'].regStr}"
        grammar_automata["definition"] = str2regexp(grammar_automata["definition"]).reduced()
        
        # program
        grammar_automata["program"] = f"{lexem_dict['eol'].regStr}*({grammar_automata['definition']}{lexem_dict['eol'].regStr}*)*"
        grammar_automata["program"] = str2regexp(grammar_automata["program"]).reduced()

        return grammar_automata

    start = time()
    print(option)
    if int(option) == 2 or int(option) == 3:
        print("Using Regular Expression based generation...")
        for lexem in lexemObjects:
            lexem.setRegex(lexem.regStr, lexem.sigma)
            lexem.regExpr.reduced()
            lexem.dfa = lexem.dfa.toDFA().minimal()
            #lexem.dfa.display()
        grammar_automata = createRuleAutomataReg(lexem_dict)
        print("RegExp generation time:", time() - start)
        # Convert regex to DFA for consistency
        grammar_automata['program'] = grammar_automata['program'].nfaPD().toDFA().minimal()
        #for automaton in grammar_automata:
        #    grammar_automata[automaton] = grammar_automata[automaton].nfaPD().toDFA().minimal()
    else:
        print("Using DFA based generation...")
        for lexem in lexemObjects:
            lexem.dfa = lexem.dfa.toDFA().minimal()
            #lexem.dfa.display()
        grammar_automata = createRuleAutomataDFA(lexem_dict)
        print("DFA generation time:", time() - start)

    start = time()
    #grammarAutomataReg = createRuleAutomataReg(lexem_dict)
    #print(grammarAutomataReg['program'])
    #print("RegExp generation time:", time() - start)
    #grammarAutomataDFANoMin = createRuleAutomataNoMin(lexem_dict)
    
    #for automaton in grammarAutomataReg:
     #   grammarAutomataReg[automaton] = grammarAutomataReg[automaton].nfaPD().toDFA().minimal()
    
    #print(checkEquivalenceDFA(grammarAutomataDFA, grammarAutomataDFANoMin))
    
    print('\n')
    """
    for automaton in grammar_automata:
        print(automaton, len(grammar_automata[automaton].States))

    for automaton in grammar_automata:
        print(grammar_automata[automaton] == grammar_automata[automaton])
    """
    print("Automaton is ready!\nWaiting for requests...")
    return grammar_automata
