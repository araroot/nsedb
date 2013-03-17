import csv

html = '''
<html>
    <table border="1" style="border:1px dotted black;width:80%%;border-collapse:collapse;">
        <tr>
            <th style="padding:3px;">Index</th>
            <th style="padding:3px;">Todays Value</th>
            <th style="padding:3px;">SMA 20</th>
            <th style="padding:3px;">SMA 50</th>
            <th style="padding:3px;">SMA 100</th>
        </tr>
        %s
    </table>
</html>
'''

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

if __name__ == '__main__':
    markup = ''''''

    with open('../data/master_sheet.csv') as in_file:
        reader = csv.reader(in_file)
        for row in reader:
            markup += html_row_generator(row)

    f = open('out.html', 'w')
    f.write(html % markup)
    f.close()