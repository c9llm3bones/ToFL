import random
from typing import List, Set
from FAdo.fa import *
from FAdo.reex import *
from time import time

############################
# Класс Lexema
############################

class Lexema:
    def __init__(self, name):
        self.name = name
        self.sigma: Set[str] = set()
        self.regStr = ''
        self.regExpr = None
        self.dfa = None
        self.sigmaLen = 0

    def setRegex(self, regStr, sigma):
        self.regStr = regStr
        self.sigma = sigma
        self.sigmaLen = len(sigma)
        self.regExpr = str2regexp(regStr)
        self.dfa = self.regExpr.toDFA()

############################
# Основная функция распределения алфавита и генерации
############################

def checkIntersection(dfa1, dfa2):
    intersection_dfa = dfa1 & dfa2
    return intersection_dfa.Final

alphabetBF = {'a', 'b', 'c', '0', '1', '2'}
alphabetRegex = {'a', 'b', 'c', '0', '1', '2', '*', '(', ')'}

def generate_recursive(current_length, alphabet, is_final):
    if current_length <= 0:
        return random.choice(alphabet)
    
    operation = random.choice(['concat', 'group'])
    
    if operation == 'concat':
        part1 = generate_recursive(current_length // 2, alphabet, is_final)
        part2 = generate_recursive(current_length // 2, alphabet, is_final)
        return part1 + part2
    
    elif operation == 'group':
        inner = generate_recursive(current_length - 2, alphabet, is_final)
        if not is_final:
            return f"({inner})*"
        else:
            return f"({inner})"

def generate_regex(alphabetBF, isFinal, AlphLen, min_length=3, max_length=20):
    
  if AlphLen > len(alphabetBF) or not alphabetBF:
    return False, '', '', {}
  chosen_alphabet = random.sample(list(alphabetBF), AlphLen)
  
  def ensure_all_used(expression, alphabet):
      unused = [char for char in alphabet if char not in expression]
      while unused:
          expression += f"{random.choice(unused)}"
          unused = [char for char in alphabet if char not in expression]
      return expression
  
  
  regex_length = random.randint(min_length, max_length)
  
  regex = generate_recursive(regex_length, chosen_alphabet, isFinal)
  regex = ensure_all_used(regex, chosen_alphabet)
      
  return regex


def generate_kostyl(symbol, lexemObjects, n=1):
    for i in range(6, len(lexemObjects)):
        lexemObjects[i].regStr = generate_regex_br(symbol, n)
        lexemObjects[i].regExpr = str2regexp(lexemObjects[i].regStr)
        lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
        #print(lexemObjects[i].regStr)
        n = n*2 + 1
  
    lexemObjects[4].setRegex(generateRegexVarConst(symbol, lexemObjects[-1].regStr, False), {symbol}) 
    lexemObjects[5].setRegex(generateRegexVarConst(symbol, lexemObjects[-1].regStr, True), {symbol})

def generate_regex_br(symb, n):
    return symb * n

def generateRegexVarConst(symbol, regStr, is_var):
    #regex_length = random.randint(min_length, max_length)
    #regex = regStr + generate_recursive(regex_length, list(symb), False)
      
    if is_var:
        regex = f"{regStr}({symbol}{symbol})*{symbol}{symbol}"
    else:
        regex = f"{regStr}({symbol}{symbol})*{symbol}"

    return regex

def generate_br_var_const(lexemObjects, remain_syms):
    countChecks = 0
    
    while countChecks < 100:
        countChecks += 1
        #print("altern brackets:")
        fl = True
        if checkIntersection(lexemObjects[4].regExpr.toDFA(), lexemObjects[5].regExpr.toDFA()):
            fl = False
            for i in range(4, len(lexemObjects)):
                lexemObjects[i].sigmaLen = random.randint(1, 2)
                lexemObjects[i].sigma = remain_syms[:lexemObjects[i].sigmaLen]
                lexemObjects[i].setRegex(generate_regex(lexemObjects[i].sigma, True if i >= 6 else False, len(lexemObjects[i].sigma)), lexemObjects[i].sigma)
        for i in range(6, len(lexemObjects)):
            if not fl:
                break
            for j in range(i + 1, len(lexemObjects)):
                if not fl:
                    break
                if checkIntersection(lexemObjects[i].dfa, lexemObjects[j].dfa):
                    fl = False
                    for i in range(4, len(lexemObjects)):  
                        lexemObjects[i].sigmaLen = random.randint(1, 2)
                        lexemObjects[i].sigma = remain_syms[:lexemObjects[i].sigmaLen]
                        lexemObjects[i].setRegex(generate_regex(lexemObjects[i].sigma, True if i >= 6 else False, len(lexemObjects[i].sigma)), lexemObjects[i].sigma)
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
                        for i in range(4, len(lexemObjects)):  # Все остальные lexemObjects:
                            lexemObjects[i].sigmaLen = random.randint(1, 2)
                            lexemObjects[i].sigma = remain_syms[:lexemObjects[i].sigmaLen]
                            lexemObjects[i].setRegex(generate_regex(lexemObjects[i].sigma, True if i >= 6 else False, len(lexemObjects[i].sigma)), lexemObjects[i].sigma)
                        #print(False, f"Languages for {lexemObjects[i].name} and {lexemObjects[j].name} have non-zero intersection")

            for i in range(6, len(lexemObjects)):
                lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
                if checkIntersection(lexemObjects[i].dfa, lexemObjects[4].regExpr.toDFA()) or checkIntersection(lexemObjects[i].dfa, lexemObjects[5].regExpr.toDFA()):
                    fl = False
                    #return False, "INTERSECTION FOR br and var, const"
        if fl:
            break
    if fl:
        #print("OK for br, var, const")
        return True, "OK"
    return False, "INTERSECTION FOR br and var, const"
def distribute_and_generate(lexemObjects):
   
    all_symbols = ['a','b','c','0','1','2']
    random.shuffle(all_symbols)

    used_symbols = set()

    # Ветвление: "даём 2 eol/blank?" (да/нет)
    give_2_eol_blank = random.choice([True, False])

    if give_2_eol_blank:
        # "Случайно распределяем 3 символа между eol и blank (хотя бы 1 в каждый)"
        chosen_3 = all_symbols[:3]   # первые 3
        all_symbols_left = all_symbols[3:]  # оставшиеся 3

        split_mode = random.choice([(1,2),(2,1)])
        eol_sigma   = set(chosen_3[:split_mode[0]])
        blank_sigma = set(chosen_3[split_mode[0]:split_mode[0] + split_mode[1]])

        # Заполняем eol
        eol_reg_str = generate_regex(eol_sigma, False, len(eol_sigma))
        #print(eol_reg_str)
        lexemObjects[0].setRegex(eol_reg_str, eol_sigma)

        # Заполняем blank
        blank_reg_str = generate_regex(blank_sigma, False, len(blank_sigma))
        lexemObjects[1].setRegex(blank_reg_str, blank_sigma)

        used_symbols.update(eol_sigma)
        used_symbols.update(blank_sigma)

        # "equal и sep забирают ровно 2 символа из оставшегося алфавита"
        eq_sep_chosen = all_symbols_left[:2]
        leftover_after_eq_sep = all_symbols_left[2:]  # 1 символ остаётся

        eq_ch = eq_sep_chosen[0]
        sep_ch = eq_sep_chosen[1]

        # Попробуем взять "middle" из leftover_after_eq_sep (если есть)
        mid_sym = leftover_after_eq_sep[0] if leftover_after_eq_sep else None

        if mid_sym:
            eq_sigma = {eq_ch, mid_sym}
            sep_sigma = {sep_ch, mid_sym}
        else:
            eq_sigma = {eq_ch}
            sep_sigma = {sep_ch}

        # Пример: "eq_ch + (regex over eq_sigma) + eq_ch"
        eq_reg_str  = eq_ch + generate_regex(eq_sigma, True, len(eq_sigma)) + eq_ch
        sep_reg_str = sep_ch + generate_regex(sep_sigma, True, len(sep_sigma)) + sep_ch

        lexemObjects[2].setRegex(eq_reg_str, eq_sigma)
        lexemObjects[3].setRegex(sep_reg_str, sep_sigma)

        used_symbols.update(eq_sigma - {mid_sym})
        used_symbols.update(sep_sigma - {mid_sym})

        # "Костыль" для остальных (var, const, lbr-1, rbr-2,...)
        remain_syms = set(all_symbols) - used_symbols
        for i in range(4):
            print(lexemObjects[i].name, lexemObjects[i].sigma, lexemObjects[i].regStr)
        generate_kostyl(list(remain_syms)[0], lexemObjects)

        return lexemObjects

    else:
        # "нет" — даём по одному символу на eol, blank
        chosen_2 = all_symbols[:2]
        all_symbols_left = all_symbols[2:]  # осталось 4

        eol_sigma = {chosen_2[0]}
        blank_sigma = {chosen_2[1]}

        eol_reg_str = generate_regex(eol_sigma, False, len(eol_sigma))
        blank_reg_str = generate_regex(blank_sigma, False, len(blank_sigma))
        lexemObjects[0].setRegex(eol_reg_str, eol_sigma)
        lexemObjects[1].setRegex(blank_reg_str, blank_sigma)

        used_symbols.update(eol_sigma)
        used_symbols.update(blank_sigma)

        # Новое ветвление: "даём два символа equal/sep?"
        give_2_symbols_eq_sep = random.choice([True, False])

        if give_2_symbols_eq_sep:
            # equal и sep забирают 3 символа
            eq_sep_chosen = all_symbols_left[:3]
            leftover_after_eq_sep = all_symbols_left[3:]  # может быть 1 символ
            if len(eq_sep_chosen) < 3:
                # На всякий случай, если symbols = 2, safeguard
                return lexemObjects

            symb1, symb2, symb3 = eq_sep_chosen

            # Случайно решаем, кому отдать 2 символа (assign_2_to)
            assign_2_to = random.choice(["eq", "sep"])

            if assign_2_to == "eq":
                eq_sigma  = {symb1, symb2, leftover_after_eq_sep[0]} 
                eq_reg_str = symb1 + generate_regex(eq_sigma, True, len(eq_sigma)) + symb2

                sep_sigma = {symb3, leftover_after_eq_sep[0]}  
                sep_reg_str = symb3 + generate_regex(sep_sigma, True, len(sep_sigma)) + symb3

            else:
                sep_sigma = {symb1, symb2, leftover_after_eq_sep[0]}
                sep_reg_str = symb1 + generate_regex(sep_sigma, True, len(sep_sigma)) + symb2

                eq_sigma = {symb3, leftover_after_eq_sep[0]}
                eq_reg_str = symb3 + generate_regex(eq_sigma, True, len(eq_sigma)) + symb3

            lexemObjects[2].setRegex(eq_reg_str, eq_sigma)
            lexemObjects[3].setRegex(sep_reg_str, sep_sigma)

            used_symbols.update(eq_sigma - {leftover_after_eq_sep[0]})
            used_symbols.update(sep_sigma - {leftover_after_eq_sep[0]})
            # "Костыль" для остальных (var, const, lbr-1, rbr-2,...)
            remain_syms = set(all_symbols) - used_symbols

            generate_kostyl(list(remain_syms)[0], lexemObjects)

            return lexemObjects

        else:
            # "equal и sep забирают 2 символа (начинаются/заканчиваются одинаковыми),
            #  посередине 2 leftover"
            eq_sep_chosen = all_symbols_left[:2]
            leftover_after_eq_sep = all_symbols_left[2:]  # осталось 2

            if len(eq_sep_chosen) != 2:
                return lexemObjects

            eq_ch = eq_sep_chosen[0]
            sep_ch = eq_sep_chosen[1]

            eq_sigma = {eq_ch} | set(leftover_after_eq_sep)
            sep_sigma = {sep_ch} | set(leftover_after_eq_sep)

            eq_reg_str  = eq_ch  + generate_regex(eq_sigma, True, len(eq_sigma)) + eq_ch
            sep_reg_str = sep_ch + generate_regex(sep_sigma, True, len(sep_sigma)) + sep_ch

            lexemObjects[2].setRegex(eq_reg_str, eq_sigma)
            lexemObjects[3].setRegex(sep_reg_str, sep_sigma)

            used_symbols.update(eq_sigma - set(leftover_after_eq_sep))
            used_symbols.update(sep_sigma - set(leftover_after_eq_sep))

            remain_syms = list(set(all_symbols) - used_symbols)
            while True:
                # Если не будет получаться генерировать, то поставь скобки конечными

                for i in range(4, len(lexemObjects)):  # Все остальные lexemObjects:
                    lexemObjects[i].sigmaLen = random.randint(1, 2)
                    lexemObjects[i].sigma = remain_syms[:lexemObjects[i].sigmaLen]
                    regex = generate_regex(lexemObjects[i].sigma, True if i >= 6 else False, len(lexemObjects[i].sigma))
                    #print(regex)
                    lexemObjects[i].setRegex(regex, lexemObjects[i].sigma)

                if sum(x.sigmaLen for x in lexemObjects) == 8:
                    generate_kostyl(remain_syms[0], lexemObjects)
                    return lexemObjects

                e, mes = generate_br_var_const(lexemObjects, remain_syms)
                if not e:
                    #print(mes)
                    continue
                return lexemObjects

############################
# Тестовый запуск
############################
#42 - ветка "даём 2 eol/blank?" - да
#45 - ветка "даём 2 eol/blank?" - нет, даём 2 equal/sep - да
#52 - ветка "даём 2 eol/blank?" - нет, даём 2 equal/sep - нет
def generateLexems():
    #s = 45
    #random.seed(s)  # Для воспроизводимости
    start = time()
    print('Generating random lexems...\n')
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

    
    lexemes = distribute_and_generate(lexemObjects)
    
    # Проверка на "кол-во лексем", "непересечение" и т.д.
    # (Упрощённо: просто печатаем результат)
    #print(f"Try #{tries}:")
    for lx in lexemes:
        print(lx.name, lx.sigma, lx.regStr)
    print(checkIntersection(lexemObjects[4].regExpr.toDFA(), lexemObjects[5].regExpr.toDFA()))
    for i in range(6, len(lexemObjects)):
        lexemObjects[i].dfa = lexemObjects[i].regExpr.toDFA()
        print(checkIntersection(lexemObjects[i].dfa, lexemObjects[4].regExpr.toDFA()), 
            checkIntersection(lexemObjects[i].dfa, lexemObjects[5].regExpr.toDFA()))
    #print(s)
    print(time() - start)
    return lexemes