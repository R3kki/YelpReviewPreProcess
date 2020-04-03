import csv
import re
import os

if os.path.exists('../final_data/train_final.csv'):
    os.remove('../final_data/train_final.csv')

with open('../final_data/train_final.csv', 'w') as outputCSV:
    with open('../train_basic_stop_rem_freq1000.csv', 'r') as inputCSV:
        writer = csv.writer(outputCSV,delimiter=',')
        reader = csv.reader(inputCSV,delimiter=',')
        next(reader,None)
        s = "ID,class,text,emoji,rate,star,num_em,num_qm,caps,positive_sentiment,negative_sentiment,neutral_sentiment,total_sentiment,positive_words,negative_words,neutral_words\n"
        outputCSV.write(s)
        for row in reader:
            aReview = [row[2],row[1],row[0],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]]
            writer.writerow(aReview)
            
            
            
