from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator

EspeakWrapper.set_library('C:\Program Files\eSpeak NG\libespeak-ng.dll')

def generate_phonemes(sentence, printout=False, lang="en-us"):
        cleanSent = ''.join(char for char in sentence if char.isalnum() or char.isspace())
        words = cleanSent.split()

        res = []
        for word in words:
            phonemizedWord = phonemize(word, language=lang, separator=Separator(phone="|", word='', syllable='||'))
            res.append(phonemizedWord)
            if printout:
                print(phonemizedWord)
                chars = phonemizedWord.split("|")
                print(chars)

        return res

        