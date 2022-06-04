import os
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import praatScript
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
from wsgiref.util import FileWrapper
import pysrt

Rootpath = pathlib.Path().resolve()

saveFolder = Rootpath.joinpath('StoredFiles')
sttModelPath = Rootpath.joinpath('models').joinpath('STT').joinpath('model.tflite')

@ensure_csrf_cookie
def upload_file(request):
    if request.method == 'POST':
        # form = UploadFileForm(request.POST, request.FILES)
        #if form.is_valid():
        sessionId = str(uuid.uuid1())
        SessionFolderPath = saveFolder.joinpath(sessionId)
        os.mkdir(SessionFolderPath)
        FormFiles = request.FILES


        for fileName, value in FormFiles.items():
            fileToSaveName = value.name
            saveFilePath = SessionFolderPath.joinpath(fileToSaveName)
            handle_uploaded_file(saveFilePath, value)


        filesInDir = next(walk(SessionFolderPath), (None, None, []))[2]
        videoFileName = list(filter(lambda x: x.split('.')[1] != 'srt', filesInDir))[0]
        subsFileName = list(filter(lambda x: x.split('.')[1] == 'srt', filesInDir))[0]
        subsFilePath = SessionFolderPath.joinpath(subsFileName)
        audioName = videoFileName.split('.')[0] + '.wav'
        audioName16k = videoFileName.split('.')[0]+"16k" + '.wav'

        audioPath = SessionFolderPath.joinpath(audioName)
        audioPath16k = SessionFolderPath.joinpath(audioName16k)

        videoPath = SessionFolderPath.joinpath(videoFileName).__str__()

        #todo clear
        #res = subprocess.run(["ls"], capture_output=True)


        audioclip = AudioFileClip(videoPath)
        audioclip.write_audiofile(audioPath, fps=None, nbytes=2,
                                  buffersize=2000,
                                  codec=None, bitrate=None, ffmpeg_params=None,
                                  write_logfile=False, verbose=True, logger='bar')


        y, sr = librosa.load(audioPath)
        data = librosa.resample(y, sr, 16000)
        sf.write(audioPath16k, data, 16000)



        ds = Model(sttModelPath.__str__())
        fin = wave.open(audioPath16k.__str__(), "rb")
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        textToTranslate = ''
        subs = pysrt.open(subsFilePath.__str__(), encoding='utf-8')

        if filesInDir.__len__() == 2:

            textToTranslate = subs.text.replace('\n', ' ')
            for sub in subs.data:
                print(sub)
        else:
            textToTranslate = ds.stt(audio)

        #todo match time

        translatedText = GoogleTranslator(source='auto', target='uk')\
            .translate(textToTranslate)



        synthedFileName = "synthed.wav"
        synthedSpeechPath = SessionFolderPath.joinpath(synthedFileName)

        ttsModelPath = Rootpath.joinpath('models').joinpath('TTS')\
            .joinpath('checkpoint_260000.pth.tar')
        ttsConfigPath = Rootpath.joinpath('models').joinpath('TTS')\
            .joinpath('config123.json')

        ttsCliCommand = f'tts --text "{translatedText}" ' \
                       f'--model_path {ttsModelPath.__str__()} ' \
                       f'--config_path {ttsConfigPath.__str__()} ' \
                       f'--out_path {synthedSpeechPath.__str__()}'


        synthResponse = subprocess.call(ttsCliCommand, shell=True)  # 1 - error, 0 - ok

        adjusted_audioFileName = "adjusted.wav"
        adjusted_audioPath = SessionFolderPath.joinpath(adjusted_audioFileName)

        praatScriptFileName = "praatScript.praat"
        praatScriptPath = SessionFolderPath.joinpath(praatScriptFileName)

        audioName16k = librosa.effects.trim(audioName16k, top_db=10)#remove silence
        synthedFileName = librosa.effects.trim(synthedFileName, top_db=10)
        praatScriptText = praatScript.generatePraatScriptText(SessionFolderPath.__str__(), audioName16k,
                                                              synthedFileName, adjusted_audioFileName)
        praatScript.createPraatFile(praatScriptText, praatScriptPath)


        adjustedSynthResponse = subprocess.call(f'{Rootpath.joinpath("Praat.exe")} '
                    f'--run "{praatScriptPath.__str__()}"', shell=True)  # 1 - error, 0 - ok

        # todo parse subs
        #todo praat per parts
        #todo show double subs
        #todo duration does not match
        #todo speechstart - speechstop
        #todo if subs synth at precise time pieces. else - use json from stt!
        #todo decompise refactor

        videoclip = VideoFileClip(videoPath)
        audioclip_adjusted = AudioFileClip(adjusted_audioPath.__str__())
        videoclip_changed_audio = videoclip.set_audio(audioclip_adjusted)

        videoclip_adjustedFileName = "adj" + videoFileName
        videoclip_adjustedFilePath = SessionFolderPath.\
            joinpath(videoclip_adjustedFileName).__str__()

        videoclip_changed_audio.write_videofile(videoclip_adjustedFilePath)



        subTitlesdata = ""

        # if subTitlesdata:
        #     textToSynth = subTitlesdata

        #tts.synth(textToSynth)

        file = FileWrapper(open(videoclip_adjustedFilePath, 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = f'attachment; filename={videoclip_adjustedFileName}'

        # context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
        #
        # render(request, "single.html", context)
        return response




        # context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
        #
        # return render(request, "single.html", context)
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