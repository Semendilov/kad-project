import time
import random
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from flask import Flask, request, abort, jsonify

def validate(date_text):
    date_regex = re.compile(r'^(3[01]|[12][0-9]|0[1-9]).(1[0-2]|0[1-9]).[0-9]{4}$')
    match = date_regex.search(date_text)
    if match:
        return True
    return False

def pars_func(args):
    if len(args)==0:
        return []

    playwright = sync_playwright().start()
    browser = playwright.firefox.launch()
    page = browser.new_page()
    page.goto("https://kad.arbitr.ru")
    time.sleep(2)
    page.keyboard.press("Escape")
    time.sleep(2)

    if 'participant' in args and args['participant'] != '':
        page.fill('textarea:visible', args['participant'])
    if 'judge' in args and args['judge'] != '':
        page.fill('input:visible', args['judge'])
    if 'court' in args and args['court'] != '':
        page.fill('input:visible >> nth=1', args['court'])
    if 'numdelo' in args and args['numdelo'] != '':
        page.fill('input:visible >> nth=2', args['numdelo'])
    if 'datefrom' in args and 'dateto' in args and validate(args['datefrom']) and validate(args['dateto']):
        page.fill('input:visible >> nth=3', args['datefrom'])
        page.fill('input:visible >> nth=4', args['dateto'])
        page.keyboard.press("Tab")

    time.sleep(1.2)
    page.click('id=b-form-submit')
    time.sleep(4)

    souppage = BeautifulSoup(page.content(), 'lxml')
    totalpages = souppage.find('input', id="documentsPagesCount").get('value')

    data = []
    for i in range(1, int(totalpages)+1):
        if i !=1:
            page.click(f'id=pages >> a[href = "#page{i}"]')
            time.sleep(random.random()*5+4)
        souppage = BeautifulSoup(page.content(), 'lxml')
        td = souppage.find('table', id="b-cases")
        soup = BeautifulSoup(td.prettify(), 'lxml')
        tr = soup.find_all('tr')
        for t in tr:
            delotype = t.find('td',class_='num').find('div',class_='b-container').find('div').get('class')[0]
            delo = ';'.join(t.find('td',class_='num').text.replace('\n', '').split())
            url = t.find('td',class_='num').find('a',class_='num_case').get('href')
            court = ';'.join(t.find('td',class_='court').text.replace('\n', '').split())
            try:
                plaintiff = t.find('td',class_='plaintiff').find('span',class_='js-rolloverHtml').text.split('\n')
                plaintiff = [i.strip() for i in plaintiff]
                plaintiff = ';'.join(list(filter(None,plaintiff)))
            except:
                plaintiff = ''
            try:
                respondent = []
                respall = t.find('td',class_='respondent').find_all('span',class_='js-rolloverHtml')
                for resp in respall:
                    resp = [i.strip() for i in resp.text.split('\n')]
                    resp = ';'.join(list(filter(None,resp)))
                    respondent.append(resp)
            except:
                respondent = ''
            data.append({'delotype': delotype,
                         'delo': delo,
                         'url': url,
                         'court': court,
                         'plaintiff': plaintiff,
                         'respondent': respondent})
    return data

app = Flask(__name__)

@app.route('/kad-service/', methods=['POST'])
def index():
    query = request.values.to_dict()
    if query == {}:
        abort(400)
    return jsonify(pars_func(query)), 200

if __name__ == '__main__':
    app.run(debug=True)