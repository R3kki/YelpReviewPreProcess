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
                w = text[i][j]
                self.dict[w] = self.dict.get(w, 0) + 1

    def getDF(self):
        ''' Returns dataframe object -> type: dictionary '''
        sorted_x = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
        return pd.DataFrame.from_dict(sorted_x)

    def getDictionary(self):
        return self.dict


