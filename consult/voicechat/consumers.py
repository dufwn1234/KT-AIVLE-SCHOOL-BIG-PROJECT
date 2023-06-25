import json
from datetime import datetime
from accounts.models import User
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, Chat, Contact
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


class VoiceChatConsumer(WebsocketConsumer):
    
    def fetch_messages(self, data):
        chat_id = int(self.room_name)
        messages = Chat.last_10_messages()
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        user = data['user']
        chat_id = int(self.room_name)
        user_instance = User.objects.filter(username=user).first()
        chat_contact = Contact.objects.filter(id=chat_id).first()
        message_content = data['message']
        room_name_contant = User.objects.get(id=chat_id)

        predict_class, predicted_probability = classify_text(message_content)

        if predict_class == 0:
            message_content = "폭언입니다 test"

        # 새로운 Message 인스턴스 생성
        message = Message.objects.create(
            user=user_instance,
            chat=chat_contact,
            content=message_content,
            room_name=room_name_contant
        )
        message_instance = message

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        self.send_chat_message(content, message_instance, chat_id)
    
    
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'user':message.user.username,
            'content':message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message, message_instance, chat_id):
        # save_customer_info(chat_id, message_instance.user)
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

