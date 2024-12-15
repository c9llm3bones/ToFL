from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from DFAFromTable import makeDfaFromTableFado  
from equivalent import *
from generateLexemDFA import generateLexems
from makeGrammatic import generateGrammar
import uvicorn

app = FastAPI()

lexemObjects = generateLexems()
grammar = generateGrammar(lexemObjects)

programDFA = grammar['pattern']

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
