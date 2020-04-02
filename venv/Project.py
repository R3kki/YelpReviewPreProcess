import pandas as pd
import re
import pickle
import xlrd
from ProcessData import ProcessData as preprocess
from WordStats import WordStats as stats
from textblob import TextBlob

def CSV_Reader(str):
    ''' Reads CSV and returns a pandas dataframe object '''
    data = pd.read_csv(str)
    text = data["text"]

    words = []
    for i in range(len(text)):
        word_row = []
        w = text[i].split()
        words.append(w)

    tupled_words = [tuple(word) for word in words]

    data["text"] = words

    return data

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

def Get_Original_CSV(file_name, tdata, *args):
    df = CSV_Reader(file_name)
    if len(args) >= 1:
        DF_to_CSV(df, "00_clean_"+tdata+".csv")
    DF_to_PKL(df, "00_clean_"+tdata+".pkl")

def min_max_key_length(dict):
    min = 10000000
    max = 0
    for key in dict.keys():
        if len(key) < min:
            min = len(key)
        if len(key) > max:
            max = len(key)

    return min, max

def clean_word(df_col, regex, *args):
    new_reviews = []
    for row in df_col:
        review = []
        for word in row:
            if len(args) >= 1:
                clean_word = re.sub(regex, '', word)
            else:
                clean_word = re.sub(regex, ' ', word)
            new_clean_word = clean_word.split()
            for ncw in new_clean_word:
                review.append(ncw)
        new_reviews.append(review)

    tupled_words = [tuple(word) for word in new_reviews]
    return tupled_words

def Emoji_Process(pkl_name, *args):
    emoji_file = "./../emoji2.xlsx"
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

    ''' convert emoji into a score and take the score sum of all emojis found in that review '''
    emoji = []
    for row in emojis:
        score = 0
        for e in row:
            if e in emoji_dict:
                score = score + float(emoji_dict[e]['score'])
        emoji.append(score)

    df["text"] = text
    df["emoji"] =  emoji

    if len(args) >= 1:
        DF_to_CSV(df, "01_emoji.csv")
    DF_to_PKL(df, "01_emoji.pkl")

    return df

def Rating_Process(pkl_name, *args):
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

    if len(args) >= 1:
        DF_to_CSV(df, "02_rating.csv")
    DF_to_PKL(df, "02_rating.pkl")
    return df

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def Star_Review(pkl_name, *args):
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

    if len(args) >= 1:
        DF_to_CSV(df, "03_star_review.csv")
    DF_to_PKL(df, "03_star_review.pkl")

def Punctuation(pkl_name, *args):
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
        num_em.append(rev_em)
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

    if len(args) >= 1:
        DF_to_CSV(df, "04_punctuation.csv")
    DF_to_PKL(df, "04_punctuation.pkl")
    return df

def Capitialized(pkl_name, *args):
    df = Get_DF_from_PKL(pkl_name)
    caps = []
    for review in df["text"]:
        caps_review = 0
        for word in review:
            if (word.isupper() and len(word) > 1):
                caps_review = caps_review + 1
        caps.append(caps_review)

    df['caps'] = caps

    if len(args) >= 1:
        DF_to_CSV(df, "05_capitalized.csv")
    DF_to_PKL(df, "05_capitalized.pkl")

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

def Label_Dict(datatype, *label):
    df = Get_DF_from_PKL("00_clean_"+datatype+".pkl")
    txt = clean_word(df['text'], '[^A-Za-z\']')
    text = clean_word(txt, '[^A-Za-z]', True) # replaces ' with '': don't -> dont
    df['text'] = text
    p = preprocess(df)
    p.removeStopWords("./../stop_words.lst")
    df = p.getDF()

    text = []
    for i in range(len(df)):
        if len(label) >= 1 and label[0] == df["class"][i]:
            text.append(df["text"][i])

    df_text = {
        'text' : text
    }

    df_new = pd.DataFrame(df_text)
    m = stats(df_new)
    DF_to_PKL(df_new, "000_"+datatype+"_"+label[0]+"_dict.pkl")
    dict = m.getDictionary()
    return dict

