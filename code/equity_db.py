import csv
import sqlite3
import datetime
import os
import math

def write_rows():
    for filename in sorted(os.listdir(path)):
        print filename

        with open(path + filename, 'r') as f:
            reader = csv.reader(f)
            headers = reader.next()
            
            for row in reader:
                if row == []: continue
                if row[1] != 'OPTSTK': continue

                row[0] = datetime.datetime.strptime(row[0], '%d-%b-%y')
                
                float_indexes = [4]

                for i in float_indexes:
                    row[i] = float(row[i])
                
                prev_records = c.execute('select * from equity where on_date=? and instrument=? and stock=? and price=?', [row[0], row[1], row[2], row[4]])
                
                if prev_records.fetchall() == []:
                    c.execute('insert into equity values (?,?,?,?)', [row[0], row[1], row[2], row[4]])
                    c.execute('insert into update_status values (?,?,?)', [row[0], 'fosettle', 1])

def fo_settle():
    stocks_list = []
    rows = c.execute('select stock from equity')
    
    for row in rows:
        stocks_list.append(row[0])

    stocks_list = list(set(stocks_list))

    for stock in stocks_list:
        print stock
        rows = c.execute('select * from equity where stock=? order by on_date asc', [stock]).fetchall()

        for i in range(1,len(rows)):
            raw_return = math.log(rows[i][3]) - math.log(rows[i-1][3])
            adj_return = raw_return
            adj_flag   = 0

            c.execute('insert into fo_settle values (?,?,?,?,?)', [stock, rows[i][0], raw_return, adj_return, adj_flag])

def create_tables():
    c.execute('''create table if not exists update_status (for_date timestamp, entry_type text, yes_or_no real)''')
    c.execute('''create table if not exists fo_settle (stock text, for_date timestamp, raw_return real, adj_return real, adj_flag real)''')

    c.execute('''create table if not exists equity (on_date timestamp, instrument text, stock text, price real)''')

    c.execute('''create index if not exists date_index  on fo_settle(for_date)''')
    c.execute('''create index if not exists stock_index on fo_settle(stock)''')

    c.execute('''create index if not exists date_index  on equity(on_date)''')
    c.execute('''create index if not exists stock_index on equity(stock)''')

    c.execute('''create index if not exists date_index  on update_status(for_date)''')
    c.execute('''create index if not exists entry_index on update_status(entry_type)''')

if __name__ == '__main__':
    conn = sqlite3.connect('../data/equity.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    today = datetime.datetime.now()

    create_tables()

    path = '../data/equity/'

    write_rows()
    fo_settle()

    conn.commit()
    conn.close()
        