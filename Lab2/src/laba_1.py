import requests
import os
import random
from time import time 

class MATAPI:
    def __init__(self, base_url="http://0.0.0.0:8000"):
        self.base_url = base_url

    def membership_query(self, word):
        print(f"Отправка запроса на {self.base_url}/checkMembership/ с параметром word={word}")
        try:
            response = requests.post(
                f"{self.base_url}/checkMembership/",
                json={"inputString": word}
            )
            if response.status_code == 200:
                print("Проверка слова - Ok")
                return response.json().get("result") == 1
            else:
                print(
                    f"Ошибка при проверке слова через API. Код ответа: {response.status_code}, Тело ответа: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса membership_query: {e}")
        return False

    def equivalence_query(self, hypothesis_sequences):
        table_str = {seq: "1" for seq in hypothesis_sequences if seq is not None}
        
        if '@epsilon' not in table_str:
            table_str['@epsilon'] = "1"
        print(table_str)
        print(f"Отправка запроса на {self.base_url}/checkEquivalence/ с таблицей гипотез.")
        print(f"Содержимое equivalenceTable для отладки: {table_str}")

        try:
            response = requests.post(
                f"{self.base_url}/checkEquivalence/",
                json={"equivalenceTable": table_str}
            )
            if response.status_code == 200:
                response_data = response.json()
                print("Проверка эквивалентности - Ok")
                if response_data.get("result") == "TRUE":
                    return True, None
                else:
                    return False, response_data.get("result")
            else:
                print(
                    f"Ошибка при проверке таблицы через API. Код ответа: {response.status_code}, Тело ответа: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса equivalence_query: {e}")
        return False, None


class SequenceGenerator:
    def __init__(self):
        self.alphabet = ["a", "b", "c", "0", "1", "2"]

    def generate_const(self):
        return ''.join(random.choice(self.alphabet) for _ in range(random.randint(1, 3)))

    def generate_var(self):
        return ''.join(random.choice(self.alphabet) for _ in range(random.randint(1, 3)))

    def generate_expression(self):
        expression_type = random.choice(["var", "const", "nested"])
        if expression_type == "var":
            return self.generate_var()
        elif expression_type == "const":
            return self.generate_const()
        elif expression_type == "nested":
            outer_brackets = random.choice([("(", ")"), ("{", "}"), ("[", "]")])
            return f"{outer_brackets[0]} {self.generate_const()} {self.generate_expression()} {outer_brackets[1]}"

    def generate_sentence(self):
        pattern = self.generate_var()
        expression = self.generate_expression()
        return f"{pattern} = {expression} ;"

    def generate_definition(self):
        const = self.generate_const()
        sentences = "\n".join(self.generate_sentence() for _ in range(random.randint(1, 3)))
        return f"{const} (\n{sentences}\n)"

    def generate_program(self, num_definitions=2):
        definitions = "\n\n".join(self.generate_definition() for _ in range(num_definitions))
        return definitions + "\n"


class LearnerBrainfuckRefal:
    def __init__(self, teacher, max_iterations=10):
        self.teacher = teacher
        self.hypothesis = set()
        self.max_iterations = max_iterations

    def learn_language(self):
        print("Генерация - Ok")
        generator = SequenceGenerator()
        for _ in range(10):
            example = generator.generate_program()
            if self.teacher.membership_query(example):
                print(f"Добавляем '{example}' в начальную гипотезу.")
                self.hypothesis.add(example)

        iterations = 0
        while iterations < self.max_iterations:
            iterations += 1
            print(f"\nИтерация № {iterations} - Проверка гипотезы - Ok")

            equivalent, counterexample = self.teacher.equivalence_query(self.hypothesis)
            if equivalent:
                print("Гипотеза соответствует целевому языку!")
                break

            print(f"Гипотеза не соответствует. Контрпример: '{counterexample}'")
            if counterexample and counterexample not in self.hypothesis:
                print(f"Добавляем контрпример '{counterexample}' в гипотезу.")
                self.hypothesis.add(counterexample)
            else:
                print(f"Пропуск некорректного контрпримера '{counterexample}'.")

        print("Обучение завершено - Ok")
        return self.hypothesis

start = time()
teacher = MATAPI(base_url="http://127.0.0.1:8000")
learner = LearnerBrainfuckRefal(teacher, max_iterations=100)
final_hypothesis = learner.learn_language()
print("\nРезультат:\n", final_hypothesis)
print(time() - start)