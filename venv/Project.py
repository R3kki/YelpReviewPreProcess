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

    df = Get_DF_from_PKL(pkl_name)
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
    text = clean_word(df["text"], '[^A-Za-z0-9!?/+-]')

    ''' take most common emoji '''
    emoji = []
    for row in emojis:
        row_dict = {}
        for e in row:
            if e not in row_dict:
                row_dict[e] = 1
            else:
                count = row_dict[e]
                row_dict[e] = count + 1

        ''' find the max '''
        max = 0
        result_emoji = ''
        for r in row_dict:
            if row_dict[r] > max:
                max = row_dict[r]
                result_emoji = r
        if max >0:
            emoji.append(result_emoji)
        else:
            emoji.append('?')

    df["text"] = text
    df["emoji"] =  emoji

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

    ''' Put Average rating into the file. ? if no rating '''
    rate = []
    for review in rating:
        sum = -1
        for i in review:
            sum =  sum + float(i)
        if (sum == -1):
            rate.append('?')
        else:
            rate.append(sum/len(review))



    ''' Remove all dates and ratings from the data set'''
    text = []
    for review in df["text"]:
        words = []
        for word in review:
            if "/" not in word:
                words.append(word)
        text.append(words)

    df['text'] = text
    df['rate'] = rate



    DF_to_CSV(df, "02_rating.csv")
    DF_to_PKL(df, "02_rating.pkl")
    return df

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def Star_Review(pkl_name):
    df = Get_DF_from_PKL(pkl_name)

    ''' Separate Numbers and characters. i.e. 3stars = 3 stars '''
    text = []
    for review in df["text"]:
        words = []
        for word in review:
            alpha_num = re.findall('(\d+)(\w*)', word)
            if len(alpha_num) > 0:
                for w in alpha_num[0]:
                    if len(w) > 0:
                        words.append(w)
            else:
                words.append(word)
        text.append(words)

    ''' Separate Capital Letters and no spaces. i.e. starsEven'''
    text_add_spaces = []
    for review in text:
        text_add = []
        for word in review:
            add_space = [0]
            is_prev_char_lower = False
            # find where to add spaces between words
            for c_index in range(len(word)):
                if word[c_index].isupper() and is_prev_char_lower:
                    add_space.append(c_index)
                if word[c_index].islower():
                    is_prev_char_lower = True
                else:
                    is_prev_char_lower = False
            add_space.append(len(word))
            word_spaced = ''

            # Add spaces to the word
            for i in range(1,len(add_space)):
                word_spaced = word_spaced + word[add_space[i-1]:add_space[i]] + ' '

            # finally resplit the word and add to final review
            splits = word_spaced.split()
            for w in splits:
                text_add.append(w)
        text_add_spaces.append(text_add)

    # text_add_spaces is the new legit review matrix

    """ Number dictionary initalized """
    Numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven",
               "eight", "nine", "ten", "eleven"]
    for i in range (111): # since people do not usually type fifty-stars but maybe 50 stars
        Numbers.append(str(i))
    number_dict = dict.fromkeys(Numbers, 0)
    n_min, n_max = min_max_key_length(number_dict)

    ''' Combine consecutive numbers  i.e [prev] 3, [curr] 5 -> then 3.5'''
    for i in range(len(text_add_spaces)):
        prev = ''
        for j in range(len(text_add_spaces[i])):
            curr = text_add_spaces[i][j]
            if prev in number_dict and curr in number_dict:
                text_add_spaces[i][j-1] = ''
                text_add_spaces[i][j] = prev + '.' + curr
            prev = text_add_spaces[i][j]

    # remove empty words that have been replaced/combined
    text = []
    for review in text_add_spaces:
        text_row = []
        for word in review:
            if len(word) > 0:
               text_row.append(word)
        text.append(text_row)

    ''' Star Ratings '''

    stars = ["stars", "star"]

    star_reviews = []
    for review in text:
        found_star_reviews = []
        prev = ''
        for word in review:
            curr_word_is_star = False
            prev_word_is_number = False
            # look if the current word is "stars" or "star"
            for s in stars:
                if s in word.lower():
                    curr_word_is_star = True

            # check if previous word is a #: i.e. [prev] 4, [curr] stars
            if prev.isnumeric() or is_number(prev):
                star_review = prev
                prev_word_is_number = True

            if prev_word_is_number and curr_word_is_star:
                found_star_reviews.append(star_review)
            prev = word
        star_reviews.append(found_star_reviews)

    ''' Put Average stars into the file. ? if no rating '''
    avg_star = []
    for review in star_reviews:
        sum = -1
        for i in review:
            sum = sum + float(i)
        if (sum == -1):
            avg_star.append('?')
        else:
            avg_star.append(sum / len(review))



    df['text'] = text
    df['star'] = avg_star



    DF_to_CSV(df, "03_star_review.csv")
    DF_to_PKL(df, "03_star_review.pkl")

