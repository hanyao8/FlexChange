import requests
from pattern import web
import re

url='https://www.dailyfx.com/forecasts?ref=SubNav'
html=requests.get(url).text

dom=web.Element(html)
bytag_span=dom.by_tag('span')

#for item in bytag_span:
#    print(item.content)

curname_dict={'USD':['us dollar','greenback','usd'],'EUR':['euro','eur']}
cur_wordbags={'USD':[],'EUR':[]}

span_text=[(item.content).lower() for item in bytag_span]
for text in span_text:
    wordbag=text.split()
    for curr in list(curname_dict.keys()):
        for curname in curname_dict[curr]:
            if curname in wordbag:
                cur_wordbags[curr]+=wordbag

punct_to_remove=['.',',','[',']','!','?',':',';','-','(',')']
for punct in punct_to_remove:
    print(punct)
    for curr in list(curname_dict.keys()):
        wordbag=cur_wordbags[curr]
        for i in range(0,len(wordbag)):
            wordbag[i]=wordbag[i].replace(punct,'')


        



