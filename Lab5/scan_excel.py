import pandas as pd

# Замените 'questions.xlsx' на путь к вашему файлу
# Замените 'Sheet1' на название нужного листа
df = pd.read_excel('bz.xlsx', sheet_name='F.A.Q.')

# Создаём пустое множество для всех вопросов
existing_questions_set = set()

# Проходимся по всем столбцам таблицы
for column in df.columns:
    # Извлекаем непустые значения из каждого столбца
    column_values = df[column].dropna().tolist()
    # Добавляем значения в множество (автоматически исключает дубликаты)
    existing_questions_set.update(column_values)

# Результат: множество уникальных вопросов
print(existing_questions_set)
print(len(existing_questions_set))