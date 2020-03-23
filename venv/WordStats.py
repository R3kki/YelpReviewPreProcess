''' Data collection techniques given a dataframe object'''
import pandas as pd
import operator

class WordStats:
    def __init__(self, data):
        self.data = data
        self.dict = {}

        ''' create dictionary '''
        id = self.data["ID"]
        label = self.data["class"]
        text = self.data["words"]

        words = []
        for i in range(len(text)):
            text_row = []
            for j in range(len(text[i])):
                # create dictionary
                w = doStemming(text[i][j])
                self.dict[w] = self.dict.get(w, 0) + 1

        doStemming()

    def doStemming(self, word):
        ''' Preform Porter Stemming Algorithm on the word
        w + consonant (not s) + s => w + consonant
        w + ies (not preceeded by e or a) => w + y
        w + ing and length > 4 => w
        w + consonant + ed and length > 4 => w + consonant
        '''
        word = self.word
        vowels = "aeiou"
        l = len(word)
        cut = 1
        if word[l-1] == 's':
            if not word[l-2] == None and word[l-2] not in vowels and not(word[l-2] == 's') :
                word = word[0:l-1]
        if l > 4:
            if word[l-3:l] == 'ies' and not not(word[l-4] == 'e' or word[l-4] == 'a'):
                word = word[0 : l-3] + 'y'
            elif word[l-3:l] == 'ies':
                word = word[0 : l-3]
            elif word[l-2:l] == 'ed' and word[l-3] not in vowels:
                word = word[0 : l-2]

        # m = 0 # [C](VC)^m[V]
        # prev = 'c'
        # # get M
        # for letter in word:
        #     if letter in vowels:
        #         prev = 'v'
        #     else:
        #         if prev == 'v':
        #             m = m + 1
        #         prev = 'c'




        return word


    def getDF(self):
        ''' Returns dataframe object -> type: dictionary '''
        sorted_x = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
        return pd.DataFrame.from_dict(sorted_x)

    def getDictionary(self):
        return self.dict


