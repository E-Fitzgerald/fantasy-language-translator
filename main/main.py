from textToPhonemes.textToPhonemes import generate_phonemes

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

def main():

    sentence = ""
    while True:
        if sentence == "CHANGE" or sentence == "":
            lang = lang_choice()
            if lang == "":
                print("Exiting program...")
                return

        instruction_word_dic = {"en-us": "English", "pt": "Portuguese"}
        instruction_word = instruction_word_dic[lang]
        
        sentence = input("Please enter an " + instruction_word + " sentence (otherwise, type 'QUIT' to exit, or 'CHANGE' to change the language): ")

        if sentence == "QUIT":
            print("Exiting program...")
            break
        elif sentence == "CHANGE":
            continue
        else:
            phonemes = generate_phonemes(sentence, lang=lang)
            print(phonemes)

if __name__ == "__main__":
    main()