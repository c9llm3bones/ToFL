from lexer import *
from parser import *
from semantic import *
from grammatic import *
from ast_ import *

def process_regex(regex):
    regex = regex.replace(" ", "")
    print(f"Regex: {regex}")

    checker = SemanticChecker()
    try:
        ast = parse_regex(regex)
        checker.check(ast)

        capturing_map = {}
        for i, grpnode in enumerate(checker.capturing_groups, start=1):
            capturing_map[grpnode] = i

        builder = GrammarBuilder(capturing_map)
        rules = builder.build_grammar(ast)
        return rules
    except ValueError as e:
        print('error: ', e)
        return []
    except SemanticError as e:
        print('semantic error: ', e)
        return []

if __name__ == "__main__":
    """examples = [
        "a",
        "(ab)*",      
        "(?:ab)*|c",   
        "(?=xyz)",     
        "(?[3])",     
        "ab|c",        
        "(((xyz)))",   
        "(a| (bb)) (a | (?1))",
        "(a(bb))(a(?2))",
        "(a(a|b)*)a(?1)b(?1)",            
        "(?=a)",       
        "(?:ab)(xy)",
        "((ab))",      
        "((ab))(?2)", 
        "(a (?1))",
        "(a(?1)b|c)",
    ]
    """

    examples = [
        "(a|(?2)b)(a(?1))",
        "(a|(?2))(a|(bb(?1)))(a)",
        "(a|(?2))(a|(bb(?4)))(a)",
        "(a)*((?1))*",
        "(a(?2)b|c)((?1)((?1)))",
        "((a(?1)b|c)|(a|b))((?3)(?2))",
        "(?1)(a|b)",
        "(?1)(a|b)",
        "(a(?1)a|b)",
        "((?1)a|b)",
        "(a|b)*(?1)",
        "(?1)(a|b)*(?1)",
        "(aa|bb)(?1)",
        "(aa|bb)(?1)",
        "(a|(bb))(a|(?2))",
        "(a|(bb))(a|(?3))",
        "(a|(?2))(a|(bb(?1)))",
        "(a(?1)b|c)",
        "(?3)(aa)(bb)",
        "(?2)(aa)(bb)",
        "sad(",
        "(?1)",
        "3",
        "(a(?1)a|b)",
        "(?2)(a)(?:aaa)(?:bbb)"
    ]
    output_file = "cfg_grammars.txt"

    with open(output_file, "w") as file:
        for ex in examples:
            try:                
                rules = process_regex(ex)

                file.write(f"Regex: {ex}\n")
                for r in rules:
                    formatted_rule = r.replace("'", "")  
                    print(formatted_rule)
                    file.write(f"{formatted_rule}\n")
                print()
                file.write("------------------------\n")  

            except ValueError as e:
                print('error: ', e)
            except SemanticError as e:
                print('semantic error: ', e)
            print()

    while (True):
        regex = input("Enter regex: ")
        rules = process_regex(regex)
        print("CFG Rules:")
        if rules:
            for rule in rules:
                print(rule)