import os

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.views.decorators.csrf import ensure_csrf_cookie
from moviepy.editor import *
import uuid
from os import walk
import librosa
import soundfile as sf
import subprocess
from deep_translator import GoogleTranslator
import pathlib

from client import *

Rootpath = pathlib.Path().resolve()

saveFolder = Rootpath.joinpath('StoredFiles')
sttModelPath = Rootpath.joinpath('models').joinpath('STT').joinpath('model.tflite')

@ensure_csrf_cookie
def upload_file(request):
    if request.method == 'POST':
        # form = UploadFileForm(request.POST, request.FILES)
        #if form.is_valid():
        sessionId = str(uuid.uuid1())
        os.mkdir("D:\\Proj\\Python\\MasterApp\\TTS\\StoredFiles\\" + sessionId)
        FormFiles = request.FILES
        folderPath = saveFolder + '\\' + sessionId + '\\'

        for fileName, value in FormFiles.items():
            fileToSaveName = value.name
            saveFilePath = saveFolder + '/' + sessionId + '/' + fileToSaveName
            handle_uploaded_file(saveFilePath, value)

            #if not os.listdir(filePath) and '.'.split(filesInDir[0])[1] != 'srt':


        filesInDir = next(walk(folderPath), (None, None, []))[2]

        videoFileName = list(filter(lambda x: x.split('.')[1] != 'srt', filesInDir))[0]

        audioName = videoFileName.split('.')[0] + '.wav'
        audioName16k = videoFileName.split('.')[0]+"16k" + '.wav'

        audioPath = folderPath + audioName
        audioPath16k = folderPath + audioName16k

        videoPath = folderPath + videoFileName

        audioclip = AudioFileClip(videoPath)
        audioclip.write_audiofile(audioPath, fps=None, nbytes=2,
                                  buffersize=2000,
                                  codec=None, bitrate=None, ffmpeg_params=None,
                                  write_logfile=False, verbose=True, logger='bar')



        y, sr = librosa.load(audioPath)
        data = librosa.resample(y, sr, 16000)
        sf.write(audioPath16k, data, 16000)



        ds = Model(sttModelPath)
        fin = wave.open(audioPath16k, "rb")
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        #jsondata = metadata_json_output(ds.sttWithMetadata(audio))
        textToTranslate = ds.stt(audio)

        # if contains srt:
        #     textToSynth = textFromSrt todo


        translatedText = GoogleTranslator(source='auto', target='uk').translate(textToTranslate)

        synthedFileName = "synthed.wav"
        synthedSpeechPath = folderPath + synthedFileName
        ttsModelPath = "D:\\Proj\\Python\\MasterApp\\TTS\\models\\TTS\\checkpoint_260000.pth.tar"
        ttsConfigPath = "D:\\Proj\\Python\\MasterApp\\TTS\\models\\TTS\\config123.json"
        ttsCliCommand = f'tts --text "{translatedText}" ' \
                       f'--model_path {ttsModelPath} ' \
                       f'--config_path {ttsConfigPath} ' \
                       f'--out_path {synthedSpeechPath}'

        synthResponse = subprocess.call(ttsCliCommand, shell=True)  # 1 - error, 0 - ok

        #todo praat


        subTitlesdata = ""

        # if subTitlesdata: #todo
        #     textToSynth = subTitlesdata

        #tts.synth(textToSynth)

        context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}

        return render(request, "single.html", context)
    else:
        form = UploadFileForm()
    return render(request, 'single.html', {'form': form})



def handle_uploaded_file(path, f):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@ensure_csrf_cookie
def upload_multiple_files(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        # if form.is_valid():
        for f in files:
            handle_uploaded_file(f)
        context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
        return render(request, "multiple.html", context)
    else:
        form = UploadFileForm()
    return render(request, 'multiple.html', {'form': form})