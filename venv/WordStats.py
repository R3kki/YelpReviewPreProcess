''' Data collection techniques given a dataframe object'''
import pandas as pd
import collections
import operator

class WordStats:
    def __init__(self, data):
        self.data = data
        self.dict = {}

    def frequencyList(self):
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

        sorted_x = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
        sorted_dict = collections.OrderedDict(sorted_x)

        print(sorted_dict)

        # show a chart of the words and its frequency
