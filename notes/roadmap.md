rough overiew:

english -> language -> phonemes -> new phonemes -> characters

-----
Steps:

-------A------- Get text to phonemes (January - March)
1) Take in english text -- engText
2) (optional) Translate english text to another language -- transText
3) transform transText into phonemes -- textPhonemes

-------B------- Get phonemes to phonemes (March - August)
1) re-map transPhonemes into new phonemes -- newPhonemes

will require experimentation on mappings in csv file, then optimized into a python dictionary (pandas)

-------C------- Get phonemes to text (August - October)
1) map phoneme/phoneme combinations to unique characters
2) print characters on screen in small font as a new image to be used as reference in art/writing

requires drawn sets of characters that can be imported as small image files, then arranged and printed on the screen for easy reference

-----
Language List:

This list is still under development because I still need to figure out what languages would be present in the world.

Confirmed:

1) English
2) Russian

Maybe:

1) Portuguese
2) Spanish
3) Arabic
4) Japanese
5) Hindi

