from FAdo.fa import *
from FAdo.reex import *
from random import choice, randint

def generate_non_intersecting_regex(existing_regexes, alphabet, max_attempts=1000):
    for _ in range(max_attempts):
        reg_str = generate_random_regex(alphabet)
        candidate_regex = str2regexp(reg_str)
        has_intersection = False
        
        for existing in existing_regexes:
            existing_dfa = existing.toDFA()
            candidate_dfa = candidate_regex.toDFA()
            if (existing_dfa & candidate_dfa).emptyP() is False:
                has_intersection = True
                break
        
        if not has_intersection:
            return candidate_regex, reg_str

    raise ValueError("Не удалось сгенерировать непересекающееся регулярное выражение.")

def generate_random_regex(alphabet, min_length=3, max_length=10):
    reg = "".join(choice(alphabet) for _ in range(randint(min_length, max_length)))
    if randint(0, 1):
        reg += "*"  # Добавляем звёздочку с вероятностью 50%
    return reg

# Пример использования
alphabet = ['b']
existing_regexes = [str2regexp("bb"), str2regexp("b*bb*bbbb*bbb")]

try:
    new_regex, reg_str = generate_non_intersecting_regex(existing_regexes, alphabet)
    print(f"Новая регулярка: {reg_str}")
    print(f"Описание: {new_regex}")
except ValueError as e:
    print(str(e))
