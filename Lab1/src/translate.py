import pandas as pd 
from deep_translator import GoogleTranslator 
import json 
import time

def translate_text(text, source_language, target_language): 
    try:
        return GoogleTranslator(source=source_language, target=target_language).translate(text)
    except Exception as e:
        print(f"Error during translation: {e}")
        return None

file_path = './augmented_data.json' 
data = pd.read_json(file_path) 

translated_data = [] 
start_index = 0

try:
    with open('translated_augmented_data.json', 'r', encoding='utf-8') as f:
        translated_data = json.load(f)
        start_index = len(translated_data) // 4  
except (FileNotFoundError, json.JSONDecodeError):
    
    translated_data = []

for index in range(start_index, len(data)):
    item = data.iloc[index]
    print(f"Translating {index}...") 
    original_question = item['question'] 
    original_answer = item['answer'] 
    
    translated_question = translate_text(original_question, 'ru', 'en') 
    translated_answer = translate_text(original_answer, 'ru', 'en') 
    
    if translated_question and translated_answer:
        translated_data.append({ 
            'question': translated_question, 
            'answer': translated_answer 
        }) 

    with open('translated_augmented_data.json', 'w', encoding='utf-8') as f: 
        json.dump(translated_data, f, ensure_ascii=False, indent=4)

    

print("Translation completed.")
