import pandas as pd
import re

# returns a pandas dataframe object
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

    df = {
        'ID': id,
        'class': label,
        'words': words
    }
    df = pd.DataFrame(df)

    return df

def Get_Data():
    file_name = "./../train2.csv"
    df = CSV_Reader(file_name)
    new_train_file = "./../clean_train.csv"
    df.to_csv(new_train_file, encoding='utf-8', index=False)

def main():
    Get_Data()

main()