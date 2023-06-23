from django.shortcuts import render
from . import models
from google.cloud import speech

# Create your views here.
def call(request):
    return render(request, 'call.html')

def test(request):
    call = models.Call.objects.all()
    
    # STT
    client = speech.SpeechClient()
    
    file_url = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
    
    audio = speech.RecognitionAudio(uri=file_url)
    
    config = speech.RecognitionConfig(
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz = 16000,
        language_code = "en_US",
    )
    
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        print(result.alternatives[0].transcript)
    
    return render(request, 'calltest.html', {'call':call})

    