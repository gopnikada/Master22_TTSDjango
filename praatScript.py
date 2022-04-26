import subprocess
import pathlib

path = pathlib.Path().resolve()

origFileName = 'neutral.ogg'
origFileNameArr = origFileName.split('.')

synthFileName = 'neutralS.wav'
synthFileNameArr = synthFileName.split('.')

exportName = "pitchClonedNeutral"

scriptText = f'Read from file: "{path}\\{origFileNameArr[0]}.{origFileNameArr[1]}"\n' \
             'To Manipulation: 0.01, 75, 600\n' \
             f'selectObject: "Manipulation {origFileNameArr[0]}"\n' \
             'Extract pitch tier\n' \
             f'selectObject: "PitchTier {origFileNameArr[0]}"\n' \
             f'Read from file: "{path}\\{synthFileNameArr[0]}.{synthFileNameArr[1]}"\n' \
             f'selectObject: "Sound {synthFileNameArr[0]}"\n' \
             'To Manipulation: 0.01, 75, 600\n' \
             f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
             f'selectObject: "PitchTier {origFileNameArr[0]}"\n' \
             f'plusObject: "Manipulation {synthFileNameArr[0]}"\n' \
             'Replace pitch tier\n' \
             f'selectObject: "Manipulation {synthFileNameArr[0]}"\n' \
             'Get resynthesis (overlap-add)\n' \
             f'Save as WAV file: "{path}\\{exportName}.wav"\n'

scText = f'Read from file: "{path}\\{origFileNameArr[0]}.{origFileNameArr[1]}"\n'\
        f'Read from file: "{path}\\{synthFileNameArr[0]}.{synthFileNameArr[1]}"\n'\
        f'selectObject: "Sound {origFileNameArr[0]}"\n'\
        f'To Intensity: 100, 0, "yes"\n'\
        f'Down to IntensityTier\n'\
        f'selectObject: "Sound {synthFileNameArr[0]}"\n'\
        f'plusObject: "IntensityTier {origFileNameArr[0]}"\n'\
        f'Multiply: "yes"\n'\
        f'To Manipulation: 0.01, 75, 600\n'\
        f'selectObject: "Sound {origFileNameArr[0]}"\n'\
        f'To Manipulation: 0.01, 75, 600\n'\
        f'Extract pitch tier\n'\
        f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n'\
        f'plusObject: "PitchTier {origFileNameArr[0]}"\n'\
        f'Replace pitch tier\n'\
        f'selectObject: "Manipulation {origFileNameArr[0]}"\n'\
        f'Extract duration tier\n'\
        f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n'\
        f'plusObject: "DurationTier {origFileNameArr[0]}"\n'\
        f'Replace duration tier\n'\
        f'selectObject: "Manipulation {synthFileNameArr[0]}_int"\n'\
        f'Get resynthesis (overlap-add)\n'\
        f'Save as WAV file: "{path}\\{exportName}.wav"\n'\

scriptFileName = "copyPitch.praat"

linesArr = scText.split("\n")
for i in range(0, len(linesArr) - 1):
    writeToFile = f'echo {linesArr[i]}>> {scriptFileName}'
    res = subprocess.call(writeToFile, shell=True)
    if res == 1:
        raise ValueError('A very specific bad thing happened.')

res = subprocess.call(f'praat --run "{scriptFileName}"', shell=True)  # 1 - error, 0 - ok
if res == 1:
    raise ValueError('A very specific bad thing happened.')


