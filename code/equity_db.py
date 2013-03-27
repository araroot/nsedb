import csv
import sqlite3
import datetime
import os
import math

def skipheader(reader):
    try:
        headers = reader.next()
        return True
    except:
        print '*** DEBUG, got an empty file *** '
        return False 

def parsedate(dstamp):
    try:
        return datetime.datetime.strptime(dstamp, '%d-%b-%y')
    except ValueError:
        try:
            return datetime.datetime.strptime(dstamp, '%d-%b-%Y') # format changed in later  years
        except ValueError:
            print 'DEBUG: failed to parse date given as ', dstamp
            return None    

def fill_fo_volt_table(c, con, path):
    for filename in sorted(os.listdir(path)):
        filedate = datetime.datetime.strptime(filename.split('.')[0], '%d%m%Y')
        is_updated = c.execute('select * from update_status where date=? and table_name=?',[filedate, 'fo_volt']).fetchone()
        if is_updated: 
            print 'fo_volt table is already up-to-date for ', filedate
            continue
        
        with open(path + filename, 'r') as f:
            reader = csv.reader(f)
            if not skipheader(reader): continue
            
            for row in reader:
                if row == []: continue
                pdate = parsedate(row[0])
                if not pdate: continue

                volt = float(row[-1])
                if volt < 1.0: volt = volt * 100.0 # From 29 Mar 2011, they changed it
                c.execute('insert or replace into fo_volt values (?,?,?)', [row[1], pdate, volt])
        
        print 'DEBUG: updated fo_volt for', filename, filedate
        c.execute('insert into update_status values (?,?,?)', ['fo_volt', filedate, 1]) # This stmt is executed only once per file       
        con.commit()

def fill_fo_price_table(c, con, path):
    for filename in sorted(os.listdir(path)):
        filedate = datetime.datetime.strptime(filename.split('.')[0], '%d%m%Y')
        
        is_updated = c.execute('select * from update_status where date=? and table_name=?',[filedate, 'fo_prices']).fetchone()
        if is_updated: 
            print 'fo_prices table is already up-to-date for ', filedate
            continue
        
        with open(path + filename, 'r') as f:
            reader = csv.reader(f)
            if not skipheader(reader): continue
            
            for row in reader:
                if row == [] or row[1] != 'OPTSTK': continue
                pdate = parsedate(row[0])
                if not pdate: continue
                
                c.execute('insert into fo_prices values (?,?,?,?)', [row[2], pdate, row[1], float(row[4])])
        
        print 'DEBUG: updated fo_prices data for', filename, filedate
        c.execute('insert into update_status values (?,?,?)', ['fo_prices', filedate, 1]) # This stmt is executed only once per file       
        con.commit()


# To be done with caution - this table is hand fixed!!!
def _fill_fo_returns_backup_table(c, con):
    c.execute('INSERT or replace INTO fo_returns_backup SELECT * FROM fo_returns where adj_flag=1')
    con.commit()

def restore_handfix_table(c, con):
    c.execute('INSERT or replace INTO fo_returns SELECT * FROM fo_returns_backup where adj_flag > 0')
    con.commit()
    
def fill_returns_table(c, con):
    
    sym_list = c.execute('select distinct symbol from fo_prices').fetchall()
    for t in sym_list:
        stock = t[0]
        print stock
        rows = c.execute('select * from fo_prices where symbol=? order by date asc', [stock]).fetchall()

        for i in range(1,len(rows)):
            raw_return = math.log(rows[i][3]) - math.log(rows[i-1][3])
            adj_return = raw_return
            adj_flag   = 0

            c.execute('insert or replace into fo_returns values (?,?,?,?,?)', [stock, rows[i][1], raw_return, adj_return, adj_flag])

    con.commit()
    restore_handfix_table(c, con)

def create_tables(c):
    c.execute('''create table if not exists update_status (table_name text not null, date timestamp not null,  
                status integer, PRIMARY KEY(table_name, date))''')
    
    c.execute('''create table if not exists fo_returns (symbol text not null, date timestamp not null, raw_return real, 
                 adj_return real, adj_flag integer, PRIMARY KEY(symbol, date))''')
    
    c.execute('''create table if not exists fo_prices (symbol text not null, date timestamp not null, instrument text, 
                 price real, PRIMARY KEY(symbol, date))''') 
    
    c.execute('''create table if not exists fo_volt (symbol text not null, date timestamp not null, 
                 ann_volt real, PRIMARY KEY(symbol, date))''') 
    
    c.execute('''create table if not exists fo_returns_backup (symbol text not null, date timestamp not null, raw_return real, 
                 adj_return real, adj_flag integer, PRIMARY KEY(symbol, date))''')
    
    
if __name__ == '__main__':
    conn = sqlite3.connect('../data/equity.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    cur.execute('PRAGMA synchronous=OFF') # Make bulk inserts go faster
    conn.commit()
   
    create_tables(cur)

    fill_fo_price_table(cur, conn, path ='../data/fosett/')
    fill_fo_volt_table(cur, conn, path ='../data/fovolt/')
    fill_returns_table(cur, conn)
    
    conn.commit()
    conn.close()
