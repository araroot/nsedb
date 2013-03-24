import urllib
import urllib2
import re
import datetime
import time
import csv
import os
import random

# Code for the scraper
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

    indices   = re.findall(indices_pattern, indices_page)
    blacklist = ["CNX NIFTY JUNIOR", "CNX 100", "CNX 200", "CNX 500 SHARIAH", "CNX NIFTY SHARIAH", "NIFTY DIVIDEND", "CNX SERVICE", "S&P ESG INDIA INDEX"]

    return [index for index in indices[1:] if index not in blacklist]
 
def get_dates():
    today = datetime.datetime.now()

    start_date = (today-datetime.timedelta(days=random.randint(400,500))).strftime('%d-%m-%Y')
    end_date   = today.strftime('%d-%m-%Y')

    return start_date, end_date

def get_csv(index, start_date, end_date):
    file_name = index.replace(' ', '_') + '.csv'

    if file_name in os.listdir(data_folder): return

    params = urllib.urlencode({'indexType': index, 'fromDate': start_date, 'toDate': end_date})
    fetch_page('http://www.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?%s' % params)

    time.sleep(random.randint(2,6))

    handle = fetch_page('http://www.nseindia.com/content/indices/histdata/%s%s-%s.csv' % (urllib.quote(index), start_date, end_date))
    f = open(data_folder + file_name, 'w')
    f.write(handle.read())
    f.close()

def scraper_main():
    indices              = get_indices()
    start_date, end_date = get_dates()

    for index in indices:
        print 'Fetching csv for', index
        get_csv(index, start_date, end_date)

# Code for the SMA calculator
def get_closes(index):
    closes = []

    with open(data_folder + index, 'r') as f:
        reader = csv.reader(f)
        reader.next()

        for row in reader:
            closes.append(float(row[4]))

    return closes

def calc(closes, days_range):
    '''Calculates the moving average for the given range'''
    average = sum(closes[-days_range:])/days_range
    return average

def sma_main():
    indexes = os.listdir(data_folder)
    f = open('master_sheet.csv', 'w')
    csv_file = csv.writer(f)

    for index in indexes:
        closes = get_closes(index)
        row    = [index, closes[-1], calc(closes, 20), calc(closes, 50), calc(closes, 100)]
        csv_file.writerow(row)

    f.close()

# HTML creator
def html_row_generator(row):
    index, last_day, average20, average50, average100 = row

    average20_color = '#FFFFFF'
    if average20 < last_day: average20_color = '#9ACD32'

    average50_color = '#FFFFFF'
    if average50 < last_day: average50_color = '#9ACD32'

    average100_color = '#FFFFFF'
    if average100 < last_day: average100_color = '#9ACD32'

    html_row = '''
        <tr>
            <td style="padding:3px;">%s</td>
            <td style="padding:3px;">%.0f</td>
            <td style="padding:3px;background-color:%s;">%.0f</td>
            <td style="padding:3px;background-color:%s;">%.0f</td>
            <td style="padding:3px;background-color:%s;">%.0f</td>
        </tr>
    ''' % (index[:-4], float(last_day), average20_color, float(average20), average50_color, float(average50), average100_color, float(average100))

    return html_row

def table_main():
    markup = ''''''


    html_template = open('template.html').read()

    with open('master_sheet.csv') as in_file:
        reader = csv.reader(in_file)
        for row in reader:
            markup += html_row_generator(row)

    f = open('output.html', 'w')
    start_date, end_date = get_dates()

    f.write(html_template % (end_date, markup))
    f.close()

if __name__ == '__main__': 
    data_folder = '../data/' + datetime.datetime.now().strftime('%d-%m-%Y') + '/'

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    scraper_main()
    sma_main()
    table_main()    