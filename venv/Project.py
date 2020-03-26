import pandas as pd
import re
import pickle
import xlrd
from ProcessData import ProcessData as preprocess
from WordStats import WordStats as stats

def CSV_Reader(str, *args):
    ''' Reads CSV and returns a pandas dataframe object '''
    data = pd.read_csv(str)
    text = data["text"]

    words = []
    for i in range(len(text)):
        word_row = []
        w = text[i].split()
        words.append(w)


    tupled_words = [tuple(word) for word in words]

    id = data["ID"]
    if len(args) < 1:   # training data
        label = data["class"]
        df = {
            'ID': id,
            'class': label,
            'text': tupled_words
        }
    else:               # test data
        df = {
            'ID': id,
            'text': tupled_words
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

def min_max_key_length(dict):
    min = 10000000
    max = 0
    for key in dict.keys():
        if len(key) < min:
            min = len(key)
        if len(key) > max:
            max = len(key)

    return min, max

def clean_word(df_col, regex):
    new_reviews = []
    for row in df_col:
        review = []
        for word in row:
            clean_word = re.sub(regex, ' ', word)
            new_clean_word = clean_word.split()
            for ncw in new_clean_word:
                review.append(ncw)
        new_reviews.append(review)

    tupled_words = [tuple(word) for word in new_reviews]
    return tupled_words

def Emoji_Process(pkl_name):
    emoji_file = "./../emoji.xlsx"
    data = pd.read_excel(emoji_file)
    emoji_dict = data.set_index('emoji').T.to_dict('dict')
    e_min, e_max = min_max_key_length(emoji_dict)

    df = Get_DF_from_PKL("00_clean_test.pkl")
    emojis = []

    # add attribute: emoji
    for row in df["text"]:
        found_emojis = []
        for word in row:
            # find all substrings of the word that could possibly match an emoji
            for size in range(e_min, e_max+1):
                for index in range(len(word)-e_min+1):
                    substr = word[index:index+size]
                    if substr in emoji_dict:
                        # emoji exists in the word
                        found_emojis.append((substr))
                        # print(word, substr)
        emojis.append(found_emojis)
    # remove emojis and all emoji related characters from the reviews
    text = clean_word(df["text"], '[^A-Za-z0-9!?/]')

    id = df["ID"]
    df_em = {
        'ID': id,
        'emoji': emojis,
        'text': text
    }
    df = pd.DataFrame(df_em)

    DF_to_CSV(df, "01_emoji.csv")
    DF_to_PKL(df, "01_emoji.pkl")

    return df

def Rating_Process(pkl_name):
    df = Get_DF_from_PKL(pkl_name)

    ''' Number Ratings '''
    # change #/# -> to a number i.e. 10/10 = 10
    rating = []
    for review in df["text"]:
        found_rating = []
        for word in review:
            # do not check dates. i.e. 11/14/10
            bl = word.split("/")
            if "/10" in word and "/100" not in word and len(bl) == 2:
                clean_rating = re.sub("/10", '', word)  # remove /10 part
                clean_rating = re.sub("[^0-9]", '', clean_rating)  # remove 10/10service words trailed
                found_rating.append(clean_rating)
        rating.append(found_rating)

    ''' Remove all dates and ratings from the data set'''
    text = []
    for review in df["text"]:
        words = []
        for word in review:
            if "/" not in word:
                words.append(word)
        text.append(words)

    tupled_words = [tuple(word) for word in text]

    id = df["ID"]
    emojis =df["emoji"]
    df_rate = {
        'ID': id,
        'emoji' : emojis,
        'rate'  : rating,
        'text'  : tupled_words
    }
    df = pd.DataFrame(df_rate)

    DF_to_CSV(df, "02_Rating.csv")
    DF_to_PKL(df, "02_Rating.pkl")
    return df


def Star_Review(pkl_name):
    df = Get_DF_from_PKL(pkl_name)

    ''' Separate Numbers and characters. i.e. 3stars = 3 stars '''
    # for word in w:
    #     alpha_num = re.split('(\d+)', word)
    #     for a in alpha_num:
    #         if len(a) > 0:
    #             word_row.append(a)
    # words.append(word_row)

    rated = clean_word(df["text"], '[^A-Za-z0-9!?]')

    ''' Star Ratings '''
    # Numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven",
    #            "eight", "nine", "ten", "eleven"]
    # for i in range (111): # since people do not usually type fifty-stars but maybe 50 stars
    #     Numbers.append(str(i))
    # number_dict = dict.fromkeys(Numbers, 0)
    # n_min, n_max = min_max_key_length(number_dict)
    #
    # Stars = ["stars", "star", "Stars", "Star", "STARS", "STAR"]
    # star_dict = dict.fromkeys(Stars, 0)
    # s_min, s_max = min_max_key_length(star_dict)
    #
    # fixed_numbers = []
    #
    # # combine numbers if consecutive. i.e [prev] 3, [curr] 5 -> then 3.5
    # for i in range(len(rated)):
    #     fixed_rows = []
    #     prev = ''
    #     for j in range(len(rated[i])):
    #         if j > 0 and prev in number_dict and rated[i][j] in number_dict:
    #             # remove the previous number and just use the current word as the new combined #
    #             fixed_rows[j-1] = ''
    #             fixed_rows.append(prev + "." + rated[i][j])
    #         else:
    #             fixed_rows.append(rated[i][j])
    #         prev = rated[i][j]
    #     fixed_numbers.append(fixed_rows)
    #
    # # remove the empty and words that have been replace/combined
    #
    # text = []
    # for review in fixed_numbers:
    #     text_row = []
    #     for word in review:
    #         if len(word) > 0:
    #             text_row.append(word)
    #     text.append(text_row)
    #
    # star_reviews = []
    # for review in text:
    #     found_star_reviews = []
    #     prev = ''
    #     for word in review:
    #         curr_word_is_star = False
    #         # look if the current word is "stars" or "star"
    #         for s_size in range(s_min, s_max + 1):
    #             for index in range(len(word) - s_min + 1):
    #                 substar = word[index:index + s_size]
    #                 if substar in star_dict:
    #                     curr_word_is_star = True
    #         # check if previous word is a #: i.e. [prev] 4, [curr] stars
    #         prev_word_is_number = False
    #         star_review = ''
    #         if curr_word_is_star:
    #             for n_size in range(n_min, n_max + 1):
    #                 for n_index in range(len(prev) - n_min + 1):
    #                     subnumber = prev[index:index + n_size]
    #                     if subnumber in number_dict:
    #                         prev_word_is_number = True
    #                         star_review = subnumber
    #         if prev_word_is_number:
    #             found_star_reviews.append(subnumber)
    #         prev = word
    #     star_reviews.append(found_star_reviews)
    #
    # text = clean_word(df["text"], '[^A-Za-z!?]')
    #
    # id = df["ID"]
    # emojis =df["emoji"]
    # df_star = {
    #     'ID': id,
    #     'emoji' : emojis,
    #     'rate'  : rating,
    #     'star'  : star_reviews,
    #     'text'  : text
    # }
    # df = pd.DataFrame(df_star)
    #
    # DF_to_CSV(df, "02_rating.csv")
    # DF_to_PKL(df, "02_rating.pkl")

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

    ''' 0. Test Data: to DF from CSV '''
    # Get_Original_CSV("./../test2.csv", True) # outputs: 01_clean_test.csv, 01_clean_test.pkl

    """ 0.1 Test Data: Add attribute: Emojis """
    # Emoji_Process("00_clean_test_stop_df.pkl")

    """ 0.2 Test Data: Add attribute: Rating out of 10 """
    Rating_Process("01_emoji.pkl")

    """ 0.3 Test Data: Add attribute: Star Reviews"""

    """ 0.4 Test Data: Add attribute: # of ! and # of ? """




    """ 1. Test Data: Removing Words with Basic Stop Word List """
    # Basic_Stop_Words("01_clean_test.pkl", True) # outputs: 02_clean_test_basic_stop.csv, 02_clean_test_basic_stop.pkl

    """ 2. Test Data: Remove words with frequency less than 10  """
    # Remove_Infrequent_Words(10, "02_stop_df.pkl") # outputs: 02_stop_df_rem_freq_10.csv, 02_stop_df_df_rem_freq_10.pkl
    ''' Comment-out above after use '''

main()