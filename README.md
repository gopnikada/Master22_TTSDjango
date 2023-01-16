# Voice-over speech TTS!

Demo repo from Master Thesis got at Summer '22.
 Paper: (UA) ![https://github.com/gopnikada/Master22_TTSDjango/blob/master/paper.pdf]  


# Overview

The basic app overview:    
![This is an image](https://github.com/gopnikada/tts_django2/blob/master/schemeEng.png?raw=true)
# TTS model

The Ukrainian  TTS model was built using  [Coqui-TTS Framework](https://github.com/coqui-ai/TTS) and  [VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech)](https://github.com/jaywalnut310/vits)




### Datasets used for training: 
[Ukrainian Open Speech To Text Dataset 4.2 part 2 | Kaggle](https://www.kaggle.com/datasets/aikhmelnytskyy/ukrainian-open-speech-to-text-dataset-42-part-2/code)
[caito](https://www.caito.de/data/Training/stt_tts/uk_UK.tgz)
[Common Voice (mozilla.org)](https://commonvoice.mozilla.org/uk/datasets)
[VoxForge Repository (voxforge1.org)](http://www.repository.voxforge1.org/downloads/uk/Trunk/)

### Losses
![Learning ](https://github.com/gopnikada/tts_django2/blob/master/learning.png?raw=true)



### Adjusting emotion params

The paper [Jianhua Tao, Member, IEEE, Yongguo Kang, and Aijun Li. TRANSACTIONS ON AUDIO, SPEECH, AND LANGUAGE PROCESSING, VOL. 14, NO. 4, JULY 2006] was borrowed in order to adjust the neutral generated speech to emotional.

Corresponding emotional speech params from the study:
![Learning ](https://github.com/gopnikada/tts_django2/blob/master/params.png?raw=true)

Achieved could be this results by using [Praat](https://www.fon.hum.uva.nl/praat/)

### Another used models
[coqui-ai/STT](https://github.com/coqui-ai/STT) for extracting text from english audio

[Twitter Sentiment Analysis](https://www.kaggle.com/code/paoloripamonti/twitter-sentiment-analysis) for getting emotional tags
