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

def DF_to_CSV(df, new_name):
    ''' Run Once: get the cleaned data into a csv file '''
    new_train_file = "./../" + new_name
    df.to_csv(new_train_file, encoding='utf-8', index=False)


def DF_to_PKL(df, new_name):
    ''' Avoid reading the data each time to process the original .csv.
        Returns new object removes special characters, whitespace, and puts into a dataframe object '''
    new_pkl_file = "./../" + new_name
    df.to_pickle(new_pkl_file)

def Get_DF_from_PKL(new_name):
    ''' Returns df object from pkl file'''
    pkl_name = "./../" +new_name
    train_data = pickle.load(open(pkl_name, "rb"))
    return train_data

def Remove_Stop_Words(data):
    ''' Returns df object with removed words from stop list file'''
    stop_file = "./../stop_words.lst"
    stop_words = [line.rstrip('\n') for line in open(stop_file)]

    text = data["words"]

    words = []
    for i in range(len(text)):
        text_row = []
        for j in range(len(text[i])):
            # clean up words. i.e. "Fun should be fun
            w = text[i][j]
            if w not in stop_words:
                text_row.append(w)
        words.append(text_row)

    tupled_words = [tuple(word) for word in words]
    label = data["class"]
    id = data["ID"]
    df_sw = {
        'ID': id,
        'class': label,
        'words': tupled_words
    }
    df = pd.DataFrame(df_sw)
    return df

def Get_Original_CSV(file_name):
    df = CSV_Reader(file_name)
    DF_to_CSV(df, "clean_train.csv")
    DF_to_PKL(df, "clean_train.pkl")


def main():
    ''' Run Once: get pandas object (pickle) as a new file. then comment out '''
    Get_Original_CSV("./../train2.csv") # outputs: clean_train.csv, clean_train.pkl
    ''' Comment out above '''

    ''' Start Pre-processing methods '''

    clean_df = Get_DF_from_PKL("clean_train.pkl")
    stop_df = Remove_Stop_Words(clean_df)
    DF_to_CSV(stop_df, "stop_df.csv")


main()