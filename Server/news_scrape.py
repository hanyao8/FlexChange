import requests
from pattern import web
import scipy.signal as spsig
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np

url='https://us.cnn.com/?hpt=header_edition-picker'
html=requests.get(url).text

disaster_words=['hurricane','storm','cyclone','flood']
dw_count=sum([html.count(dw) for dw in disaster_words])

#base = datetime.datetime.today()
base=datetime.datetime.strptime('2018-12-31', '%Y-%m-%d')
days_series = [base - datetime.timedelta(days=x) for x in range(0, 365)]
simul_dw_series=spsig.gaussian(365,15)
simul_dw_series=np.append(simul_dw_series,np.zeros(5u))[-365:]
simul_dw_series*2-1
for i in range(0,len(simul_dw_series)):
    if simul_dw_series[i]<0.0:
        simul_dw_series[i]=0.0

plt.plot(days_series,simul_dw_series,linewidth=1.0)
plt.show()


