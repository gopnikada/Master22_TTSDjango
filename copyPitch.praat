Read from file: "D:\Proj\Python\MasterApp\TTS\neutral.ogg"
Read from file: "D:\Proj\Python\MasterApp\TTS\neutralS.wav"
selectObject: "Sound neutral"
To Intensity: 100, 0, "yes"
Down to IntensityTier
selectObject: "Sound neutralS"
plusObject: "IntensityTier neutral"
Multiply: "yes"
To Manipulation: 0.01, 75, 600
selectObject: "Sound neutral"
To Manipulation: 0.01, 75, 600
Extract pitch tier
selectObject: "Manipulation neutralS_int"
plusObject: "PitchTier neutral"
Replace pitch tier
selectObject: "Manipulation neutral"
Extract duration tier
selectObject: "Manipulation neutralS_int"
plusObject: "DurationTier neutral"
Replace duration tier
selectObject: "Manipulation neutralS_int"
Get resynthesis (overlap-add)
Save as WAV file: "D:\Proj\Python\MasterApp\TTS\pitchClonedNeutral.wav"
