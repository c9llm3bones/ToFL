import pandas as pd 
from deep_translator import GoogleTranslator 
import json 
import time

file_path = './data.json' 
data = pd.read_json(file_path) 

def translate_text(text, source_language, target_language): 
    try:
        return GoogleTranslator(source=source_language, target=target_language).translate(text)
    except Exception as e:
        print(f"Error during translation: {e}")
        return None

translated_data = [] 
start_index = 0

try:
    with open('augmented_data.json', 'r', encoding='utf-8') as f:
        translated_data = json.load(f)
        start_index = len(translated_data) // 4  
except (FileNotFoundError, json.JSONDecodeError):
    
    translated_data = []

for index in range(start_index, len(data)):
    item = data.iloc[index]
    print(f"Translating {index}...") 
    original_question = item['question'] 
    original_answer = item['answer'] 
    
    #(ru->en->ru)
    first_translated_question = translate_text(original_question, 'ru', 'en') 
    first_back_translated_question = translate_text(first_translated_question, 'en', 'ru') 
    
    first_translated_answer = translate_text(original_answer, 'ru', 'en') 
    first_back_translated_answer = translate_text(first_translated_answer, 'en', 'ru') 

    #(ru->fr->ru)
    second_translated_question = translate_text(first_back_translated_question, 'ru', 'fr') 
    second_back_translated_question = translate_text(second_translated_question, 'fr', 'ru') 

    second_translated_answer = translate_text(first_back_translated_answer, 'ru', 'fr') 
    second_back_translated_answer = translate_text(second_translated_answer, 'fr', 'ru') 

    #(ru->en->fr->ru)
    third_translated_question = first_translated_question
    third_retranslated_question = translate_text(third_translated_question, 'en', 'fr')
    third_back_translated_question = translate_text(third_retranslated_question, 'fr', 'ru') 

    third_translated_answer = first_translated_answer
    third_retranslated_answer = translate_text(third_translated_answer, 'en', 'fr')
    third_back_translated_answer = translate_text(third_retranslated_answer, 'fr', 'ru') 

    translated_data.append({ 
            'question': original_question, 
            'answer': original_answer 
        }) 
    
    if first_back_translated_question and first_back_translated_answer:
        translated_data.append({ 
            'question': first_back_translated_question, 
            'answer': first_back_translated_answer 
        }) 
    if second_back_translated_question and second_back_translated_answer:
        translated_data.append({ 
            'question': second_back_translated_question, 
            'answer': second_back_translated_answer 
        }) 
    if third_back_translated_question and third_back_translated_answer:
        translated_data.append({ 
            'question': third_back_translated_question, 
            'answer': third_back_translated_answer 
        }) 

    with open('augmented_data.json', 'w', encoding='utf-8') as f: 
        json.dump(translated_data, f, ensure_ascii=False, indent=4)

    

print("Augmentation completed.")
