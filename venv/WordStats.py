''' Data collection techniques given a dataframe object'''
import pandas as pd
import operator
from ProcessData import ProcessData as process

class WordStats:
    def __init__(self, data, *args):
        self.data = data
        self.dict = {}

        obj = process(data)

        ''' create dictionary '''
        id = self.data["ID"]
        if len(args) < 1: label = data["class"]
        text = self.data["words"]

        words = []
        for i in range(len(text)):
            text_row = []
            for j in range(len(text[i])):
                # create dictionary
                w = obj.doStemming(text[i][j])
                self.dict[w] = self.dict.get(w, 0) + 1

    def getDF(self):
        ''' Returns dataframe object -> type: dictionary '''
        sorted_x = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
        return pd.DataFrame.from_dict(sorted_x)

    def getDictionary(self):
        return self.dict


