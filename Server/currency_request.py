#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 00:51:00 2018

@author: jia_qu
"""

import requests

def exchange(base,other):
    #base="USD"
    #other="GBP"
    resp=requests.get("https://api.exchangeratesapi.io/latest?",params={"base":base,"symbols":other})
    #resp=requests.get("https://data.fixer.io/api/latest?base=USD&symbols=EUR")
    
    if resp.status_code!=200:
        raise Exception("Error")
    data=resp.json()
    
    rate=data['rates'][other]
    #print("1 {} is equal to {} {}".format(base,rate,other))
   
    return(rate)

if __name__=="__main__":
    exchange("EUR","USD")
