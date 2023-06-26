from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


model_dir = "C:/Users/dufwn/Desktop/results"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)

def Translation(text):
    model_dir = "results"
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
    input_text = text
    max_token_length = 64
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, max_length=max_token_length)
    koreans = model.generate(**inputs,max_length=max_token_length,num_beams=5,)
    result = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(koreans[0]))
    return result