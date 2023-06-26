from django.shortcuts import render,redirect,HttpResponse
from accounts.models import User
from django.utils import timezone
from .models import Voice
from django.http import JsonResponse
import os
import re
import sys
from google.cloud import speech
import pyaudio
from six.moves import queue
from call import models

## stt 비동기 처리##
import asyncio
from google.cloud import speech_v1 as speech

def test(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        counselor_username = request.POST.get('counselor')
        
        if action == 'start':
            # 전화 시작 시간을 저장
            request.session['start_time'] = timezone.now()
        elif action == 'stop':
            # 전화 종료 시간을 저장
            start_time = request.session.pop('start_time', None)
            
            if start_time:
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds() / 60
                
                # 시작 시간과 종료 시간을 DB에 저장
                call = Voice(caller=username, receiver=counselor_username, start_time=start_time, end_time=end_time, duration=duration)
                call.save()

    return render(request, 'voice_test.html', context)


def test1(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    return render(request, 'voice_test.html', context)

def counselor(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    # return render(request, 'voice_counselor.html', context)
    return render(request, 'counselor.html', context)
def client(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    return render(request, 'voice_client.html', context)

def voice_en(request):
    return render(request, 'voice_en.html')

def voice_ja(request):
    return render(request, 'voice_ja.html')

def voice_ch(request):
    return render(request, 'voice_ch.html')

def voice_vi(request):
    return render(request, 'voice_vi.html')

def voice_th(request):
    return render(request, 'voice_th.html')

def account(request):
    return render(request, 'account.html')

def summary(request):
    return render(request, 'summary.html')

def history(request):
    return render(request, 'history.html')


###################################stt 테스트용 #################################

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

def stttest(request):
    username = None
    counselor_list = User.objects.filter(member_type='Counselor')
    if request.user.is_authenticated:  # 사용자가 인증된 경우에만 사용자 이름 가져오기
        username = request.user.username
    #     counselor_list = User.objects.all()
    
    context = {
        'username': username,
        'counselor_list': counselor_list
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        counselor_username = request.POST.get('counselor')
        
        if action == 'start':
            # 전화 시작 시간을 저장
            request.session['start_time'] = timezone.now()
            result = main()
            context["transcriptText"]=result
        elif action == 'stop':
            # 전화 종료 시간을 저장
            start_time = request.session.pop('start_time', None)
            
            if start_time:
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds() / 60
                
                # 시작 시간과 종료 시간을 DB에 저장
                call = Voice(caller=username, receiver=counselor_username, start_time=start_time, end_time=end_time, duration=duration)
                call.save()

    return render(request, 'stttest.html', context)

class MicrophoneStream(object):

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,

            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,

            stream_callback=self._fill_buffer,
        )

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True

        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:

            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0
            

def main():
    language_code = "ko-KR" 

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        profanity_filter = True
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses)

# if __name__ == "__main__":
#     main()
    
    
###################################api 호출 테스트 ###################################

# def apitest(request):
#     call = models.Call.objects.all()
    
#     # STT
#     client = speech.SpeechClient()
    
#     file_url = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
    
#     audio = speech.RecognitionAudio(uri=file_url)
    
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=16000,
#         language_code="en_US",
#     )
    
#     response = client.recognize(config=config, audio=audio)
#     transcript = ""
#     for result in response.results:
#         transcript += result.alternatives[0].transcript + "\n"
    
#     return render(request, 'apitest.html', {'call': call, 'transcript': transcript})



# def apitest(request):
#     call = models.Call.objects.all()
#     language_code = "en-US"

#     client = speech.SpeechClient()

#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=RATE,
#         language_code=language_code,
#         profanity_filter=True,
#     )

#     streaming_config = speech.StreamingRecognitionConfig(
#         config=config,
#         interim_results=True,
#     )

#     transcript = ""

#     with MicrophoneStream(RATE, CHUNK) as stream:
#         audio_generator = stream.generator()
#         requests = (
#             speech.StreamingRecognizeRequest(audio_content=content)
#             for content in audio_generator
#         )

#         responses = client.streaming_recognize(streaming_config, requests)

#         transcript = listen_print_loop(responses)

#     return render(request, 'apitest.html', {'call': call, 'transcript': transcript})


# def transcribe_audio(content, language_code):
#     client = speech.SpeechClient()

#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=RATE,
#         language_code=language_code,
#         profanity_filter=True,
#     )

#     streaming_config = speech.StreamingRecognitionConfig(
#         config=config,
#         interim_results=True,
#     )

#     transcript = ""

#     audio_generator = content.generator()
#     requests = [
#         speech.StreamingRecognizeRequest(audio_content=audio_content)
#         for audio_content in audio_generator
#     ]

#     responses = client.streaming_recognize(streaming_config, requests)

#     for response in responses:
#         if response.results:
#             for result in response.results:
#                 if result.is_final:
#                     transcript += result.alternatives[0].transcript

#     return transcript


def apitest(request):
    calls = models.Call.objects.all()
    language_code = "en-US"
    transcripts = {}

    for call in calls:
        transcript = ""
        with MicrophoneStream(RATE, CHUNK) as stream:
            transcript = transcribe_audio(stream, language_code)
        transcripts[call] = transcript

    return render(request, 'apitest.html', {'call': calls, 'transcript': transcripts})



######################### 상담 내용 요약 #########################

# Bard API 키 설정

from django.db.models import Max
from call.models import Call
from bardapi import Bard

os.environ["_BARD_API_KEY"] = "sidts-CjEBLFra0tGGxmom7Gw7eOu9FnHKBjErUcnrPpEc3DX3ThN_q8Ld94nhCGlF19Dh7oF7EAA" # 쿠키에서 받아오는 거

def summary():
    # 가장 최근에 등록된 Call 객체 가져오기
    latest_call = Call.objects.latest('id')

    # Consult text 가져오기
    consult_text = latest_call.consult_text

    # Bard API를 사용하여 요약 처리
    bard = Bard()
    response = bard.get_answer(consult_text)
    summary = response["choices"][0]["content"][0]  # 요약된 내용

    # 요약된 내용을 Call 객체의 summary 필드에 저장
    latest_call.summary = summary
    latest_call.save()

# JSON 형식으로 응답
    response_data = {
        'status': 'success',
        'message': 'Summary saved successfully',
    }
    return JsonResponse(response_data)





# # open ai 활용 시

# import mysql.connector
# import openai

# # 데이터베이스 연결 설정
# db_config = {
#     'host': 'localhost',
#     'user': 'username',
#     'password': 'password',
#     'database': 'database_name',
# }

# # Bard API 인증 설정
# openai.api_key = 'your_bard_api_key'

# # 데이터베이스 연결 생성
# connection = mysql.connector.connect(**db_config)
# cursor = connection.cursor()

# # 데이터베이스에서 데이터 가져오고 요약 처리 후 저장하는 함수
# def summarize_data():
#     # 데이터베이스 쿼리 실행
#     query = 'SELECT contacts FROM chat'
#     cursor.execute(query)
#     results = cursor.fetchall()

#     for result in results:
#         contact = result[0]
#         prompt = f'Summarize: {contact}'

#         # Bard API 호출
#         response = openai.Completion.create(
#             engine='davinci',
#             prompt=prompt,
#             max_tokens=100,
#             temperature=0.5
#         )

#         summary = response.choices[0].text.strip()

#         # 요약된 내용을 데이터베이스에 저장
#         update_query = 'UPDATE chat SET summary = %s WHERE contacts = %s'
#         cursor.execute(update_query, (summary, contact))

#     connection.commit()

# # summarize_data 함수 실행
# summarize_data()

# # 데이터베이스 연결 종료
# cursor.close()
# connection.close()

# bard api 활용 시
# import mysql.connector
# import os        # 위에 있어서 빼도 됨.
# from bardapi import Bard

# # MySQL 연결 설정
# mysql_config = {
#     'host': 'localhost',
#     'database': 'your_database',
#     'user': 'your_username',
#     'password': 'your_password'
# }


import bardapi
import os
from twilio.rest import Client
def sum(request):
    return render(request, 'sum.html')

def Bardd(prompt):
    os.environ["_BARD_API_KEY"] = "XQgOVGsSD7eGDvKozvshtguxw_ocrPgdqwOopYUDYMfX9B1FlsXc2bJ27Ip945izhZoYAA."
    input_text = prompt + " \n이 대화내용을 5줄로 요약해서 한국어로 답변해줘.\n마지막 줄에는 반드시 대화의 결과가 나타나야해. \n반드시 요약내용만 보여줘!"
    response = bardapi.core.Bard().get_answer(input_text)
    # twilio(response["choices"][0]["content"][0])
    return response["choices"][0]["content"][0]
    
def summ(request):
    prompt = request.POST.get('question')
    result = Bardd(prompt)

    context = {
        'question': prompt,
        'result': result
    }

    return render(request, 'result.html', context) 


def twilio(prompt):
    account_sid = "ACa0a888268f1ccccc271e417826c74886"
    auth_token = "18d1c29db7eec5b093ee24bd6069e2f7"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body="AI가 요약한 상담 내용입니다." + prompt,
    from_="+13613154870",
    to="+821020631392"
    )