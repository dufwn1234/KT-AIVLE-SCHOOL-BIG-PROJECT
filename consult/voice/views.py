from django.shortcuts import render,redirect,HttpResponse
from accounts.models import User
from django.utils import timezone
from .models import Voice

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
            a=transcript + overwrite_chars
            return a

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


def transcribe_audio(content, language_code):
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        profanity_filter=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    transcript = ""

    audio_generator = content.generator()
    requests = [
        speech.StreamingRecognizeRequest(audio_content=audio_content)
        for audio_content in audio_generator
    ]

    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        if response.results:
            for result in response.results:
                if result.is_final:
                    transcript += result.alternatives[0].transcript

    return transcript


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