import pandas as pd
import re

# returns a words[][] each row contains a list of words for that review
def CSV_Reader(str):
    data = pd.read_csv(str)
    text = data["text"]
    label = data["class"]
    id = data["ID"]

    words = []
    for i in range(len(text)):
        srw = []
        single_review_words = text[i].split()
        for word in single_review_words:
            # clean up words. i.e. "Fun should be fun
            clean_word = re.sub('[^A-Za-z]+', '', word)
            # all lowercase
            clean_word = clean_word.lower()
            srw.append(clean_word)
        words.append(srw)

    return words

def CSV_Cleaner():
    file_name = "./../train2.csv"
    data = pd.read_csv(str)
    label = data["class"]
    id = data["ID"]
    words = CSV_Reader(file_name)

    print(words[0][0])




def main():
    CSV_Cleaner()
main()