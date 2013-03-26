import urllib
import urllib2
import re
import datetime
import csv
import os
import time

def fetch_handle(url):
    req = urllib2.Request(url)

    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Referer', 'http://www.nseindia.com/products/content/equities/equities/eq_security.htm')

    urlhandle = urllib2.urlopen(req)
    return urlhandle

def format_date(d):
    return d.strftime('%d%m%Y')

def get_dates(start_date = datetime.datetime(2013,1,1), end_date = datetime.datetime.now()):
    dates = []
    cur_date = start_date

    while cur_date <= end_date:
        if cur_date.weekday() < 5: dates.append(cur_date)
        cur_date += datetime.timedelta(days=1)

    return dates

def get_csv(cur_date, filetype):

    data_folder = '../data/' + filetype +'/'
    file_name = format_date(cur_date) + '.csv'
    if file_name in os.listdir(data_folder): return

    params = urllib.urlencode({'h_filetype': filetype, 'date': cur_date.strftime('%d-%m-%Y'), 'section': 'FO'})
    response = fetch_handle('http://www.nseindia.com/ArchieveSearch?%s' % params).read()
    
    # probably a holiday, so we can ignore it
    if 'No file found for specified date. Try another date.' in response: return

    time.sleep(1)

    if filetype == 'fosett' : urltail = 'sett/FOSett_prce_%s.csv' %format_date(cur_date)
    if filetype == 'fovolt' : urltail = 'volt/FOVOLT_%s.csv' %format_date(cur_date)


    handle = fetch_handle('http://www.nseindia.com/archives/nsccl/' + urltail)
    f = open(data_folder + file_name, 'w')
    f.write(handle.read())
    f.close()

if __name__ == '__main__':
    dates_list  = get_dates(start_date=datetime.datetime(2003,1,1), end_date = datetime.datetime.now())
    
    for cur_date in dates_list:
        print 'Fetching data for', cur_date
        get_csv(cur_date, filetype='fovolt')
        #get_csv(cur_date, filetype='fosett') # Temporary comment
        cur_date += datetime.timedelta(days=1)