import pandas as pd
import re
import pickle
from ProcessData import ProcessData as preprocess
from WordStats import WordStats as stats

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
            clean_word = re.sub('[^A-Za-z]+', ' ', word) # no special char i.e. pizza!!Tony -> pizzaTony
            clean_word = re.sub('[^\S]', '', clean_word) # selects non-whitespace
            # all lowercase
            clean_word = clean_word.lower()
            if len(clean_word) > 2: # avoid adding "", single characters, double characters
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

def Get_Original_CSV(file_name):
    df = CSV_Reader(file_name)
    DF_to_CSV(df, "01_clean_train.csv")
    DF_to_PKL(df, "01_clean_train.pkl")

def Basic_Stop_Words(pkl_name):
    clean_df = Get_DF_from_PKL(pkl_name)
    m = preprocess(clean_df)
    stop_df = m.removeStopWords("./../stop_words.lst")
    DF_to_PKL(stop_df, "02_stop_df.pkl")
    DF_to_CSV(stop_df, "02_stop_df.csv")

def Remove_Infrequent_Words(freq, pkl_name):
    basic_stop_df = Get_DF_from_PKL(pkl_name)
    s = stats(basic_stop_df)
    old_dict = s.getDictionary() # returns dictionary

    new_dict = {key: value for key, value in old_dict.items() if value <= freq }

    ''' create a new file for the stop words and only run on those words '''
    og_stop_file = open("./../stop_words_new.lst", "w+")
    for word in new_dict:
        og_stop_file.write(word + '\n')

    m = preprocess(basic_stop_df)
    stop_df = m.removeWithDict(new_dict)
    full_name = re.split(r"\.", pkl_name)
    f_name =    full_name[0] + "_rem_freq" + str(freq)
    DF_to_PKL(stop_df, f_name+".pkl")
    DF_to_CSV(stop_df, f_name+".csv")


def main():
    ''' Data Preprocessing Pipeline '''

    ''' 0. Given the original dataset '''
    # Get_Original_CSV("./../train2.csv") # outputs: 01_clean_train.csv, 01_clean_train.pkl
    ''' Comment-out above after use '''

    """ 1. Removing Words with Basic Stop Word List """
    # Basic_Stop_Words("01_clean_train.pkl") # outputs: 02_stop_df.csv, 02_stop_df.pkl
    ''' Comment-out above after use '''

    """ 2. Remove words with frequency less than 10  """
    Remove_Infrequent_Words(10, "02_stop_df.pkl") # outputs: 02_stop_df_rem_freq_10.csv, 02_stop_df_df_rem_freq_10.pkl






main()