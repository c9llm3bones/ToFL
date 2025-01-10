import pandas as pd

df = pd.read_excel('bz.xlsx', sheet_name='F.A.Q.')

existing_questions_set = set()

for column in df.columns:
    column_values = df[column].dropna().tolist()
    existing_questions_set.update(column_values)

print(existing_questions_set)
print(len(existing_questions_set))