def Punctuation(pkl_name):
    df = Get_DF_from_PKL(pkl_name)
    num_em = []
    num_qm = []
    for review in df["text"]:
        rev_em = 0
        rev_qm = 0
        for word in review:
            for c in word:
                if c == '!':
                    rev_em = rev_em + 1
                elif c == '?':
                    rev_qm = rev_qm + 1
        if rev_em == 0:
            num_em.append('?')
        else:
            num_em.append(rev_em)
        if rev_qm == 0:
            num_qm.append('?')
        else:
            num_qm.append(rev_qm)

    # remove ! and ? from the reviews
    text = []
    for review in df["text"]:
        text_row = []
        for word in review:
            text_word = ""
            nword = re.sub('[!?]', ' ', word)
            for w in nword:
                if len(w) > 0:
                    text_word = text_word + w
            if len(text_word) > 0:
                text_row.append(text_word)
        text.append(text_row)

    df['text'] = text
    df['num_em'] = num_em
    df['num_qm'] = num_qm


    DF_to_CSV(df, "04_punctuation.csv")
    DF_to_PKL(df, "04_punctuation.pkl")
    return df

def Capitialized(pkl_name):
    df = Get_DF_from_PKL(pkl_name)
    caps = []
    for review in df["text"]:
        caps_review = 0
        for word in review:
            if (word.isupper() and len(word) > 1):
                caps_review = caps_review + 1

        if caps_review == 0:
            caps.append('?')
        else:
            caps.append(caps_review)

    df['caps'] = caps



    DF_to_PKL(df, "05_capitalized.pkl")
    DF_to_CSV(df, "05_capitalized.csv")

    return df

def file_lookup(file_name):
    t = set()
    with open(file_name) as f:
        next(f)
        for line in f:
            if not line.startswith(';') and not line.startswith('\n'):
                word =re.sub('\n', '', line)
                t.add(word)
    return t

def Sentiment(pkl_name):
    df = Get_DF_from_PKL(pkl_name)

    ''' add each file into its own hashset for faster lookup '''
    positive_words = file_lookup("../positive-negative-words/positive-words.txt")
    negative_words = file_lookup("../positive-negative-words/negative-words.txt")

    pos = []
    neg = []

    for review in df['text']:
        pn = 0
        nn = 0
        for word in review:
            if word in positive_words:
                pn = pn + 1
            if word in negative_words:
                nn = nn + 1
        if pn == 0:
            pos.append('?')
        else:
            pos.append(pn)
        if nn == 0:
            neg.append('?')
        else:
            neg.append(nn)

    df['positive_words'] = pos
    df['negative_words'] = neg



    DF_to_PKL(df, "06_sentiment.pkl")
    DF_to_CSV(df, "06_sentiment.csv")
    return df

def Basic_Stop_Words(pkl_name):
    clean_df = Get_DF_from_PKL(pkl_name)
    m = preprocess(clean_df)
    m.casingNumbers()
    m.removeStopWords("./../stop_words.lst")

    stop_df = m.getDF()
    f_name = "10_test_basic_stop"
    DF_to_PKL(stop_df, f_name + ".pkl")
    DF_to_CSV(stop_df, f_name + ".csv")

def Remove_Infrequent_Words(freq, pkl_name):
    basic_stop_df = Get_DF_from_PKL(pkl_name)
    s = stats(basic_stop_df)
    old_dict = s.getDictionary() # returns dictionary

    new_dict = {key: value for key, value in old_dict.items() if value <= freq }

    ''' create a new file for the stop words and only run on those words '''
    new_fname ="./../stop_words_"+str(freq)+".lst"
    og_stop_file = open(new_fname, "w+")
    for word in new_dict:
        og_stop_file.write(word + '\n')

    m = preprocess(basic_stop_df)
    m.removeWithDict(new_dict)
    stop_df = m.getDF()
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
    # Rating_Process("01_emoji.pkl")

    """ 0.3 Test Data: Add attribute: Star Reviews"""
    # Star_Review("02_Rating.pkl")

    """ 0.4 Test Data: Add attribute: # of ! and # of ? """
    # Punctuation("03_star_review.pkl")

    """ 0.5 Test Data: Add attribute: # of capitalized words """
    # Capitialized("04_punctuation.pkl")

    """ 0.6 Test Data: Add attributs: # of positive words and # of negative words"""
    # Sentiment("05_capitalized.pkl")

    """ 1. Test Data: Removing Words with Basic Stop Word List """
    # Basic_Stop_Words("06_sentiment.pkl")

    """ 2. Test Data: Remove words with frequency less than 10  """
    # Remove_Infrequent_Words(10, "10_test_basic_stop.pkl")


    '''------------------------------ Training Data below -----------------------------'''

    ''' 0. Training Data: to DF from CSV '''
    Get_Original_CSV("./../train2.csv")

    """ 0.1 Test Data: Add attribute: Emojis """
    Emoji_Process("00_clean_train.pkl")

    """ 0.2 Test Data: Add attribute: Rating out of 10 """
    Rating_Process("01_emoji.pkl")

    """ 0.3 Test Data: Add attribute: Star Reviews"""
    Star_Review("02_Rating.pkl")

    """ 0.4 Test Data: Add attribute: # of ! and # of ? """
    Punctuation("03_star_review.pkl")

    """ 0.5 Test Data: Add attribute: # of capitalized words """
    Capitialized("04_punctuation.pkl")

    """ 0.6 Test Data: Add attributs: # of positive words and # of negative words"""
    Sentiment("05_capitalized.pkl")

    """ 1. Test Data: Removing Words with Basic Stop Word List """
    Basic_Stop_Words("06_sentiment.pkl")

    """ 2. Test Data: Remove words with frequency less than 10  """
    Remove_Infrequent_Words(10, "10_train_basic_stop.pkl")


main()