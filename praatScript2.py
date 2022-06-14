import subprocess
import pathlib

def generatePraatScriptText(path, origFileName, synthFileName, exportName, emo):
    origFileNameArr = origFileName.split('.')
    synthFileNameArr = synthFileName.split('.')

    scTextHapy = f'Read from file: "{path}\\{synthFileNameArr[0]}.{synthFileNameArr[1]}"\n' \
                  f'To Manipulation: 0.01, 75, 600\n' \
                  f'Read from file: "D:\\Proj\\Python\\MasterApp\\TTS\\refs\\happyref1.PitchTier"\n' \
                  f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
                  f'plusObject: "PitchTier happyref1"\n' \
                  f'Replace pitch tier\n' \
                  f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
             f'Get resynthesis (overlap-add)\n' \
                 f'Read from file: "D:\\Proj\\Python\\MasterApp\\TTS\\refs\\happyref1.IntensityTier"\n' \
                 f'selectObject: "IntensityTier happyref1"\n' \
                 f'plusObject: "Sound {synthFileNameArr[0]}"\n' \
                 f'selectObject: "Sound {synthFileNameArr[0]}"\n' \
             f'Save as WAV file: "{path}\\{exportName}"\n'

    scTextAngry = f'Read from file: "{path}\\{synthFileNameArr[0]}.{synthFileNameArr[1]}"\n' \
                  f'To Manipulation: 0.01, 75, 600\n' \
                  f'Read from file: "D:\\Proj\\Python\\MasterApp\\TTS\\refs\\angryref1.PitchTier"\n' \
                  f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
                  f'plusObject: "PitchTier angryref1"\n' \
                  f'Replace pitch tier\n' \
                  f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
             f'Get resynthesis (overlap-add)\n' \
             f'Save as WAV file: "{path}\\{exportName}"\n'
    if(emo=='POSITIVE' or emo=='NEUTRAL'):
        return scTextHapy
    else:
        return scTextAngry




def createPraatFile(scTextArg, scriptFileName):
    linesArr = scTextArg.split("\n")
    for i in range(0, len(linesArr) - 1):
        writeToFile = f'echo {linesArr[i]}>> {scriptFileName}'
        res = subprocess.call(writeToFile, shell=True)
        if res == 1:
            raise ValueError('A very specific bad thing happened.')

#res = subprocess.call(f'praat --run "{scriptFileName}"', shell=True)  # 1 - error, 0 - ok
#if res == 1:
#    raise ValueError('A very specific bad thing happened.')


