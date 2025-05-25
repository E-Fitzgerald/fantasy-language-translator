from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator
from progressbar import ProgressBar
import pickle
import random

EspeakWrapper.set_library('C:/Program Files/eSpeak NG/libespeak-ng.dll')

# generates a list of words broken down into their phonemes
# returns: List
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


# generates english phonemes from a sentence
# returns: Set
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

# shuffles a list of phonemes
# returns: List
def remix_phonemes(phonemes1):
    phoneme_list = list(phonemes1)
    random.shuffle(phoneme_list)
    return phoneme_list

# generates a mapping dict from phonemes1 to phonemes2
# returns: Dict
def generate_mapping(phonemes1, phonemes2):
    mapping = {}
    for i in range(len(phonemes1)):
        mapping[phonemes1[i]] = phonemes2[i]
    return mapping

# transcribes a phonetic sentence using a mapping
# returns: String
def transcribe(sentence, mapping):
    print(sentence)
    cleanSent = ''.join(char for char in sentence if char.isalnum() or char.isspace())
    words = cleanSent.split()

    res = []
    for word in words:
        phonemizedWord = phonemize(word, language="en-us", separator=Separator(phone="|", word='', syllable='||'))
        chars = phonemizedWord.split("|")
        print("".join(chars))
        for i in range(len(chars)):
            if chars[i] in mapping:
                chars[i] = mapping[chars[i]]
        word = "".join(chars)
        res.append(word)

    return " ".join(res)

# generates a mapping dict from consonants to phonemes2
def generate_unique_consonant_vowel_mappings(consonants, vowels, i, printout=False, remix_v = True, remix_c = True):
    
    if remix_v:
        remixed_v = remix_phonemes(vowels)
    else:
        remixed_v = list(vowels)

    if remix_c:
        remixed_c = remix_phonemes(consonants)
    else:
        remixed_c = list(consonants)
    
    remixed_c = remix_phonemes(consonants)
    mapping_c = generate_mapping(list(consonants), remixed_c)

    remixed_v = remix_phonemes(vowels)
    mapping_v = generate_mapping(list(vowels), remixed_v)

    mapping = {**mapping_c, **mapping_v}

    if printout:
        print("Consonants mapping:")
        print(mapping_c)
        print("Vowels mapping:")
        print(mapping_v)
        print("Full mapping:")   
        print(mapping)

    return mapping, mapping_v, mapping_c

def remix_mapping(mapping, printout=False):
    keys = list(mapping.keys())
    values = list(mapping.values())
    random.shuffle(values)
    new_mapping = dict(zip(keys, values))
    if printout:
        print("Remixed mapping:")
        print(new_mapping)
    return new_mapping