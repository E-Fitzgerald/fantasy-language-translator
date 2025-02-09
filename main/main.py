from textToPhonemes.textToPhonemes import generate_phonemes, generate_english_phonemes, remix_phonemes, generate_mapping, transcribe, generate_unique_consonant_vowel_mappings
from private_vars import getAWSAccessKeyId, getAWSSecret
import pickle
import boto3
import os
from contextlib import closing
from playsound import playsound
import time
import sys
from pydub import AudioSegment
from pydub.playback import play


TIGER_WOLF_TEXT = "A tiger and a mouse were walking in a field when they saw a big lump of cheese lying on the ground. The mouse said: \"Please, tiger, let me have it. You don't even like cheese. Be kind and find something else to eat.\" But the tiger put his paw on the cheese and said: \"It's mine! And if you don't go I'll eat you too.\" The mouse was very sad and went away. The tiger tried to swallow all of the cheese at once but it got stuck in his throat and whatever he tried to do he could not move it. After a while, a dog came along and the tiger asked it for help. \"There is nothing I can do.\" said the dog and continued on his way. Then, a frog hopped along and the tiger asked it for help. \"There is nothing I can do.\" said the frog and hopped away. Finally, the tiger went to where the mouse lived. She lay in her bed in a hole which she had dug in the ground. \"Please help me,\" said the tiger. \"The cheese is stuck in my throat and I cannot remove it." "You are a very bad animal,\" said the mouse. \"You wouldn't let me have the cheese, but I'll help you nonetheless. Open your mouth and let me jump in. I'll nibble at the cheese until it is small enough to fall down your throat.\" The tiger opened his mouth, the mouse jumped in and began nibbling at the cheese. The tiger thought: \"I really am very hungry..\" "

ENG_VOWLES = "pit pet pat cut put dog about week hard fork heard boot place home mouse clear care boy find tour ee ooo ou uo eh ah oh ih uh ae ai oi au er ar or ur"

ENG_MAPPING = None


def lang_choice(lang):
    lang_ops = ["eng", "pt"]

    while lang == "":
        choice = input("Please select one of the two languages to begin: eng, pt (or type 'QUIT' to exit):")
        if choice == "QUIT":
            break
        if choice in lang_ops:
            lang = choice
    
    return lang

def run_menu(lang, printout=False):
    sentence = ""
    while True:
        if sentence == "CHANGE" or sentence == "":
            lang = lang_choice(lang)
            if lang == "":
                print("Exiting program...")
                return

        instruction_word_dic = {"eng": "English", "pt": "Portuguese"}
        instruction_word = instruction_word_dic[lang]
        mapping = None
        if instruction_word == "English" and ENG_MAPPING is not None:
            mapping = ENG_MAPPING
        
        sentence = input("Please enter an " + instruction_word + " sentence (otherwise, type 'QUIT' to exit, or 'CHANGE' to change the language): ")

        if sentence == "QUIT":
            print("Exiting program...")
            break
        elif sentence == "CHANGE":
            continue
        else:
            if printout:
                phonemes = generate_phonemes(sentence, lang=lang)
                print(phonemes)

            if mapping is None:
                test_phonemes(sentence, lang="eng", printout=False)

            transcribed = transcribe(sentence, mapping)
            print(transcribed)
            speak(transcribed)
            

def speak(transcription, voice="Emma"):
    # init s3 and polly
    polly = boto3.client("polly", region_name='us-west-2',
         aws_access_key_id=getAWSAccessKeyId(),
         aws_secret_access_key= getAWSSecret())

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

    #say("main/cacher/data/audio/output", .75)

    # audio = AudioSegment.from_file("main/cacher/data/audio/output.mp3", format="mp3") # or other formats like "mp3"
    # slowed_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.75)})
    # slowed_audio = slowed_audio.set_frame_rate(audio.frame_rate)
    # play(slowed_audio)
    playsound("main/cacher/data/audio/output.mp3")



