from DFAFromTable import makeDfaFromTableFado  
from equivalent import *
import generateLexemDFA
import generateLexemRegexpr
import test
from makeGrammatic import generateGrammar
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from DFAFromTable import makeDfaFromTableFado  
from equivalent import *
from generateLexemDFA import generateLexems
from test import generateRandomRegex
from makeGrammatic import generateGrammar
import uvicorn


print("Choose generation method:")
print("1. DFA-based generation")
print("2. Regular expression-based generation")

choice = input("Enter your choice (1 or 2): ") 

if choice == "1":
    lexemObjects = generateLexemDFA.generateLexems()
elif choice == "2":
    lexemObjects = test.generateLexems()
else:
    print("Invalid choice. Using DFA-based generation by default.")
    lexemObjects = generateLexemDFA.generateLexems()

grammar = generateGrammar(lexemObjects, choice)
programDFA = grammar['program']

#programDFA.display()
#generateRandomWord(programDFA)

app = FastAPI()

class MembershipRequest(BaseModel):
    inputString: str

class EquivalenceRequest(BaseModel):
    equivalenceTable: dict

@app.post("/checkMembership/")
async def checkMembership(request: MembershipRequest):
    print(f"Проверка членства для строки: {request.inputString}")
    result = members(programDFA, request.inputString)
    print(f"Результат: {'да' if result else 'нет'}")
    return {"result": int(result)}

@app.post("/checkEquivalence/")
async def checkEquivalence(request: EquivalenceRequest):
    print(f"Получена таблица эквивалентности: {request.equivalenceTable}")
    table = request.equivalenceTable

    reconstructed_table = {}
    for key, value in table.items():
        prefix, _, suffix = key.partition('_')
        if not prefix:  
            prefix = '@epsilon'
        if not suffix:  
            suffix = '@epsilon'
        reconstructed_table[(prefix, suffix)] = value

    print(f"Реконструированная таблица эквивалентности: {reconstructed_table}")

    prefixes = set(prefix for prefix, _ in reconstructed_table.keys())
    suffixes = set(suffix for _, suffix in reconstructed_table.keys())
    mainPrefixes = list(prefixes)

    print(f"Префиксы: {mainPrefixes}")
    print(f"Суффиксы: {suffixes}")

    learnerDFA = makeDfaFromTableFado(mainPrefixes, list(suffixes), reconstructed_table)
    print("Построен DFA для лернера.")

    areEquivalent, counterexample = checkEquivalenceDFA(programDFA, learnerDFA)
    if areEquivalent:
        print("Автоматы эквивалентны.")
        return {"result": "TRUE"}
    else:
        print(f"Автоматы не эквивалентны. Контрпример: {counterexample}")
        return {"result": counterexample}


if __name__ == "__main__":
    #programDFA.display()
    #generateRandomWord(programDFA)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
