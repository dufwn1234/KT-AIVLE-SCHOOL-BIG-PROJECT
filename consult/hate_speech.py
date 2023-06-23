# !pip install torch
# !pip install transformers

import torch
from transformers import BertForSequenceClassification, BertTokenizer

output_dir = "C:/Users/User/Desktop/Portfolio/KT_AIVLE_BigProject/consult/kcbert"

model = BertForSequenceClassification.from_pretrained(output_dir)
tokenizer = BertTokenizer.from_pretrained(output_dir)

def classify_text(text):
    encoded_input = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=128,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    with torch.no_grad():
        outputs = model(**encoded_input)
        logits = outputs.logits
    
    probabilities = torch.softmax(logits, dim=1)
    
    predicted_class = torch.argmax(probabilities, dim=1).item()
    predicted_probability = probabilities[0][predicted_class].item()
    
    return predicted_class, predicted_probability
