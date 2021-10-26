# -*- coding: utf-8 -*-
import random, math
# from csaudio import play, read_wav, write_wav
from IPython.display import Audio
from scipy.io import wavfile
from functools import reduce

# If you get complaints about "big endian", (un)comment the following two lines
# import wave
# wave.big_endian = 0

################################################################################
# Helper functions
# 
# These functions help modify a list of values. We'll use them to modify sounds,
# which are also lists of values
################################################################################

def scale(L, scale_factor):
    '''Given a list L, scales each element of the list by scale_factor'''

    return [scale_factor * n for n in L]


def add(lists):
    '''
    Given a list of lists, adds their respective elements. If the two 
    lists have different lengths, the function truncates the result so that 
    it is as long as the shortest list.
    '''
    
    return map(sum, zip(lists)) # lots of higher-order functions here!


def addAndScale(lists, scaleFactors):
    '''
    Given a list of lists and a list of scale factors, scales each list by 
    its respective scale factor, then sums the results, element-wise. If the 
    lists have different lengths, the function  truncates the result so that 
    it is as long as the shortest list.
    '''
    
    scaledLists = [scale(l, f) for (l, f) in zip(lists, scaleFactors)]
    return add(scaledLists)


def randomize(x, chanceOfReplacing):
    ''' 
    randomize takes in an original value, x
    and a fraction named chanceOfReplacing.

    With the "chanceOfReplacing" chance, it
    should return a random float from -32767 to 32767.

    Otherwise, it should return x (not replacing it).
    '''

    r = random.uniform(0,1)
    if r < chanceOfReplacing:
        return random.uniform(-32768,32767)
    else:
        return x
    

def replaceSome(L, chanceOfReplacing):
    '''
    Given a list L, returns a new list L' where each element in L has a 
    chanceOfReplacing chance of being replaced with a random, 
    floating-point value in the range -32767 to 32767.
    '''

    return [randomize(e, chanceOfReplacing) for e in L]

################################################################################
# Sound file functions
# 
# Functions that manipulate sound files
################################################################################

# one way to add fluency is to give a better / more consistent name to 
# an existing library function...
# from csaudio import readwav as loadSound
# from csaudio import play as playFile 

def loadSound(filename):
    ''''
    Given a filename, loads the sound data from the file. Returns a tuple of
    (rate, sound-data)
    '''
    return wavfile.read('swnotry.wav')


def saveSound(data, outputFilename='out.wav' ):
    '''
    Given a sound and the name of an output file, 
    the function will write the sound data to the output file.
    '''

    Audio(list(data), outputFilename)


# def playSound(data, outputFilename='out.wav' ):
#     '''
#     Given a sound and the name of an output file, 
#     the function will write the sound data to the output file and play the sound.
#     '''

#     #write_wav(data, outputFilename)
#     saveSound(data, outputFilename)
#     play(outputFilename)


# def modifyAndPlay(filename, modifier, outputFilename='out.wav'):
#     '''
#     Given a sound filename, a function that modifies the sound, and the name
#     of an output file, the funciton will load the sound from the file, 
#     modify it, write the sound, to the output file, and play it.

#     NOTE: This function captures the boilerplate code from most of the original
#     functions.
#     '''

#     print("Playing the original sound...")
#     play(filename)
    
#     print("Reading in the sound data...")
#     sound = readwav(filename)

#     print("Computing new sound...")
#     newSound = modifier(sound)
#     saveSound(newSound, outputFilename)

#     print("\nPlaying new sound...")
#     play(outputFilename) 


################################################################################
# Sound functions
# 
# A "sound" is a (sample, sampling rate) tuple
################################################################################

def overlay(sounds):
    '''given a list of sounds, overlay them into a single sound'''
    
    # IMPORTANT!
    # we want each sound to make a 1 / N contribution to the final sound, 
    # where N is the number of sounds
    scaleBack = 1.0 / len(sounds) 
    
    # separate the samples from the rates
    samples, rates = zip(sounds)
    
    # scale and sum the sounds
    scaleFactors = [scaleBack] * len(samples)
    newSound = addAndScale(samples, scaleFactors)
    
    # use the first stream's sample rate as the sample rate for the new sounds
    newRate = rates[0]

    return (newSound, newRate)