def test_phonemes(sentence, lang="eng", printout=False):

    if lang=="eng":
        eng_phonemes = generate_english_phonemes(sentence=TIGER_WOLF_TEXT, printout=False, regen=False, name="tiger_wolf")
        eng_vowel_phonemes = generate_english_phonemes(sentence=ENG_VOWLES, printout=False, regen=False, name="eng_vowels") - set(['k', 'ᵻ', "p", "t", "d", "b", "g", "f", "v", "ɡ", "s", "z", "m", "n", "l", "r", "w", "h", "j", "ng", "sh", "ch", "th", "zh", "dh", "hh", "jh", "wh", "zh", "th"])
        eng_vowel_phonemes.add('i')
        eng_vowel_phonemes.add('y')
        eng_vowel_phonemes.add('ə')
        eng_vowel_phonemes.add('iə')
        eng_vowel_phonemes.add('eɪ')
        eng_vowel_phonemes.add('əl')
        eng_vowel_phonemes.add('ᵻ')
    else:
        exit("Language not supported.")

    eng_consonants = eng_phonemes - eng_vowel_phonemes
    if printout:
        print(eng_phonemes)
        print(len(eng_phonemes))
        print(eng_vowel_phonemes)
    print("\n\n")
        
    c = 0
    choice = ""
    while True:
        if choice != "r" and choice != "y":
            print("Mapping #" + str(c))
            print("=====================================")
            file_name = "main/cacher/data/" + lang +  "/" + str(c) + ".p"

            if os.path.exists(file_name):
                print("Loading from file: " + file_name)
                try:
                    mapping = pickle.load(open(file_name, "rb"))
                except:
                    print("Error loading file: " + file_name)
                    c += 1
                    print("Mapping #" + str(c))
                    print("=====================================")
                    mapping = generate_unique_consonant_vowel_mappings(eng_consonants, eng_vowel_phonemes, c, printout=True)
            else:
                mapping = generate_unique_consonant_vowel_mappings(eng_consonants, eng_vowel_phonemes, c, printout=True)  

        if choice != 'y':
            transcribed = transcribe(sentence, mapping)
            print(transcribed)
            speak(transcribed, "Zeina")
            print("\n")
        
        choice = input("'y' to keep this mapping, 'c' to continue, 'd' to delete this mapping, , 'q' to quit, 'r' to repeat the sentence, 's' to jump to a specific entry, or simply type a new sentence: ")
        time.sleep(.5)
        print(choice)
        if choice == "y":
            pickle.dump(mapping, open(file_name, "wb"))
            print(f"Mapping {c} saved successfully.")
            print(pickle.load(open(file_name, "rb")))

            time.sleep(.5)

        elif choice == "q":
            sys.exit()

        elif choice == "c":
            c += 1

        elif choice == "d":
            confirm = input("Are you sure you want to delete this mapping? 'y' to confirm, 'n' to cancel: ")
            if confirm == "y":
                delete_file(file_name)
        
        elif choice == "s":
            c = int(input("Enter the mapping number to jump to: "))

        elif choice != "r":
            sentence = choice
            choice = "r"
        

def delete_file(file_name):
    try:
        os.remove(file_name)
        print(f"File {file_name} deleted successfully.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"Error deleting file {file_name}: {e}")

def main():
    run_menu("eng")
    # test_phonemes("Hello my good friend -- nice weather we are having!")
    pass
    


if __name__ == "__main__":
    main()

    def test_delete_file(s):
        file_name = "main/cacher/data/" + s + ".p"
        try:
            delete_file(file_name)
        except FileNotFoundError:
            print("Could not delete file. File not found: " + file_name)
            pass
        assert os.path.exists(file_name) == False
    
    test_delete_file("eng_0")
    test_delete_file("eng_1")
    test_delete_file("eng_2")
    test_delete_file("eng_3")
    test_delete_file("eng_4")