from textToPhonemes.textToPhonemes import generate_phonemes, generate_english_phonemes, remix_phonemes, generate_mapping, transcribe
from private_vars import getAWSAccessKeyId, getAWSSecret
import pickle
import boto3
import os
from contextlib import closing
from botocore.exceptions import ClientError


TIGER_WOLF_TEXT = "A tiger and a mouse were walking in a field when they saw a big lump of cheese lying on the ground. The mouse said: \"Please, tiger, let me have it. You don't even like cheese. Be kind and find something else to eat.\" But the tiger put his paw on the cheese and said: \"It's mine! And if you don't go I'll eat you too.\" The mouse was very sad and went away. The tiger tried to swallow all of the cheese at once but it got stuck in his throat and whatever he tried to do he could not move it. After a while, a dog came along and the tiger asked it for help. \"There is nothing I can do.\" said the dog and continued on his way. Then, a frog hopped along and the tiger asked it for help. \"There is nothing I can do.\" said the frog and hopped away. Finally, the tiger went to where the mouse lived. She lay in her bed in a hole which she had dug in the ground. \"Please help me,\" said the tiger. \"The cheese is stuck in my throat and I cannot remove it." "You are a very bad animal,\" said the mouse. \"You wouldn't let me have the cheese, but I'll help you nonetheless. Open your mouth and let me jump in. I'll nibble at the cheese until it is small enough to fall down your throat.\" The tiger opened his mouth, the mouse jumped in and began nibbling at the cheese. The tiger thought: \"I really am very hungry..\" "

ENG_VOWLES = "pit pet pat cut put dog about week hard fork heard boot place home mouse clear care boy find tour ee ooo ou uo eh ah oh ih uh ae ai oi au er ar or ur"

ENG_MAPPING = pickle.load(open("main/cacher/data/eng_4.p", "rb"))


def lang_choice():
    lang_ops = ["en-us", "pt"]

    lang = ""
    while lang == "":
        choice = input("Please select one of the two languages to begin: en-us, pt (or type 'QUIT' to exit):")
        if choice == "QUIT":
            break
        if choice in lang_ops:
            lang = choice
    
    return lang

def run_menu():
    sentence = ""
    while True:
        if sentence == "CHANGE" or sentence == "":
            lang = lang_choice()
            if lang == "":
                print("Exiting program...")
                return

        instruction_word_dic = {"en-us": "English", "pt": "Portuguese"}
        instruction_word = instruction_word_dic[lang]
        mapping = None
        if instruction_word == "English":
            mapping = ENG_MAPPING
        
        sentence = input("Please enter an " + instruction_word + " sentence (otherwise, type 'QUIT' to exit, or 'CHANGE' to change the language): ")

        if sentence == "QUIT":
            print("Exiting program...")
            break
        elif sentence == "CHANGE":
            continue
        else:
            # phonemes = generate_phonemes(sentence, lang=lang)
            # print(phonemes)
            transcribed = transcribe(sentence, mapping)
            print(transcribed)
            speak(transcribed)
            

def speak(transcription):
    # init s3 and polly
    polly = boto3.client("polly", region_name='us-west-2',
         aws_access_key_id=getAWSAccessKeyId(),
         aws_secret_access_key= getAWSSecret())

    # get submitted text string and selected voice
    voice = "Emma"

    # generate phoneme tag for polly to read
    phoneme = f"<phoneme alphabet='ipa' ph='{transcription}'></phoneme>"

    # send to polly, requesting mp3 back
    response = polly.synthesize_speech(
        OutputFormat="mp3",
        TextType="ssml",
        Text=phoneme,
        VoiceId=voice
    )

    # save polly's returned audio stream to lambda's tmp directory
    tmpfile = os.path.join("main/cacher/data/audio/", "output.mp3")
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            with open(tmpfile, "wb") as file:
                file.write(stream.read())



def test_new_phonemes():
    sentence = TIGER_WOLF_TEXT
    eng_phonemes = generate_english_phonemes(sentence=sentence, printout=False, regen=False, name="tiger_wolf")
    sentence = ENG_VOWLES
    eng_vowel_phonemes = generate_english_phonemes(sentence=sentence, printout=False, regen=False, name="eng_vowels") - set(['k', 'ᵻ', "p", "t", "d", "b", "g", "f", "v", "ɡ", "s", "z", "m", "n", "l", "r", "w", "h", "j", "ng", "sh", "ch", "th", "zh", "dh", "hh", "jh", "wh", "zh", "th"])
    eng_vowel_phonemes.add('i')
    eng_vowel_phonemes.add('y')
    eng_vowel_phonemes.add('ə')
    eng_vowel_phonemes.add('iə')
    eng_vowel_phonemes.add('eɪ')
    eng_vowel_phonemes.add('əl')
    eng_vowel_phonemes.add('ᵻ')
    # print(eng_phonemes)
    # print(len(eng_phonemes))
    #print(eng_vowel_phonemes)
    excepted = [2, 4]
    print("\n\n")
    for i in range(5):
        if i in excepted: 
            print("Loading from cache...")
            mapping = pickle.load(open("main/cacher/data/eng_" + str(i) + ".p", "rb"))
        else:
            eng_consonants = eng_phonemes - eng_vowel_phonemes
            # print(eng_consonants)

            remixed_c = remix_phonemes(eng_consonants)
            mapping_c = generate_mapping(list(eng_consonants), remixed_c)
            #print(mapping_c)

            remixed_v = remix_phonemes(eng_vowel_phonemes)
            mapping_v = generate_mapping(list(eng_vowel_phonemes), remixed_v)
            #print(mapping_v)

            mapping = {**mapping_c, **mapping_v}

            pickle.dump(mapping, open("main/cacher/data/eng_" + str(i) + ".p", "wb"))

        print(mapping)
        sentence = "I am a ghost with a massive dong"
        transcribed = transcribe(sentence, mapping)
        print(transcribed)
        print("\n\n")

def main():
    run_menu()
    


if __name__ == "__main__":
    main()