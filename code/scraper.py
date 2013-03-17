import urllib
import urllib2
import re
import datetime
import time

def fetch_page(url):
    req = urllib2.Request(url)

    req.add_header('Accept', '*/*')
    req.add_header('User-Agent', 'Mozilla/5.0')
    req.add_header('Referer', 'http://www.nseindia.com/products/content/equities/equities/eq_security.htm')

    urlhandle = urllib2.urlopen(req)
    return urlhandle

def get_indices():
    indices_url  = 'http://www.nseindia.com/products/content/equities/indices/historical_index_data.htm'
    indices_page = fetch_page(indices_url).read()

    indices_pattern = '<option value="(.*?)".*?>'

    indices = re.findall(indices_pattern, indices_page)
    return indices[1:]

def get_dates():
    today = datetime.datetime.now()

    start_date = datetime.date(2012,1,1).strftime('%d-%m-%Y')
    end_date   = today.strftime('%d-%m-%Y')

    return start_date, end_date

def send_request(index, start_date, end_date):
    params = urllib.urlencode({'indexType': index, 'fromDate': start_date, 'toDate': end_date})
    url    = 'http://www.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?%s' % params

    print 'debug phase 1', url
    fetch_page(url)

def get_csv(index, start_date, end_date):
    #url = 'http://www.nseindia.com/content/indices/histdata/%s%s-%s.csv' % (index.replace(' ', '%20'), start_date, end_date)
    
    url = 'http://www.nseindia.com/content/indices/histdata/CNX%20NIFTY02-01-2012-17-03-2013.csv'
    print 'debug phase 2', url

    flag = False

    handle = fetch_page(url)
    print 'debug. got handle'
    f = open('../data/%s' % index, 'w')
    f.write(handle.read())
    f.close()

    flag = True

    return flag

if __name__ == '__main__':
    indices = get_indices()

    start_date, end_date = get_dates()

    for index in indices:
        print 'Fetching csv for', index

        send_request(index, start_date, end_date)

        flag = False
        time.sleep(2)

        flag = get_csv(index, start_date, end_date)