def changeSpeed(data, newRate ):
    '''change a sound's speed'''

    samples, rate = data
    return (samples, newRate)


def flipflop(data ):
    '''swap the halves of a sound'''

    samples, rate = data

    # compute the midpoint and exchange those parts of the list
    # the sample rate doesn't change
    mid = len(samples)/2
    newSamples = samples[mid:] + samples[:mid]

    return (newSamples, rate)


def reverse(data ):
    '''reverses a sound'''

    samples, rate = data
    return (samples[::-1], rate)


def volume(data, scaleFactor ):
    '''changes the volume of a soudn by a given factor'''

    samples, rate = data
    newSamples = scale(samples, scaleFactor)
    return (newSamples, rate)


def static(data, probabilityOfStatic):
    '''replaces each sample with static, according to the given probability'''

    samples, rate = data
    newSamples = replaceSome(samples, probabilityOfStatic)
    return (newSamples, rate)


def echo(data, timeDelay ):
    '''adds an echo effect to a sound'''
    
    samples, rate = data
    numSilentSamples = int(rate * timeDelay)   # how long is the silence?
    silentSamples = [0] * numSilentSamples     # make the silence
    paddedSamples = silentSamples + samples    # pad the sound with silence

    # prepare to overlay
    sound = (samples, rate)    
    echoedSound = (paddedSamples, rate)
    
    return overlay([sound, echoedSound])


def pureTone(freq, timeInSeconds):
    '''creates a pure tone of frequency freq for timeInSeconds seconds'''

    # a pure tone is the y-values of a cosine wave whose frequency is 
    # freq  Hertz. We'll generate one sample every 1/44100 of a second;
    # thus, the sampling rate is 44100 Hertz.
    rate = 44100
    numSamples = int(timeInSeconds * rate) 
    f = 2*math.pi/rate  # converts from samples to Hz
    a = 32767.0         # amplitude-scaling coefficient
    samples = [ a * math.sin(f*i*freq) for i in range(numSamples) ]

    return (samples, rate)


################################################################################
# Bonus: melodies!
################################################################################

# a dictionary that maps note names to frequencies
# http://en.wikipedia.org/wiki/Piano_key_frequencies
FREQUENCIES = {'A'  : 440.000,
               'A#' : 466.164,
               'B'  : 493.883,
               'C'  : 523.251,
               'C#' : 554.365,
               'D'  : 587.330,
               'D#' : 622.254,
               'E'  : 659.255,
               'F'  : 698.456,
               'F#' : 739.989,
               'G'  : 783.991,
               'G#' : 783.991 }
FREQUENCIES['A♭'] = FREQUENCIES['G#']
FREQUENCIES['B♭'] = FREQUENCIES['A#']
FREQUENCIES['D♭'] = FREQUENCIES['C#']
FREQUENCIES['E♭'] = FREQUENCIES['D#']
FREQUENCIES['G♭'] = FREQUENCIES['F#']


def makeMelody(notes, duration = .5):
    '''
    Given a list of notes, and a duration for each note, 
    returns a melody of those notes
       
    Each note is represented as a string (see the body of this function).
    '''

    # generate the tones
    tones = [pureTone(FREQUENCIES[note], duration) for note in notes]

    # separate the samples from the rates
    samples, rates = zip(*tones)
    
    # flatten the list of samples into a single list
    melody = reduce(list.__add__, samples)
    
    # use the rate of the first sample as the rate of the melody
    rate = rates[0]
    
    return (melody, rate)


def twinkle():
    '''Plays a simple version of "Twinkle, twinkle little star"'''
    
    part1 = [ 'A',  'A',  'E',  'E',  'F#', 'F#', 'E',
              'D',  'D',  'C#', 'C#', 'B',  'B',  'A'  ] 
  
    part2 = [ 'E',  'E',  'D',  'D',  'C#', 'C#', 'B'  ]
    
    song = part1 + part2 + part2 + part1
    
    # playSound(makeMelody(song))
    return makeMelody(song)
