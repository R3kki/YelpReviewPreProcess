''' Different Preprocessing Methods given a dataframe object'''
import pandas as pd
class ProcessData:
    def __init__(self, data):
        self.data = data

    def removeStopWords(self, stop_file):
        ''' Returns df object with removed words from stop list file'''
        stop_words = [line.rstrip('\n') for line in open(stop_file)]

        id = self.data["ID"]
        label = self.data["class"]
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

        df_sw = {
            'ID': id,
            'class': label,
            'words': tupled_words
        }
        df = pd.DataFrame(df_sw)

        return df
