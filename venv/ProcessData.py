''' Different Preprocessing Methods given a dataframe object'''
import pandas as pd
class ProcessData:
    def __init__(self, data):
        self.data = data

    def removeWithDict(self, dict, *args):
        ''' uses a dictionary to remove words '''
        words = []

        id = self.data["ID"]
        text = self.data["words"]
        for i in range(len(text)):
            text_row = []
            for j in range(len(text[i])):
                w = text[i][j]
                if w not in dict:
                    text_row.append(w)
            words.append(text_row)

        tupled_words = [tuple(word) for word in words]

        if len(args) < 1: # training data
            label = data["class"]
            df_sw = {
                'ID': id,
                'class': label,
                'words': tupled_words
            }
        else: # test data
            df_sw = {
                'ID': id,
                'words': tupled_words
            }
        df = pd.DataFrame(df_sw)

        return df

    def removeStopWords(self, stop_file, *args):
        ''' Returns df object with removed words from stop list file'''
        stop_words = [line.rstrip('\n') for line in open(stop_file)]

        id = self.data["ID"]
        text = self.data["words"]

        words = []
        for i in range(len(text)):
            text_row = []
            for j in range(len(text[i])):
                # clean up words. i.e. "Fun -> fun
                w = text[i][j]
                if w not in stop_words:
                    text_row.append(w)
            words.append(text_row)

        tupled_words = [tuple(word) for word in words]

        if len(args) < 1:  # training data
            label = data["class"]
            df_sw = {
                'ID': id,
                'class': label,
                'words': tupled_words
            }
        else:  # test data
            df_sw = {
                'ID': id,
                'words': tupled_words
            }
        df = pd.DataFrame(df_sw)

        return df

    def doStemming(self, word):
        ''' Preform Porter Stemming Algorithm on the word
        w + consonant (not s) + s => w + consonant
        w + ies (not preceeded by e or a) => w + y
        w + ing and length > 4 => w
        w + consonant + ed and length > 4 => w + consonant
        '''
        word = word
        vowels = "aeiou"
        l = len(word)
        cut = 1
        if word[l-1] == 's':
            if not word[l-2] == None and word[l-2] not in vowels and not(word[l-2] == 's') :
                word = word[0:l-1]
        if l > 4:
            if word[l-3:l] == 'ies' and not not(word[l-4] == 'e' or word[l-4] == 'a'):
                word = word[0 : l-3] + 'y'
            elif word[l-3:l] == 'ing':
                word = word[0 : l-3]
            elif word[l-2:l] == 'ed' and word[l-3] not in vowels:
                word = word[0 : l-2]

        return word
