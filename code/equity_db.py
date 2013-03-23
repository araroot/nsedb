import csv
import sqlite3
import datetime
import os
import math

def write_rows(f):
    reader = csv.reader(f)
        
    headers = reader.next()
    c.execute('''create table if not exists equity (on_date date, instrument text, stock text, price real)''')
    
    for row in reader:
        if row == []: continue
        if row[1] != 'OPTSTK': continue

        row[0] = datetime.datetime.strptime(row[0], '%d-%b-%y')
        
        float_indexes = [4]
        
        for i in float_indexes:
            row[i] = float(row[i])
        
        c.execute('insert into equity values (?,?,?,?)', [row[0], row[1], row[2], row[4]])
        c.execute('insert into updated values  (?,?,?)', [row[0], 'fosettle', 1])

def get_prev_day(d):
    cur_date = d

    cur_date -= datetime.timedelta(days=1)

    while cur_date.strftime('%d%m%Y') + '.csv' not in os.listdir(path):
        cur_date -= datetime.timedelta(days=1)

    return cur_date

def fo_settle(filename):
    # First file; skip
    if filename == '01012003.csv': return

    with open(path + filename, 'r') as f:
        reader = csv.reader(f)
        headers = reader.next()

        for row in reader:
            if row == []: continue
            if row[1] != 'OPTSTK': continue

            date  = datetime.datetime.strptime(row[0], '%d-%b-%y')
            stock = row[2]

            prev_day = get_prev_day(date)

            prev_price = c.execute('select price from equity where on_date=? and stock=?', [prev_day, stock])

            try:
                raw_return = math.log(float(row[4])) - math.log(prev_price.fetchone()[0])
            except TypeError:
                print prev_price.fetchone()
            adj_return = raw_return
            adj_flag   = 0

            c.execute('insert into fo_settle values (?,?,?,?,?)', [stock, prev_day, raw_return, adj_return, adj_flag])

if __name__ == '__main__':
    conn = sqlite3.connect('../data/equity.db')
    c = conn.cursor()

    today = datetime.datetime.now()

    c.execute('''create table if not exists updated (for_date date, entry_type text, yes_or_no real)''')
    c.execute('''create table if not exists fo_settle (stock text, for_date date, raw_return real, adj_return real, adj_flag real)''')

    c.execute('''create index if not exists date_index on updated(for_date)''')
    c.execute('''create index if not exists entry_type_index on updated(entry_type)''')

    path = '../data/equity/'

    # for filename in sorted(os.listdir(path)):
    #     print filename

    #     with open(path + filename, 'r') as f:
    #         write_rows(f)

    for filename in sorted(os.listdir(path)):
        print filename

        fo_settle(filename)
        