'''
Crawls Craigslist webpage (the preferred approach).

Created on Jun 13, 2013

@author: yuncong
'''
import urllib
import re
import csv

prefix = 'http://sandiego.craigslist.org'

# search_name = 'civic'
# brand = 'honda'
# model = 'civic'
# trim = ['ex','lx','si','dx']

# search_name = 'fit'
# brand = 'honda'
# model = 'fit'
# trim = ['sport']

search_name = 'corolla'
brand = 'toyota'
model = 'corolla'
trim = ['s','le','l','dx','xle','xrs','ce']

type = ['sedan','coupe','hatchback']
years = [str(y) for y in range(1992,2014)]
years_short = [y[-2:]for y in years]
transm = ['automatic','manual']
srch_year = '2006'
start = 0

if __name__ == '__main__':
    url = 'http://sandiego.craigslist.org/search/cta?query='+brand+'%20'+model+'&srchType=T&s='+str(start)
    xml_str = urllib.urlopen(url).read()
    contents = re.findall('<p class="row" data-pid=".*?">(.*?)</p>', xml_str, re.M|re.S)
    
    keys = ['date','price','title','url','owner','trim','year','type','transm','cond']
    items = []

    for c in contents:
        item = dict([(k,None) for k in keys])
        
        item['date'] = re.findall('<span class="date">(.*?)</span>', c)[0]
        try:
            item['price'] = re.findall('<span class="price">(.*?)</span>', c)[0]
        except:
            pass

        item['title'] = re.findall('<a href=".*\.html">(.*?)</a> ?</span>', c)[0].strip()
        title_lower = item['title'].lower()
        
        item['url'] = prefix + re.findall('<a href="(.*?)"', c)[0]
        page = urllib.urlopen(item['url']).read()
        try:
            posting = re.findall('<section id="postingbody">(.*?)</section>', page, re.M|re.S)[0]
        except:
            continue
        posting_lower = posting.lower()
        
        for t in transm:
            if t in posting_lower or t in title_lower:
                item['transm'] = t
                break
        for t,s in zip(years,years_short):
            if re.search('(\W|^| )%s(\W|$| )'%t, posting_lower) \
                    or re.search('(\W|^| )%s(\W|$| )'%t, title_lower)\
                    or re.search('(\W|^| )%s(\W|$| )'%s, posting_lower) \
                    or re.search('(\W|^| )%s(\W|$| )'%s, title_lower):
                item['year'] = t
                break
        for t in type:
            if t in posting_lower or t in title_lower:
                item['type'] = t
                break
        for t in trim:
            if re.search('(\W|^| )%s(\W|$| )'%t, posting_lower) or re.search('(\W|^| )%s(\W|$| )'%t, title_lower):
                item['trim'] = t
                break
        
        if 'salvage' in posting_lower or 'salvage' in title_lower:
            item['cond'] = 'salvage'
        
        item['owner'] = re.findall('<a class="gc".*?by (.*?)</a>', c)[0]
        items.append(item)
    
    dw = csv.DictWriter(open(search_name+".csv", "wb"), fieldnames=keys)
#     dw.writerow(dict((fn,fn) for fn in keys))
    for i in items:
        dw.writerow(i)
