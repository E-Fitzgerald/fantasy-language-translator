from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator
from progressbar import ProgressBar
import pickle
import random

EspeakWrapper.set_library('C:/Program Files/eSpeak NG/libespeak-ng.dll')

def generate_phonemes(sentence, printout=False, lang="en-us"):
        cleanSent = ''.join(char for char in sentence if char.isalnum() or char.isspace())
        words = cleanSent.split()

        res = []
        pbar = ProgressBar().start()
        jobs = len(words)
        for word in words:
            phonemizedWord = phonemize(word, language=lang, separator=Separator(phone="|", word='', syllable='||'))
            res.append(phonemizedWord)
            if printout:
                print(phonemizedWord)
                chars = phonemizedWord.split("|")
                print(chars)
            pbar.update(int((len(res)/jobs)*100))

        return res

    
def generate_english_phonemes(sentence, printout=False, regen=False, name=None):
    if regen:
        phonemes = generate_phonemes(sentence, False, lang="en-us")
        pickle.dump(phonemes, open("main/cacher/data/" + name + ".p", "wb"))
    else:
        print("Loading from cache...")
        phonemes = pickle.load(open("main/cacher/data/" + name + ".p", "rb"))
    wordSet = set(phonemes)
    if printout:
        print("English phonemes set:")
        print(wordSet)

    res = []
    for w in wordSet:
        res += w.split("|")
    
    return set(res) - set([''])

def remix_phonemes(phonemes1):
    phoneme_list = list(phonemes1)
    random.shuffle(phoneme_list)
    return phoneme_list

def generate_mapping(phonemes1, phonemes2):
    mapping = {}
    for i in range(len(phonemes1)):
        mapping[phonemes1[i]] = phonemes2[i]
    return mapping

def transcribe(sentence, mapping):
    cleanSent = ''.join(char for char in sentence if char.isalnum() or char.isspace())
    words = cleanSent.split()

    res = []
    for word in words:
        phonemizedWord = phonemize(word, language="en-us", separator=Separator(phone="|", word='', syllable='||'))
        chars = phonemizedWord.split("|")
        for i in range(len(chars)):
            if chars[i] in mapping:
                chars[i] = mapping[chars[i]]
        res.append("".join(chars))

    return " ".join(res)