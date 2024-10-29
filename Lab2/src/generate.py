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
        self.regExp = None
        self.dfa = None

    def setRegex(self, regStr, sigma):
        self.regStr = regStr
        self.sigma = sigma
        self.regExp = str2regexp(regStr)
        self.dfa = self.regExp.toNFA().toDFA()

alphabetBF = {'a', 'b', 'c', '0', '1', '2'}

alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '+', '(', ')'}

def randomRegex(alphabetBF, alphabetRegex, min_length=1, max_length=10,):
    if not alphabetRegex or not alphabetBF:
      return False, '', ''

    while True:
        length = random.randint(min_length, max_length)
        sigma = set()
        s = ''
        
        for _ in range(length):
          symb = random.choice(list(alphabetRegex))
          if symb in alphabetBF:
            sigma.add(symb)
          s += symb

        # Проверка с помощью str2regexp
        try:
            r = str2regexp(s)
            return True, r, s, sigma  # Если не возникает ошибки, возвращаем регулярку
        except Exception as e:

            #print(f"Ошибка: {e}. Пробуем снова.")
            continue  # Если есть ошибка, пробуем снова


def generateRandomRegex(lexemRegex, alphabetBF, alphabetRegex):
  global countGens
  countGens+=1
  for lexem in lexemRegex:
    if not alphabetBF:
       return False, lexemRegex
    #print(f"generating for {lexem.name}")
    minLenRegex = 1
    maxLenRegex = 5
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

      firstLetter = getFirstLetter(regStr, alphabetBF)
      secondLetter = getLastLetter(regStr, alphabetBF)
      alphabetBF = alphabetBF - {firstLetter, secondLetter}
      alphabetRegex = alphabetRegex - {firstLetter, secondLetter}

    elif lexem.name in ('var', 'const'):
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)

      while regStr.count('+') == 0 and regStr.count('*') == 0:
        #print(regExpr)
        e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
    else:
      e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, minLenRegex, maxLenRegex)
    
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
    return not intersection_dfa.Final


def checkCorrection(lexemObjects):
  global countChecks
  countChecks+=1
  for lexem in lexemObjects:
    if not lexem.sigma:
        return False, f"Some alphabets are empty"

  if lexemObjects[0].sigma & lexemObjects[1].sigma:
    return False, "Alphabets for eol and blank have non-zero untersection"
  
  for i in range(6, len(lexemObjects)):
     lexemObjects[i].dfa = lexemObjects[i].regExpr.toNFA().toDFA()


  for i in range(6, len(lexemObjects)):
      for j in range(i + 1, len(lexemObjects)):
          if not checkIntersection(lexemObjects[i].dfa, lexemObjects[j].dfa):
              return False, f"Languages for {lexemObjects[i].name} and {lexemObjects[j].name} have non-zero intersection"

  
  for i in range(6, len(lexemObjects)):
      for j in range(i + 1, len(lexemObjects)):
          combinedDFA = lexemObjects[i].dfa.concat(lexemObjects[j].dfa)
          for k in range(6, len(lexemObjects)):
              if not checkIntersection(lexemObjects[k].dfa, combinedDFA):
                  return False, f"Concatenated languages for {lexemObjects[i].name} and {lexemObjects[j].name} should not intersect any single bracket language."
  
  return True, ""

# {lexem : ['reg', sigma], ..}

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
print("starting...")
e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)

#print(lexemObjects)
fl, mes = checkCorrection(lexemObjects)

print(fl, ': ' + mes)
while not fl or not e:
  alphabetBF = {'a', 'b', 'c', '0', '1', '2'}
  alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '+', '(', ')'}
  
  e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)
 # for lex in lexemObjects:
   #  print(lex.name, lex.sigma, lex.regStr)
  fl, mes = checkCorrection(lexemObjects)
  print(fl, ': ' + mes)
for lex in lexemObjects:
  print(lex.name, lex.sigma, lex.regStr)
print(time() - start)

print(countChecks, countGens)