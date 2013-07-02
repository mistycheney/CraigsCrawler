'''
Crawls Craigslist webpage (the preferred approach).

Created on Jun 13, 2013

@author: yuncong
'''
import urllib
import re
import csv
import sys

prefix = 'http://sandiego.craigslist.org'

blacklisted_dealers = ['skyline', 'vtek', 'auto city', 'your choice']

# search_name = 'civic'
# brand = 'honda'
# model = 'civic'
# trims = ['ex','lx','si','dx']

# search_name = 'elantra'
# brand = 'hyundai'
# model = 'elantra'
# trims = ['gls','limited']

search_name = 'fit'
brand = 'honda'
model = 'fit'
trims = ['sport']

# search_name = 'corolla'
# brand = 'toyota'
# model = 'corolla'
# trims = ['s','le','l','dx','xle','xrs','ce']

types = ['sedan', 'coupe', 'hatchback']
years = [str(y) for y in range(1992, 2014)]
years_short = [y[-2:]for y in years]
transm = ['automatic', 'manual']
srch_year = '2006'
# start = 0
items = []

if __name__ == '__main__':
    keys = ['date', 'price', 'title', 'url', 'owner', 'trim', 'year', 'type', 'transm', 'cond', 'comment']
    try:
        dr = csv.DictReader(open(search_name + ".csv", "rU"), fieldnames=keys)
        for entry in dr:
            items.append(entry)
    except:
        pass
                         
    for start in range(0,500,100):
    
        url = 'http://sandiego.craigslist.org/search/cta?query=' + brand + '+' + model + \
                     '&srchType=T&zoomToPosting=&minAsk=&maxAsk=&s=' + str(start)
        xml_str = urllib.urlopen(url).read()
            
        contents = re.findall('<p class="row" data-.*?>(.*?)</p>', xml_str, re.M | re.S)
        
        for c in contents:
            
            item = dict([(k, None) for k in keys])
            
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
                posting = re.findall('<section id="postingbody">(.*?)</section>', page, re.M | re.S)[0]
            except:
                continue
            posting_lower = posting.lower()
            
            for t in transm:
                if t in posting_lower or t in title_lower:
                    item['transm'] = t
                    break
            for t, s in zip(years, years_short):
                if re.search('(^| )%s($| )' % t, title_lower) \
                    or re.search('(^| )%s($| )' % s, title_lower) \
                    or re.search('(^| )%s($| )' % t, posting_lower) \
                    or re.search('(^| )%s($| )' % s, posting_lower):
                    item['year'] = t
                    break
                
            for t in types:
                if t in posting_lower or t in title_lower:
                    item['type'] = t
                    break
            for t in trims:
                if re.search('(\W|^| )%s(\W|$| )' % t, posting_lower) or re.search('(\W|^| )%s(\W|$| )' % t, title_lower):
                    item['trim'] = t
                    break
    
            blacklisted = False
            for t in blacklisted_dealers:
                if re.search('(\W|^| )%s(\W|$| )' % t, posting_lower) or re.search('(\W|^| )%s(\W|$| )' % t, title_lower):
                    blacklisted = True
                    break
            if blacklisted:
                continue
            
            if 'salvage' in posting_lower or 'salvage' in title_lower:
                item['cond'] = 'salvage'
            
            item['owner'] = re.findall('<a class="gc".*?by (.*?)</a>', c)[0]
            items.append(item)
    
    item_num = len(items)
    print str(item_num) + ' items collected.'
    
    import string
    items_title = [i['title'].translate(None, string.punctuation) for i in items]
    items_title_sorted, items_sorted_by_title = zip(*sorted(sorted(zip(items_title, items), key=lambda (x,y):y['comment']))) 
    items_is_unique = [True] * item_num
    for i in range(0, item_num-1):
        if items_title_sorted[i] == items_title_sorted[i + 1]:
            items_is_unique[i] = False
         
    items_unique = [items_sorted_by_title[i] for i in range(item_num) if items_is_unique[i]]
    
    item_unique_num = len(items_unique)

    print str(item_unique_num) + ' unique items detected.'

    dw = csv.DictWriter(open(search_name + ".csv", "wb"), fieldnames=keys)
#     dw.writerow(dict((fn,fn) for fn in keys))
    for i in items_unique:
        dw.writerow(i)
