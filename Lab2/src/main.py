from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from DFAFromTable import makeDfaFromTableFado  
from equivalent import *
from generateLexem import generateLexems
from makeGrammatic import generateGrammar
import uvicorn

app = FastAPI()

lexemObjects = generateLexems()
grammar = generateGrammar(lexemObjects)


programDFA = grammar['program']

class MembershipRequest(BaseModel):
    inputString: str

class EquivalenceRequest(BaseModel):
    equivalenceTable: dict

@app.post("/checkMembership/")
async def checkMembership(request: MembershipRequest):
    result = members(programDFA, request.inputString)
    return {"result": int(result)}

@app.post("/checkEquivalence/")
async def checkEquivalence(request: EquivalenceRequest):
    # Извлекаем таблицу эквивалентности
    epsilonVal = request.equivalenceTable.get("epsilon", 0)
    classes = {k: v for k, v in request.equivalenceTable.items() if k != "epsilon"}
    mainPrefixes = [key for key in classes.keys()]
    extendedPrefixes = mainPrefixes.copy()  # Пример копирования для extend (уточните по необходимости)
    suffixes = list(classes.values())

    
    learnerDFA = makeDfaFromTableFado(mainPrefixes, extendedPrefixes, suffixes, request.equivalenceTable)
    # Проверка эквивалентности
    areEquivalent, counterexample = checkEquivalence(programDFA, learnerDFA)
    
    if areEquivalent:
        return {"result": "TRUE"}
    else:
        return {"result": counterexample}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
