import os
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
import praatScript2
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
from tensorflow import keras
from keras.preprocessing.text import Tokenizer
SEQUENCE_LENGTH = 300
import time

model = keras.models.load_model('/content/sentAnalys.h5')
tokenizer = Tokenizer()
POSITIVE = "POSITIVE"
NEGATIVE = "NEGATIVE"
NEUTRAL = "NEUTRAL"
SENTIMENT_THRESHOLDS = (0.4, 0.7)
def pad_sequences(sequences, maxlen=None, dtype='int32',
                  padding='pre', truncating='pre', value=0.):

  if not hasattr(sequences, '__len__'):
    raise ValueError('`sequences` must be iterable.')
  num_samples = len(sequences)

  lengths = []
  sample_shape = ()
  flag = True

  # take the sample shape from the first non empty sequence
  # checking for consistency in the main loop below.

  for x in sequences:
    try:
      lengths.append(len(x))
      if flag and len(x):
        sample_shape = np.asarray(x).shape[1:]
        flag = False
    except TypeError as e:
      raise ValueError('`sequences` must be a list of iterables. '
                       f'Found non-iterable: {str(x)}') from e

  if maxlen is None:
    maxlen = np.max(lengths)

  is_dtype_str = np.issubdtype(dtype, np.str_) or np.issubdtype(
      dtype, np.unicode_)
  if isinstance(value, str) and dtype != object and not is_dtype_str:
    raise ValueError(
        f'`dtype` {dtype} is not compatible with `value`\'s type: '
        f'{type(value)}\nYou should set `dtype=object` for variable length '
        'strings.')

  x = np.full((num_samples, maxlen) + sample_shape, value, dtype=dtype)
  for idx, s in enumerate(sequences):
    if not len(s):  # pylint: disable=g-explicit-length-test
      continue  # empty list/array was found
    if truncating == 'pre':
      trunc = s[-maxlen:]  # pylint: disable=invalid-unary-operand-type
    elif truncating == 'post':
      trunc = s[:maxlen]
    else:
      raise ValueError(f'Truncating type "{truncating}" not understood')

    # check `trunc` has expected shape
    trunc = np.asarray(trunc, dtype=dtype)
    if trunc.shape[1:] != sample_shape:
      raise ValueError(f'Shape of sample {trunc.shape[1:]} of sequence at '
                       f'position {idx} is different from expected shape '
                       f'{sample_shape}')

    if padding == 'post':
      x[idx, :len(trunc)] = trunc
    elif padding == 'pre':
      x[idx, -len(trunc):] = trunc
    else:
      raise ValueError(f'Padding type "{padding}" not understood')
  return x



def decode_sentiment(score, include_neutral=True):
    if include_neutral:
        label = NEUTRAL
        if score <= SENTIMENT_THRESHOLDS[0]:
            label = NEGATIVE
        elif score >= SENTIMENT_THRESHOLDS[1]:
            label = POSITIVE

        return label
    else:
        return NEGATIVE if score < 0.5 else POSITIVE

def predict(text, include_neutral=True):
    start_at = time.time()
    # Tokenize text
    x_test = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=SEQUENCE_LENGTH)
    # Predict
    score = model.predict([x_test])[0]
    # Decode sentiment
    label = decode_sentiment(score, include_neutral=include_neutral)

    return {"label": label, "score": float(score),
       "elapsed_time": time.time()-start_at}

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

        emo = predict(textToTranslate)[1]
        praatScriptText = praatScript2.generatePraatScriptText(SessionFolderPath.__str__(), audioName16k,
                                                              synthedFileName, adjusted_audioFileName, emo)
        praatScript2.createPraatFile(praatScriptText, praatScriptPath)


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