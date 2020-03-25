import csv
import string
import pandas as pd
import re
import pickle
from ProcessData import ProcessData as preprocess

def CSV_Reader(str, *args):
    ''' Reads CSV and returns a pandas dataframe object '''
    data = pd.read_csv(str)
    text = data["text"]
    if len(args) < 1: label = data["class"]
    id = data["ID"]
    
    translator = str.maketrans('', '', string.punctuation)
    words = []
    for i in range(len(text)):
        srw = []
        single_review_words = text[i].split()
        for word in single_review_words:
            clean_word = word.replace('&','').replace('/','').replace('*','').replace('!', '').replace('.','').replace(',','').replace('?','') #remove all puntuation marks
            clean_word = re.sub('[^\S]', '', clean_word) # clean up whitespace
            clean_word = clean_word.replace('(','').replace(')','').replace('[','').replace(']','').replace('{', '').replace('}','') #remove all extra bracke
            clean_word = clean_word.lower() # all lowercase
            if len(clean_word) > 2: # avoid adding "", single characters, double characters
#                res = re.split(r'(\d+)', clean_word)
#                if(len(res) > 1):
#                    for s in res:
#                        srw.append(s)
#                else:
                srw.append(clean_word)
        words.append(srw)

    tupled_words = [tuple(word) for word in words]
    if len(args) < 1: # training data
        df = {
            'ID': id,
            'class': label,
            'words': tupled_words
        }
    else:
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
        df = CSV_Reader(file_name, True)
        DF_to_CSV(df, "01_clean_test.csv")
        DF_to_PKL(df, "01_clean_test.pkl")
    else:
        df = CSV_Reader(file_name)
        DF_to_CSV(df, "01_clean_train.csv")
        DF_to_PKL(df, "01_clean_train.pkl")

def Basic_Stop_Words(pkl_name, *args):
    clean_df = Get_DF_from_PKL(pkl_name)
    m = preprocess(clean_df)
    if len(args) > 0:
        stop_df = m.removeStopWords("./../stop_words.lst", args[0])
    else:
        stop_df = m.removeStopWords("./../stop_words.lst")

    full_name = re.split(r"\.", pkl_name)
    f_name = full_name[0] + "_stop_df"
    DF_to_PKL(stop_df, f_name + ".pkl")
    DF_to_CSV(stop_df, f_name + ".csv")
    
def replaceEmoji(file_name, *args):
    if len(args) > 0:
        f_name = './../test_edit1.csv'
    else:
        f_name = './../train_edit1.csv'
        
    with open('../emoji.csv', 'r') as emojiFile:
        emojiReader = csv.reader(emojiFile, delimiter = ',')
        emoji = []
        emojiLabel = []
        for row in emojiReader:
            emoji.append(row[0])
            emojiLabel.append(row[1])

    with open(f_name, 'w') as outputCSV:
        with open(file_name, 'r') as inputCSV:
            writer = csv.writer(outputCSV, delimiter = ',', quotechar = '"')
            reader = csv.reader(inputCSV, delimiter = ',')
            for row in reader:
                s = " "
                review = []
                words = []
                for word in row[0].split():
                    if word in emoji:
                        emotion = emojiLabel[emoji.index(word)]
                        words.append(emotion)
                    else:
                        words.append(word)
                s = s.join(words)
                review.append(s)
                review.append(row[1])
                review.append(row[2])
                writer.writerow(review)


def main():
    ''' Data Preprocessing Pipeline '''

    ''' 0. Given the original dataset '''
    #replaceEmoji("./../train3.csv")
    #Get_Original_CSV("./../train_edit1.csv") #outputs: 01_clean_train.csv, 01_clean_train.pkl
    ''' Comment-out above after use '''

    """ 1. Test Data: Removing Words with Basic Stop Word List """
    Basic_Stop_Words("01_clean_train.pkl") # outputs: 01_clean_test_stop_df.csv, 01_clean_test_stop_df.pkl
    ''' Comment-out above after use '''

main()
