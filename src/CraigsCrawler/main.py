'''
Crawls Craigslist RSS, which does not contain all postings.

Created on Jun 12, 2013

@author: yuncong
'''

import xml.etree.ElementTree as ET
import urllib
import re
import csv

prefix = '{http://purl.org/rss/1.0/}'

trim = ['ex','lx','si']
level = ['sedan','coupe']
years = [str(y) for y in range(1992,2014)]
years_short = [y[-2:]for y in years]
transm = ['automatic','manual']

if __name__ == '__main__':
    items = []
    srch_year = '2006'
    brand = 'honda'
    model = 'civic'
#     url = 'http://sandiego.craigslist.org/search/cta?query='+srch_year+'%20'+brand+'%20'+model+'&srchType=T&format=rss'
    url = 'http://sandiego.craigslist.org/search/cta?query='+brand+'%20'+model+'&srchType=T&format=rss'
    xml_str = urllib.urlopen(url).read()
    root = ET.fromstring(xml_str)
    for child in root.iter(prefix+'item'):
        item = dict([('title',None),('link',None),('desc',None),('price',None),
                     ('transm',None),('year',None),('level',None),('trim',None)])
        for c in child:
            if re.match('\{.*\}date',c.tag):
                item['date'] = c.text
            elif re.match('\{.*\}title',c.tag) :
                item['title'] = c.text
                title_lower = c.text.lower()
                price = re.findall('\$[0-9]{4,5}',c.text)
                item['price'] = price[0] if len(price)>0 else None
            elif re.match('\{.*\}link',c.tag) :
                item['link'] = c.text
            elif re.match('\{.*\}description',c.tag):
                item['desc'] = c.text
                desc_lower = c.text.lower()
                for t in transm:
                    if t in desc_lower or t in title_lower:
                        item['transm'] = t
                        break
                for t,s in zip(years,years_short):
                    if t in desc_lower or t in title_lower or re.search('(^| )%s '%s, desc_lower) or re.search('(^| )%s '%s, title_lower):
                        item['year'] = t
                        break
                for t in level:
                    if t in desc_lower or t in title_lower:
                        item['level'] = t
                        break
                for t in trim:
                    if t in desc_lower or t in title_lower:
                        item['trim'] = t
                        break
        items.append(item)

    print len(items)
    
    c = csv.writer(open("civic.csv", "wb"))
    for i in items:
        c.writerow(i.values())
        
        