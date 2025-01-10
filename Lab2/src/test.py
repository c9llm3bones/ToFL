import random
from FAdo.fa import *
from FAdo.reex import *
from time import time

# Constants
MIN_REGEX_LENGTH = 5
MAX_REGEX_LENGTH = 10

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

# Initial alphabets
alphabetBF = {'a', 'b', 'c', '0', '1', '2'}
alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '(', ')'}

def randomRegex(alphabetBF, alphabetRegex, min_length=10, max_length=20):
    if not alphabetRegex or not alphabetBF:
        return False, None, '', set()

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
    countGens += 1
    
    for lexem in lexemRegex:
        if not alphabetBF:
            return False, lexemRegex
            
        regExpr = RegExp()
        regStr = ''
        sigma = set()
        
        if lexem.name in ('eol', 'blank'):
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            while len(sigma) > 2:
                e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            alphabetBF = alphabetBF - sigma
            alphabetRegex = alphabetRegex - sigma

        elif lexem.name in ('sep', 'equal'):
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetBF, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            while len(sigma) > 2:
                e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetBF, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            firstLetter = getFirstLetter(regStr, alphabetBF)
            secondLetter = getLastLetter(regStr, alphabetBF)
            alphabetBF = alphabetBF - {firstLetter, secondLetter}
            alphabetRegex = alphabetRegex - {firstLetter, secondLetter}

        elif lexem.name in ('const'):
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            while regStr.count('*') == 0 and len(sigma) > 2:
                #print(regExpr)
                e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)

          
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
        elif lexem.name in ('var'):
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            
            while lexemObjects[4].regStr.count('*') == 0 or regStr.count('*') == 0 or len(sigma) > 2 or checkIntersection(lexemObjects[4].regExpr.toDFA(), regExpr.toDFA()):
                countGens += 1
                #print(regExpr, '||',lexemObjects[4].regExpr) 
                e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH) 
                e, lexemObjects[4].regExpr, lexemObjects[4].regStr, lexemObjects[4].sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
                if countGens % 100 == 0:
                    return False, lexemRegex
        
        else:
            e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
            while len(sigma) > 2:
                e, regExpr, regStr, sigma = randomRegex(alphabetBF, alphabetRegex, MIN_REGEX_LENGTH, MAX_REGEX_LENGTH)
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
    countChecks += 1

    for lexem in lexemObjects:
        if not lexem.sigma:
            #for lex in lexemObjects:
              #print(lex.name, lex.sigma, lex.regStr)
            return False, "Some alphabets are empty"

    if lexemObjects[0].sigma & lexemObjects[1].sigma:
        return False, "Alphabets for eol and blank have non-zero intersection"

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
    #    print(lex.name, lex.sigma, lex.regStr)
    while True:
        countChecks += 1
        if countChecks % 100 == 0:
            return False, "Too many checks"
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
            for i in range(6, len(lexemObjects)):
                lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                if checkIntersection(lexemObjects[i].dfa, lexemObjects[4].regExpr.toDFA()) or checkIntersection(lexemObjects[i].dfa, lexemObjects[5].regExpr.toDFA()):
                    #fl = False
                    return False, "INTERSECTION FOR br and var, const"
                

        if fl:
            break
  
    for i in range(6, len(lexemObjects)):
        lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
        print(checkIntersection(lexemObjects[i].dfa, lexemObjects[4].regExpr.toDFA()), 
              checkIntersection(lexemObjects[i].dfa, lexemObjects[5].regExpr.toDFA()))
      
    return True, ""

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

def generateLexems():
  # Initialize lexemes
  
  global alphabetBF, alphabetRegex, lexemObjects  

  # Main execution
  start = time()
  print("starting...")
  e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)

  #print(lexemObjects)
  fl, mes = checkCorrection(lexemObjects)

  #print(fl, ': ' + mes)
  while not fl or not e:
      alphabetBF = {'a', 'b', 'c', '0', '1', '2'}
      alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '(', ')', '|'}

      e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)
  # for lex in lexemObjects:
    #  print(lex.name, lex.sigma, lex.regStr)
      if not e:
          continue
      fl, mes = checkCorrection(lexemObjects)
      print(fl, ': ' + mes)

  for lex in lexemObjects:
      print(lex.name, lex.regStr)

  print(time() - start)
  print(countChecks, countGens)
  print(checkIntersection(lexemObjects[4].regExpr.toDFA(), lexemObjects[5].regExpr.toDFA()))

  return lexemObjects

#lexemObjects = generateLexems()