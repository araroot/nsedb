import csv
import os

def get_closes(index):
    closes = []

    with open('../data/' + index, 'r') as f:
        reader = csv.reader(f)
        print dir(reader)

        reader.next()
        for row in reader:
            closes.append(float(row[4]))

    return closes

def calc(closes, days_range):
    '''Calculates the moving average for the given range'''
    average = sum(closes[-days_range:])/days_range
    return average

if __name__ == '__main__':
    indexes = os.listdir('../data/')

    f = open('../data/master_sheet.csv', 'w')

    for index in indexes:
        closes = get_closes(index)
        
        last_day    = closes[-1]
        average_20  = calc(closes, 20)
        average_50  = calc(closes, 50)
        average_100 = calc(closes, 100)

        line = '%s,%s,%s,%s,%s\n' % (index, str(last_day), str(average_20), str(average_50), str(average_100))
        f.write(line)

    f.close()