#!/usr/bin/python3

import requests
import pyquery
import re
import time
import difflib
import io
import xlsxwriter
import PIL.Image

root_url = 'http://www.fermedesaintemarthe.com/A-14762-collection-120-varietes-de-tomates.aspx'

resp = requests.get(root_url)
resp.raise_for_status()

pq = pyquery.PyQuery(resp.text)

res = pq('.description').text()

re_res = re.search('^(.*)(TOMATE CHAMPAGNE.*)$', res).groups()


tomates_list = [x.strip() for x in re_res[1].split('-')]

real_tomates_list = []

for tomate in tomates_list:
    
    tomate_split = tomate.split('TOMATE')
    tomate_split = ['TOMATE '+x.strip() for x in tomate_split if x]
    for tomate in tomate_split:
        if tomate == 'TOMATE NOIRE RUSSE CHARBONNEUSE':
            tomate = 'TOMATE NOIRE RUSSE'
        elif tomate == 'TOMATE ANANAS':
            tomate = 'TOMATE ANANAS (PINAPPLE)'
        real_tomates_list.append(tomate)


assert len(real_tomates_list) == 120, 'first request failed, retrived tomates list should be 120 elems'

#real_tomates_list = [x for x in real_tomates_list if x == 'TOMATE RUSSE']
#real_tomates_list = real_tomates_list[:5]

d_tomates = []
for tomate in real_tomates_list:

    search_url = 'https://www.fermedesaintemarthe.com/search.aspx'
    resp = requests.get(search_url, params={'q': tomate})
    resp.raise_for_status()
    pq = pyquery.PyQuery(resp.text)
    res = pq('.hasLink')
    d_res = {}
    for index, link in enumerate(res('a')):
        link_val = link.attrib['href'] if 'href' in link.attrib else '#'
        if link_val != '#':
            span_val = res('a > span')
            span_val = span_val[index].text
            d_res[span_val] = link_val

    if len(d_res) == 0:
        print('Search returned nothing for %s' % tomate)

    if len(d_res) > 1:
        print('Search returned multiples results for %s' % tomate)
        d_res_keys_sorted = sorted(d_res.keys(), key=lambda x: difflib.SequenceMatcher(None, x, tomate).ratio(), reverse=True)
        d_res = { d_res_keys_sorted[0]: d_res[d_res_keys_sorted[0]] }
        print(d_res)

    if d_res:
        link = list(d_res.values())[0]
        resp = requests.get(link)
        resp.raise_for_status()
        pq = pyquery.PyQuery(resp.text)
        description = pq('.description').text().split('Quand et comment semer la tomate')[0]
        description = re.sub('De couleurs et de formes différentes, elles feront de votre potager un lieu de curiosité. Leur parfum et saveur vous feront découvrir le plaisir du goût retrouvé. ', '', description)

        image_link = pq('.galleryyyThumbs img')[0].attrib['data-original']

        d_tomates.append({
            'nom': tomate,
            'lien': link,
            'description': description,
            'image_url': image_link,
            'image_filename': image_link.split('/')[-1]
        })
        
    else:
       d_tomates.append({'nom': tomate})

    time.sleep(3)

workbook  = xlsxwriter.Workbook('tomates.xlsx')
worksheet = workbook.add_worksheet()

max_name_col_size = 10
worksheet.set_column(0, 0, max_name_col_size)
worksheet.set_column(1, 1, 15)
worksheet.set_column(2, 2, 50)

cell_format = workbook.add_format()
cell_format.set_text_wrap()

worksheet.set_column(3, 3, 30) # Pictures size
for row_index, tomate in enumerate(d_tomates):
    worksheet.set_row(row_index, 130) # Pictures size
    for col_index, value in enumerate(tomate.values()):
        if col_index in [0, 1, 2]:
            worksheet.write(row_index, col_index, value, cell_format)
        elif col_index == 3:
            resp = requests.get(value)
            resp.raise_for_status()
            image_bytes = io.BytesIO(resp.content)
            pil_img = PIL.Image.open(image_bytes)
            pil_img = pil_img.resize((150, 150), PIL.Image.ANTIALIAS)
            new_image_bytes = io.BytesIO()
            pil_img.save(new_image_bytes, format='JPEG')
            filename = list(tomate.values())[2]
            worksheet.insert_image(row_index, col_index, filename, {'image_data': new_image_bytes, 'positioning': 1})
            print(row_index)
            print(col_index)
            print(filename)

        if col_index == 0:
            if len(value) > max_name_col_size:
                max_name_col_size = len(value)
                worksheet.set_column(0, 0, max_name_col_size)
    time.sleep(3)

workbook.close()