def Sentiment(pkl_name, *args):
    df = Get_DF_from_PKL(pkl_name)

    ''' add each file into its own hashset for faster lookup '''
    #positive_words = file_lookup("../positive-negative-words/positive-words.txt")
    #negative_words = file_lookup("../positive-negative-words/negative-words.txt")
    f_pos = open("../positive-negative-words/positive-words.txt", "r", encoding="ISO-8859-1")
    f_neg = open("../positive-negative-words/negative-words.txt", "r", encoding="ISO-8859-1")

    ''' Take the most frequent words in the neutral reviews'''
    #neutral_dict = Label_Dict("test", "neutral") # only need to run once to get the _dict.pkl file
    df_neutral = Get_DF_from_PKL("000_train_neutral_dict.pkl")

    #positive_dict = Label_Dict("test", "positive")  # only need to run once to get the _dict.pkl file
    df_positive = Get_DF_from_PKL("000_train_positive_dict.pkl")

    #negative_dict = Label_Dict("test", "negative")  # only need to run once to get the _dict.pkl file
    df_negative = Get_DF_from_PKL("000_train_negative_dict.pkl")

    m = stats(df_neutral)
    neutral_dict = m.getDictionary()

    n = stats(df_positive)
    positive_dict = n.getDictionary()

    o = stats(df_negative)
    negative_dict = o.getDictionary()

    positive_words = []
    negative_words = []
    for x in f_pos:
        positive_words.append(x[0:len(x)-1])
    for x in f_neg:
        negative_words.append(x[0:len(x)-1])
        
    pos = []
    neg = []
    neutral = []
    posSent = []
    negSent = []
    neuSent = []
    sent_tot = []

    for review in df['text']:
        totsen = 0
        neu_sen = 0
        pos_sen = 0
        neg_sen = 0
        pn = 0
        nn = 0
        mn = 0
        for word in review:
            sen = TextBlob(word).sentiment.polarity
            if sen < 0:
                neg_sen = neg_sen + 1
            if sen > 0:
                pos_sen = pos_sen + 1
            if sen == 0:
                neu_sen = neu_sen + 1
            totsen = totsen + sen
            
            if word in positive_words and word not in negative_words and word in positive_dict:
                pn = pn + positive_dict[word]
            if word in negative_words and word not in positive_words and word in negative_dict:
                nn = nn + negative_dict[word]
            if word not in positive_words and word not in negative_words and word in neutral_dict:
                mn = mn + neutral_dict[word]
        posSent.append(pos_sen)
        negSent.append(neg_sen)
        neuSent.append(neu_sen)
        sent_tot.append(totsen)
        pos.append(pn)
        neg.append(nn)
        neutral.append(mn)
    
    df['postive_sent'] = posSent
    df['negative_sent'] = negSent
    df['neutral_sent'] = neuSent
    df['total_sent'] = sent_tot
    df['positive_words'] = pos
    df['negative_words'] = neg
    df['neutral_words'] = neutral

    if len(args) >= 1:
        DF_to_CSV(df, "06_sentiment.csv")
    DF_to_PKL(df, "06_sentiment.pkl")

    return df

def Basic_Stop_Words(pkl_name, tdata, *args):
    clean_df = Get_DF_from_PKL(pkl_name)
    m = preprocess(clean_df)
    m.casingNumbers()
    m.removeStopWords("./../stop_words.lst")

    stop_df = m.getDF()
    f_name = "10_"+ tdata + "_basic_stop"

    if len(args) >= 1:
        DF_to_CSV(stop_df, f_name + ".csv")

    DF_to_PKL(stop_df, f_name + ".pkl")

def Remove_Infrequent_Words(freq, pkl_name, *args):
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

    if len(args) >= 1:
        DF_to_CSV(stop_df, f_name + ".csv")
    DF_to_PKL(stop_df, f_name+".pkl")

def main():
    ''' Data Preprocessing Pipeline '''

    '''------------------------------ Training Data below -----------------------------'''
    ''' For datatype: select: 'train' or 'test' 
        For all the methods that are of 0.# add additional argument "True" if you want csv to be outputted as well
        By default no CSV is outputted 
    '''
    # ONLY VALUE YOU HAVE TO CHANGE
    datatype = "test"      # CHANGE TO TEST OR TRAIN
    # ONLY VALUE YOU HAVE TO CHANGE

    ''' 0. Training Data: to DF from CSV '''
    # Get_Original_CSV("./../train2.csv", datatype) # filename here
    #Get_Original_CSV("./../test2.csv", datatype)  # filename here

    """ 0.1 Test Data: Add attribute: Emojis """
    #Emoji_Process("00_clean_"+datatype+".pkl")

    """ 0.2 Test Data: Add attribute: Rating out of 10 """
    #Rating_Process("01_emoji.pkl")

    """ 0.3 Test Data: Add attribute: Star Reviews"""
    #Star_Review("02_Rating.pkl")

    """ 0.4 Test Data: Add attribute: # of ! and # of ? """
    #Punctuation("03_star_review.pkl")

    """ 0.5 Test Data: Add attribute: # of capitalized words """
    #Capitialized("04_punctuation.pkl")

    """ 0.6 Test Data: Add attributs: # of positive words and # of negative words"""
    Sentiment("05_capitalized.pkl")

    """ 1. Test Data: Removing Words with Basic Stop Word List """
    Basic_Stop_Words("06_sentiment.pkl", datatype)

    """ 2. Test Data: Remove words with frequency less than 10  """
    Remove_Infrequent_Words(10, "10_"+datatype+"_basic_stop.pkl", True)

main()
