import pandas as pd
import re
import pickle

def CSV_Reader(str):
    ''' Reads CSV and returns a pandas dataframe object '''

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
            clean_word = re.sub('[^A-Za-z]+', ' ', word)
            clean_word = re.sub('[^A-Za-z]+', '', word) # seperate i.e. pizza!!Tony -> pizzaTony
            # all lowercase
            clean_word = clean_word.lower()
            srw.append(clean_word)
        words.append(srw)

    tupled_words = [tuple(word) for word in words]
    df = {
        'ID': id,
        'class': label,
        'words': tupled_words
    }
    df = pd.DataFrame(df)

    return df

def Get_CSV():
    ''' Run Once: get the cleaned data into a csv file '''

    file_name = "./../train2.csv"
    df = CSV_Reader(file_name)
    new_train_file = "./../clean_train.csv"
    df.to_csv(new_train_file, encoding='utf-8', index=False)


def Get_Data():
    ''' Avoid reading the data each time to process the original .csv.
        Returns new object removes special characters, whitespace, and puts into a dataframe object '''

    file_name = "./../train2.csv"
    df = CSV_Reader(file_name)
    df.to_pickle("./../clean_train.pkl")

def Read_Data():
    train_data = pickle.load(open("./../clean_train.pkl", "rb"))
    print(train_data)

def main():
    ''' Run Once: get pandas object (pickle) as a new file. then comment out '''
    # Get_Data()
    ''' Comment out above '''

    ''' Start Pre-processing methods '''
    Read_Data()


main()