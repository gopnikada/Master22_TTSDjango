#from moviepy.editor import *
from os import walk
import uuid
import os

# filesInDir = next(walk("C:\\Users\\49157\\Pictures\Camera Roll"), (None, None, []))[2]
# len = len(filesInDir)
# someFile = filesInDir[5]

#audioclip = AudioFileClip("C:\\Users\\49157\\Pictures\Camera Roll\\vid1.mp4")
#audioclip.write_audiofile("C:\\Users\\49157\\Pictures\Camera Roll\\audio.wav", fps=None, nbytes=2, buffersize=2000,
                       # codec=None, bitrate=None, ffmpeg_params=None,
                       # write_logfile=False, verbose=True, logger='bar')

#sessionId = str(uuid.uuid1())
#os.mkdir("C:\Kirill\Prog\FilesuploadProject\StoredFiles\\" + sessionId)
#import librosa as librosa
#
# from deep_translator import *
# translated = GoogleTranslator(source='auto', target='uk').translate("keep it up, you are awesome")  # output -> Weiter so, du bist großartig
# print(translated)
#
# import pathlib
# Rootpath = pathlib.Path().resolve()
# path = pathlib.Path().resolve().joinpath('models')
# sttModelPath = Rootpath.joinpath('models').joinpath('STT').joinpath('model.tflite')
# print(sttModelPath)



def generatePraatScriptText(path, origFileName, synthFileName, exportName):
    origFileNameArr = origFileName.split('.')
    synthFileNameArr = synthFileName.split('.')
    exportName = "pitchClonedNeutral"
    print(path)

    scText = f'Read from file: "{path}\\{origFileNameArr[0]}.{origFileNameArr[1]}"\n' \
             f'Read from file: "{path}\\{synthFileNameArr[0]}.{synthFileNameArr[1]}"\n' \
             f'selectObject: "Sound {origFileNameArr[0]}"\n' \
             f'To Intensity: 100, 0, "yes"\n' \
             f'Down to IntensityTier\n' \
             f'selectObject: "Sound {synthFileNameArr[0]}"\n' \
             f'plusObject: "IntensityTier {origFileNameArr[0]}"\n' \
             f'Multiply: "yes"\n' \
             f'To Manipulation: 0.01, 75, 600\n' \
             f'selectObject: "Sound {origFileNameArr[0]}"\n' \
             f'To Manipulation: 0.01, 75, 600\n' \
             f'Extract pitch tier\n' \
             f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n' \
             f'plusObject: "PitchTier {origFileNameArr[0]}"\n' \
             f'Replace pitch tier\n' \
             f'selectObject: "Manipulation {origFileNameArr[0]}"\n' \
             f'Extract duration tier\n' \
             f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n' \
             f'plusObject: "DurationTier {origFileNameArr[0]}"\n' \
             f'Replace duration tier\n' \
             f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n' \
             f'Get resynthesis (overlap-add)\n' \
             f'Save as WAV file: "{path}\\{exportName}.wav"\n'
scriptFileName = "copyPitch.praat"



