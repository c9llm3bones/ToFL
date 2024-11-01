for lexem in lexemObjects:
  lexem.setRegex(lexem.regStr, lexem.sigma)
  lexem.regExpr.reduced()
  lexem.dfa.minimal()
  
lexem_dict = {lex.name: lex for lex in lexemObjects}

grammar_automata = {}

"""[program] ::= [eol]*([definition][eol]+)+

[definition] ::= [const] [lbr-1] ([eol]*[sentence])* [eol]*[rbr-1]

[sentence] ::= [pattern][equal][expression][sep]

[pattern] ::= [lbr-3][pattern][rbr-3]|[pattern][blank][pattern]
| [var] | [const] |

[expression] ::= [var] | [const] | [expression][blank][expression]
[lbr-3] [expression] [rbr-3] |
[lbr-2] [const] [blank] [expression] [rbr-2]"""

def create_rule_automata_dfa(lexem_dict):
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
    # programm
    grammar_automata["program"] = lexem_dict["eol"].dfa.star().concat(
        grammar_automata["definition"].concat(lexem_dict["eol"].dfa.plus()).plus()
    ).toDFA().minimal()

    return grammar_automata



def create_rule_automata_reg(lexem_dict):
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
grammar_automata_dfa = create_rule_automata_dfa(lexem_dict)
print(time() - start)

start = time()
grammar_automata_reg = create_rule_automata_reg(lexem_dict)
print(time() - start)


"""
for automaton in grammar_automata_reg:
    print(automaton, grammar_automata_reg[automaton])
"""
start = time()

for automaton in grammar_automata_reg:
    grammar_automata_reg[automaton] = grammar_automata_reg[automaton].nfaPD().toDFA().minimal()
print(time() - start)

for automaton in grammar_automata_reg:
    print(automaton, len(grammar_automata_reg[automaton].States))

for automaton in grammar_automata_dfa:
    print(automaton, len(grammar_automata_dfa[automaton].States))
     
for automaton in grammar_automata_reg:
    print(grammar_automata_dfa[automaton] == grammar_automata_reg[automaton])
