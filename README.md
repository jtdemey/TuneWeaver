# TuneWeaver
## John DeMey SMP2017-2018
## Advisor: Simon Read
An LSTM-based recurrent neural network that can learn to produce accompaniments for melodies in MIDI format.  TuneWeaver can use a pre-trained model out of the box or it can train itself on any set of MIDI-formatted songs.

# Usage
#### [] = required, {} = optional
### 1) Preparing data
```
python prepweaver.py [directory of MIDI training set] {split-only / serialize-only / both}
```
### 2) Training the model
```
python trainweaver.py {amount of epochs} {.hdf5 model checkpoint}
```
### 3) Producing a new accompaniment
```
python runweaver.py
```
If you want to use the pre-trained model, only the third step is required.

# Dependencies
* Python version <=2.7
* Tkinter
* numpy
* TensorFlow
* Keras
* python-midi
