import pandas as pd
import re
import pickle
from ProcessData import ProcessData as preprocess
from WordStats import WordStats as stats

def CSV_Reader(str, *args):
    ''' Reads CSV and returns a pandas dataframe object '''
    data = pd.read_csv(str)
    text = data["text"]

    words = []
    for i in range(len(text)):
        single_review_words = text[i].split()
        words.append(single_review_words)

    tupled_words = [tuple(word) for word in words]

    id = data["ID"]
    if len(args) < 1:   # training data
        label = data["class"]
        df = {
            'ID': id,
            'class': label,
            'words': tupled_words
        }
    else:               # test data
        df = {
            'ID': id,
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

def Get_Original_CSV(file_name, *args):
    if len(args) >= 1:
        df = CSV_Reader(file_name, True)        # test data with no class label
        DF_to_CSV(df, "00_clean_test.csv")
        DF_to_PKL(df, "00_clean_test.pkl")
    else:
        df = CSV_Reader(file_name)              # training data with class label
        DF_to_CSV(df, "00_clean_train.csv")
        DF_to_PKL(df, "00_clean_train.pkl")

def Emoji_to_Word(pkl_name):
    emoji_file = "./../emoji.csv"
    data = pd.read_csv(emoji_file)
    emoji = data["emoji"]
    emoji_text = data["text"]

    print(emoji)

    # emoji_dict = {}
    # for i in range(len(emoji_text)):
    #     text_row = []
    #     emoji_dict[i] = emoji_dict.get(i, 0) + 1
    #
    # print(emoji_dict)

    # clean_data = Get_DF_from_PKL("00_clean_test.pkl")




    # if len(args) >= 1:

def Basic_Stop_Words(pkl_name, *args):
    clean_df = Get_DF_from_PKL(pkl_name)
    m = preprocess(clean_df)
    if len(args) >= 1:
        stop_df = m.removeStopWords("./../stop_words.lst", args[0])
    else:
        stop_df = m.removeStopWords("./../stop_words.lst")

    f_name = "02_test_basic_stop" if len(args) >= 1 else "02_train_basic_stop"
    DF_to_PKL(stop_df, f_name + ".pkl")
    DF_to_CSV(stop_df, f_name + ".csv")



def Remove_Infrequent_Words(freq, pkl_name):
    basic_stop_df = Get_DF_from_PKL(pkl_name)
    s = stats(basic_stop_df)
    old_dict = s.getDictionary() # returns dictionary

    new_dict = {key: value for key, value in old_dict.items() if value <= freq }

    ''' create a new file for the stop words and only run on those words '''
    og_stop_file = open("./../stop_words_"+freq+".lst", "w+")
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

    ''' 0. Test Data: to DF from CSV'''
    # Get_Original_CSV("./../test2.csv", True) # outputs: 01_clean_test.csv, 01_clean_test.pkl
    ''' Comment-out above after use '''

    """ 0.5. Test Data: Transform emojis to words"""
    Emoji_to_Word("00_clean_test_stop_df.pkl")

    """ 1. Test Data: Removing Words with Basic Stop Word List """
    # Basic_Stop_Words("01_clean_test.pkl", True) # outputs: 02_clean_test_basic_stop.csv, 02_clean_test_basic_stop.pkl
    ''' Comment-out above after use '''





    # basic_stop_df = Get_DF_from_PKL("01_clean_test_stop_df.pkl")
    # s = stats(basic_stop_df, True)
    # s.getDictionary()  # returns dictionary
    # basic_stop_df = s.getDF()
    # print(basic_stop_df)


    """ 2. Test Data: Remove words with frequency less than 10  """
    # Remove_Infrequent_Words(10, "02_stop_df.pkl") # outputs: 02_stop_df_rem_freq_10.csv, 02_stop_df_df_rem_freq_10.pkl
    ''' Comment-out above after use '''

main()