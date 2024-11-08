import random
from FAdo.fa import *
from FAdo.reex import *
from time import time

countGens, countChecks = 0, 0

class Lexema:
    def __init__(self, name):
        self.name = name
        self.sigma = set()
        self.regStr = ''
        self.regExpr = None
        self.dfa = None

    def setRegex(self, regStr, sigma):
        self.regStr = regStr
        self.sigma = sigma
        self.regExpr = str2regexp(regStr)
        self.dfa = self.regExpr.toDFA()

alphabetBF = {'a', 'b', 'c', '0', '1', '2'}

alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '(', ')'}

def randomRegex(alphabetBF, alphabetRegex, min_length=10, max_length=20,):
    if not alphabetRegex or not alphabetBF:
      return False, '', '', {}

    while True:
        length = random.randint(min_length, max_length)
        s = ''
        curAlph = set(random.sample(list(alphabetBF), k=random.randint(1, min(len(alphabetBF), 2))))
        if alphabetRegex == alphabetBF:
            alphabetRegex = curAlph  
        else:
            alphabetRegex = curAlph | {'*', '(', ')'}
        for _ in range(length):
          symb = random.choice(list(alphabetRegex))
          s += symb
        
        try:
            r = str2regexp(s)
            return True, r, s, curAlph  
        except Exception as e:

            #print(f"Ошибка: {e}. Пробуем снова.")
            continue 


def generateRandomRegex(lexemRegex, alphabetBF, alphabetRegex):
  global countGens 
  countGens+=1
  for lexem in lexemRegex:
    if not alphabetBF:
       return False, lexemRegex
    #print(f"generating for {lexem.name}")
    minLenRegex = 1
    maxLenRegex = 20
    regExpr = RegExp()
    regStr = ''
    sigma = {}
    if lexem.name in ('eol', 'blank'):
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
      while len(sigma) > 2:
        e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)

      alphabetBF = alphabetBF - sigma
      alphabetRegex = alphabetRegex - sigma

    elif lexem.name in ('sep', 'equal'):
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetBF, minLenRegex, maxLenRegex) # передаем alphabetBF = alphabetRegex, для соблюдения условия конечности языка
      while len(sigma) > 2:
        e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetBF, minLenRegex, maxLenRegex)
      firstLetter = getFirstLetter(regStr, alphabetBF)
      secondLetter = getLastLetter(regStr, alphabetBF)
      alphabetBF = alphabetBF - {firstLetter, secondLetter}
      alphabetRegex = alphabetRegex - {firstLetter, secondLetter}

    elif lexem.name in ('var', 'const'):
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
      
      while regStr.count('*') == 0 and len(sigma) > 2:
        #print(regExpr)
        e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
    else:
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
      while len(sigma) > 2:
        e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
      if len(sigma) != 2:
        return False, lexemRegex
    if len(sigma) > 2:
      return False, lexemRegex

    #lexemRegex[lexem][0], lexemRegex[lexem][1] = regExpr, sigma
    lexem.sigma = sigma
    lexem.regExpr = regExpr
    lexem.regStr = regStr
    if not e:
        return False, lexemRegex

  return True, lexemRegex

def getLastLetter(word, alph):
  for i in range(len(word)-1, -1, -1):
    if word[i] in alph:
      return word[i]

def getFirstLetter(word, alph):
  for i in range(0, len(word)):
    if word[i] in alph:
      return word[i]

def checkIntersection(dfa1, dfa2):
    intersection_dfa = dfa1 & dfa2
    return intersection_dfa.Final


def checkCorrection(lexemObjects):
  global countChecks, alphabetBF, alphabetRegex
  countChecks+=1

  for lexem in lexemObjects:
    if not lexem.sigma:
        #for lex in lexemObjects:
        #  print(lex.name, lex.sigma, lex.regStr)
        return False, f"Some alphabets are empty"

  if lexemObjects[0].sigma & lexemObjects[1].sigma:
    return False, "Alphabets for eol and blank have non-zero untersection"

  for i in range(12):
    lexemObjects[i].regExpr.reduced()

  for i in range(6, len(lexemObjects)):
     lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
 
  for lexem in lexemObjects:
    if lexem.name in ('eol', 'blank'):
        alphabetBF = alphabetBF - lexem.sigma
        alphabetRegex = alphabetRegex - lexem.sigma

    elif lexem.name in ('sep', 'equal'):
        
        firstLetter = getFirstLetter(lexem.regStr, alphabetBF)
        secondLetter = getLastLetter(lexem.regStr, alphabetBF)
        alphabetBF = alphabetBF - {firstLetter, secondLetter}
        alphabetRegex = alphabetRegex - {firstLetter, secondLetter}
  #for lex in lexemObjects:
  #  print(lex.name, lex.sigma, lex.regStr)
  while True:
    #print("altern brackets:")
    fl = True
    for i in range(6, len(lexemObjects)):
        if not fl:
          break
        for j in range(i + 1, len(lexemObjects)):
            if not fl:
               break
            if checkIntersection(lexemObjects[i].dfa, lexemObjects[j].dfa):
                fl = False
                for i in range(6, len(lexemObjects)):
                    e, lexemObjects[i].regExpr, lexemObjects[i].regStr, lexemObjects[i].sigma = randomRegex(alphabetBF, alphabetRegex)
                    
                    lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                    #print(False, f"Languages for {lexemObjects[i].name} and {lexemObjects[j].name} have non-zero intersection")


    for i in range(6, len(lexemObjects)):
        if not fl:
          break
        for j in range(i + 1, len(lexemObjects)):
            if not fl:
              break
            combinedDFA = lexemObjects[i].dfa.concat(lexemObjects[j].dfa)
            for k in range(6, len(lexemObjects)):
                if not fl:
                  break
                if checkIntersection(lexemObjects[k].dfa, combinedDFA):
                    fl = False
                    for i in range(6, len(lexemObjects)):
                        e, lexemObjects[i].regExpr, lexemObjects[i].regStr, lexemObjects[i].sigma = randomRegex(alphabetBF, alphabetRegex)
                        lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                        #print(False, f"Concatenated languages for {lexemObjects[i].name} and {lexemObjects[j].name} should not intersect any single bracket language.")
                
    if fl:
      break
  return True, ""

# {lexem : ['reg', sigma], ..}

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
  e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)

  #print(lexemObjects)
  fl, mes = checkCorrection(lexemObjects)

  print(fl, ': ' + mes)
  while not fl or not e:
    alphabetBF = {'a', 'b', 'c', '0', '1', '2'}
    alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '(', ')', '|'}

    e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)
  # for lex in lexemObjects:
    #  print(lex.name, lex.sigma, lex.regStr)
    if not e:
      continue
    fl, mes = checkCorrection(lexemObjects)
    #print(fl, ': ' + mes)
  
  print('Regular expressions for lexems:\n')
  for lex in lexemObjects:
    print(lex.name, lex.regStr)
  print()
  #print(time() - start)

  #print(countChecks, countGens)

  return lexemObjects
