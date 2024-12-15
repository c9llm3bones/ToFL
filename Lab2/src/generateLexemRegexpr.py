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
        self.sigmaLen = 0

    def setRegex(self, regStr, sigma):
        self.regStr = regStr
        self.sigma = sigma
        self.regExpr = str2regexp(regStr)
        self.dfa = self.regExpr.toDFA()

alphabetBF = {'a', 'b', 'c', '0', '1', '2'}

alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '|', '(', ')'}

def setAlphabetsLen(lexemObjects):
  hasTwo = False
  i = 0
  while (not hasTwo) and i < 4:
    curLen = random.randint(1, 2)
    if curLen == 2:
      hasTwo = True
    lexemObjects[i].sigmaLen = curLen
    i += 1
  
  if not hasTwo:
    lexemObjects[random.randint(0, 3)].sigmaLen = 2
    
  for j in range(i, len(lexemObjects)):
    lexemObjects[j].sigmaLen = 1
  
def generate_regex(alphabetBF, isFinal, AlphLen, min_length=10, max_length=100):
    
  if AlphLen > len(alphabetBF) or not alphabetBF:
    return False, '', '', {}
  chosen_alphabet = random.sample(list(alphabetBF), AlphLen)
  
  def ensure_all_used(expression, alphabet):
      unused = [char for char in alphabet if char not in expression]
      while unused:
          expression += f"|{random.choice(unused)}"
          unused = [char for char in alphabet if char not in expression]
      return expression
  
  def generate_recursive(current_length, alphabet, is_final):
      if current_length <= 0:
          return random.choice(alphabet)
      
      operation = random.choice(['concat', 'union', 'group'])
      
      if operation == 'concat':
          part1 = generate_recursive(current_length // 2, alphabet, is_final)
          part2 = generate_recursive(current_length // 2, alphabet, is_final)
          return part1 + part2

      elif operation == 'union':
          part1 = generate_recursive(current_length // 2, alphabet, is_final)
          part2 = generate_recursive(current_length // 2, alphabet, is_final)
          return f"({part1}|{part2})"
      
      elif operation == 'group':
          inner = generate_recursive(current_length - 2, alphabet, is_final)
          if not is_final:
              return f"({inner})*"
          else:
              return f"({inner})"
  
  regex_length = random.randint(min_length, max_length)
  
  regex = generate_recursive(regex_length, chosen_alphabet, isFinal)
  regex = ensure_all_used(regex, chosen_alphabet)
  
    
    
  return True, str2regexp(regex), regex, set(chosen_alphabet)

def randomRegex(alphabetBF, isFinal, AlphLen, min_length=20, max_length=50,):
    if not alphabetRegex or not alphabetBF:
      return False, '', '', {}

    while True:
        length = random.randint(min_length, max_length)
        s = ''
        curAlph = set(random.sample(list(alphabetBF), k=AlphLen))
        if not isFinal: #если sep/equal
            curAlph = curAlph | {'*', '|', '(', ')'}
        
        counter = set()
        while len(counter) != AlphLen:
          for _ in range(length):
            symb = random.choice(list(curAlph))
            s += symb
            if symb in alphabetBF:
              counter.add(symb) 
        
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
    minLenRegex = 2 # >1
    maxLenRegex = 5 # >= minLenRegex
    regExpr = RegExp()
    regStr = ''
    sigma = {}
    isFinal = True if lexem.name in ('equal', 'sep') else False
    
    if lexem.name in ('eol', 'blank'):
      e, regExpr, regStr, sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen)
      #print(regExpr)
      alphabetBF = alphabetBF - sigma
      alphabetRegex = alphabetRegex - sigma

    elif lexem.name in ('sep', 'equal'):
      e, regExpr, regStr, sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen) # передаем alphabetBF = alphabetRegex, для соблюдения условия конечности языка
      
      firstLetter = getFirstLetter(regStr, alphabetBF)
      secondLetter = getLastLetter(regStr, alphabetBF)
      alphabetBF = alphabetBF - {firstLetter, secondLetter}
      alphabetRegex = alphabetRegex - {firstLetter, secondLetter}

    elif lexem.name in ('var', 'const'):
      e, regExpr, regStr, sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen)    
        
    else:
      e, regExpr, regStr, sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen)

    #lexemRegex[lexem][0], lexemRegex[lexem][1] = regExpr, sigma
    lexem.sigma = sigma
    lexem.regExpr = regExpr
    lexem.regStr = regStr
    if not e:
        return False, lexemRegex
  """inters = checkIntersection(lexemRegex[4].regExpr.toDFA(), lexemRegex[5].regExpr.toDFA())
  while inters:
    print(inters)
    e, lexemRegex[4].regExpr, lexemRegex[4].regStr, lexemRegex[4].sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen)
    e, lexemRegex[5].regExpr, lexemRegex[5].regStr, lexemRegex[5].sigma = generate_regex(alphabetBF, isFinal, lexem.sigmaLen)
    inters = checkIntersection(lexemRegex[4].regExpr.toDFA(), lexemRegex[5].regExpr.toDFA())
    """
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

def generate_regex_br(alphabet, n, max_depth=3):
    single_symbol = list(alphabet)[0]  
 
    s = ''
    for _ in range(n):
        insertStar = random.randint(0, 1)
        if insertStar and max_depth:
            s += single_symbol + '*'
            max_depth-=1    
        s += single_symbol
    
    return s

def integrate_bracket_generation(lexem_objects, alphabetBF):
    n = random.randint(1, 5)  # Случайное начальное значение 
    for _ in range(4, len(lexem_objects)):
        
        reg_str= generate_regex_br(alphabetBF, n)
        print(reg_str)
        n=n*2 + 1

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
  n = 3
  for i in range(6, len(lexemObjects)):
    lexemObjects[i].regStr= generate_regex_br(alphabetBF, n)
    lexemObjects[i].regExpr = str2regexp(lexemObjects[i].regStr)
    lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
    print(lexemObjects[i].regStr)
    n = n*2 + 1
    
  print(alphabetBF)
  while True:
    print("altern brackets:")
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
                    #e, lexemObjects[i].regExpr, lexemObjects[i].regStr, lexemObjects[i].sigma = generate_regex(alphabetBF, False, lexemObjects[i].sigmaLen)
                    
                    #lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                    print(False, f"Languages for {lexemObjects[i].name} and {lexemObjects[j].name} have non-zero intersection")
                    print(lexemObjects[i].regStr, lexemObjects[j].regStr)
    print('brackets do not intersect')
    return
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
                        e, lexemObjects[i].regExpr, lexemObjects[i].regStr, lexemObjects[i].sigma = generate_regex(alphabetBF, alphabetRegex)
                        lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                        print(False, f"Concatenated languages for {lexemObjects[i].name} and {lexemObjects[j].name} should not intersect any single bracket language.")
                
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
  setAlphabetsLen(lexemObjects)
  for lexem in lexemObjects:
    print(lexem.name, ' ', lexem.sigmaLen)
  
  
  e, lexemObjects = generateRandomRegex(lexemObjects, alphabetBF, alphabetRegex)
  
  for lexem in lexemObjects:
    print(lexem.name, lexem.regExpr, lexem.sigmaLen, lexem.sigma)
  lexemObjects[0].regExpr.toDFA().display()
  
  #print(lexemObjects)
  print(checkIntersection(lexemObjects[4].regExpr.toDFA(), lexemObjects[5].regExpr.toDFA()))
  
  fl, mes = checkCorrection(lexemObjects)
  exit(0)
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
