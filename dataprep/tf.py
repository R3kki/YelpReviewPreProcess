import csv
from ast import literal_eval

with open('../tf.txt', 'w') as tfFile:
    with open('../01_clean_train_stop_df.csv', 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        words = {}
        firstLine = True
        for row in reader:
            for word in literal_eval(row[2]):
                if firstLine:
                    firstLine = False
                    continue
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        for word in words:
            tfFile.write(str(words[word]) + " " + word + "\n")
