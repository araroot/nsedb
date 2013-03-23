import csv
import sqlite3
import datetime

def write_rows(f):
    reader = csv.reader(f)
        
    headers = reader.next()
    c.execute('''create table if not exists bhavcopy (symbol text, series text,
                 open real, high real, low real, close real, last real, prev_close real, total_traded_quantity real, 
                 total_traded_volume real, timestamp date, total_trades real, isin text)''')
    
    for row in reader:
        row[10] = datetime.datetime.strptime(row[10], '%d-%b-%Y')
        
        float_indexes = range(2,10) + [11]
        
        for i in float_indexes:
            row[i] = float(row[i])
        
        c.execute('insert into bhavcopy values (?,?,?,?,?,?,?,?,?,?,?,?,?)', row[:-1])

def read_rows():
    for row in c.execute('select * from bhavcopy'):
        print row

if __name__ == '__main__':
    conn = sqlite3.connect('bhavcopy.db')
    c = conn.cursor()

    with open('cm22MAR2013bhav.csv', 'r') as f:
        write_rows(f)
    
    read_rows()