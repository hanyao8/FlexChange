#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 00:24:59 2018

@author: jia_qu
"""

from flask import Flask, session, request, jsonify
import os
import sqlite3 as sq3
import requests
import json #json dumps and loads
import pandas as pd
import datetime
import currency_request as cr

#if __name__=="__main__":
#fixer_curr_names=cr.fixerapi_cur_names()

app=Flask(__name__)

app.config.update(dict(SECRET_KEY='secret_key'))
dbpath=os.path.join(os.getcwd(),'fc_db.db')


@app.after_request
def enable_cors(response):
   response.headers["Access-Control-Allow-Origin"] = "*"
   response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Token, Accept"
   response.headers["Access-Control-Allow-Methods"] = "OPTIONS, POST, PUT, GET, DELETE"
   return response


@app.route("/")
def index():
    
    #eur_usd=cr.exchange("EUR","USD")
    #exch_rate=pd.DataFrame([[1.0,1/eur_usd],[eur_usd,1.0]],index=['EUR','USD'],columns=['EUR','USD']) #1 eur=X usd
    try:
        fixer_resp=requests.get('http://data.fixer.io/api/latest?access_key=a0522fd9aa2fffffaa87f8767375886f')
        fixer_latest=json.loads(fixer_resp.content)
        fixer_rates=fixer_latest['rates']

        nowtime=datetime.datetime.now()
        
        conn=sq3.connect(dbpath)
        df_user=pd.read_sql_query("SELECT * FROM user;",conn)
        df_wallets=pd.read_sql_query("SELECT * FROM wallets;",conn)
        df_trans=pd.read_sql_query("SELECT * FROM trans;",conn)
        #cur=conn.cursor()




        #if nowtime>untiltime: #execute last transaction and delete in database
        
        until_arr_str=df_trans['until'].tolist()
        until_arr=[datetime.datetime.strptime(time_item, '%Y-%m-%d')for time_item in until_arr_str]

        transid_to_exe_list=[]
        for i in range(0,len(until_arr)):
            if until_arr[i]<nowtime and not(df_trans.iloc[i]['processed']=='True'):
                transid_to_exe_list.append(df_trans['transaction_id'][i])

        n_to_exe=len(transid_to_exe_list) #the number of transactions to execute

        #conn.commit()
        conn.close()

        for transid in transid_to_exe_list:
            
            conn=sq3.connect(dbpath)
            df_user=pd.read_sql_query("SELECT * FROM user;",conn)
            df_wallets=pd.read_sql_query("SELECT * FROM wallets;",conn)
            df_trans=pd.read_sql_query("SELECT * FROM trans;",conn)
            cur=conn.cursor()

            from_cur=df_trans['currency_from'][transid-1]
            #from_id=df_trans['wallet_from_id'][transid-1]
            #from_wallet=df_wallet.loc[df_wallet['currency']==from_cur]
            #from_wallet=from_wallet.loc[from_wallet['user_id']==from_id]
            #from_amount=from_wallet.iloc[0]['amount']-df_trans['amount_from'][transid-1]
            
            #query_from="update wallets set amount=%d where(user_id=%d and currency='%s');"%(from_amount,from_id,from_cur)
            #cur.execute(query_from)

            to_cur=df_trans['currency_to'][transid-1]
            to_id=df_trans['wallet_to_id'][transid-1]
            
            
            current_user_id=to_id.copy()
            df_wallets_of_user=df_wallets.loc[df_wallets['user_id']==to_id]


            if not(to_cur in df_wallets_of_user['currency'].tolist()): #create wallet if doesn't exist
                create_wallet_query="insert into wallets(user_id,currency,amount) values(%d,'%s',%f)"%(current_user_id,to_cur,0.0)
                cur.execute(create_wallet_query)
            
            
            conn.commit()
            conn.close()
            
            
            conn=sq3.connect(dbpath)
            cur=conn.cursor()
            df_user=pd.read_sql_query("SELECT * FROM user;",conn)
            df_wallets=pd.read_sql_query("SELECT * FROM wallets;",conn)

            to_wallet=df_wallets.loc[df_wallets['currency']==to_cur]
            to_wallet=to_wallet.loc[to_wallet['user_id']==to_id]
            to_amount=to_wallet.iloc[0]['amount']+df_trans['amount_from'][transid-1]/fixer_rates[from_cur]*fixer_rates[to_cur]


            query_to="update wallets set amount=%d where(user_id=%d and currency='%s');"%(to_amount,to_id,to_cur)
            cur.execute(query_to)
            conn.commit()

            query_processed="update trans set processed='True' where(transaction_id=%d)"%(transid)
            cur.execute(query_processed)
            conn.commit()
            conn.close()
       
        json_output=json.dumps({'success':True})

    except:
        json_output=json.dumps({'success':False})

    #conn.close()
    #return()
    return(json_output)

@app.route("/login",methods=['GET','POST'])
def login():
    #error=None
    #if request.method=='POST':
    #heads=request.headers
    #X_Token=heads['X-Token']
    content=request.json #decoded here into dict
        

    conn=sq3.connect(dbpath)
    df=pd.read_sql_query("SELECT * FROM user;",conn)
    conn.close()

    #success=True
    if not(content['username'] in df['username'].tolist()):
        success=False
        message='1'
    else: #the username does exist in the database
        user_row_index=(df.index[df['username']==content['username']].tolist())[0]
        if df.iloc[user_row_index]['password']==content['password']:
            success=True
            message='2'
            #session['logged_in']=True
            X_Token=df['xtoken'][user_row_index]
        else: #password doesn't match
            success=False
            message='3'

    if success:
        #app.config.update(dict(USERNAME=content['username']))
        json_output=json.dumps({'token':X_Token,'success':True})

    else:
        json_output=json.dumps({'token':'generic_token','success':False})
    
    str_output=str(json.loads(json_output))
    return(json_output)
    #return(str_output+message)
    #return(content['username'])
    #return(str(df['username'].tolist()))
    #return('hello_hello')
    #return(str(df.values))
    #return(str(df))
    #return(content)
    #return(str(content))

@app.route("/wallets")
def wallets():
    heads=request.headers
    X_Token=heads['X-Token']

    conn=sq3.connect(dbpath)
    df_user=pd.read_sql_query("SELECT * FROM user;",conn)
    df_wallets=pd.read_sql_query("SELECT * FROM wallets;",conn)
    df_trans=pd.read_sql_query("SELECT * FROM trans;",conn)
    conn.close()
    
    all_currencies=df_trans['currency_from'].append(df_trans['currency_to'])
    all_currencies=all_currencies.append(df_wallets['currency'])
    all_currencies=all_currencies.unique()

    try:
        #current_user=app.config['USERNAME']
        current_user=((df_user.loc[df_user['xtoken']==X_Token])['username'].tolist())[0]
        current_user_rowindex=(df_user.index[df_user['username']==current_user].tolist())[0]
        current_user_id=df_user['id'][current_user_rowindex]
        df_current_wallet=df_wallets.loc[df_wallets['user_id']==current_user_id]
        current_wallet=df_current_wallet.values

        
        df_pending=df_trans.loc[df_trans['processed']=='False']
        df_pending=df_pending.loc[df_pending['wallet_from_id']==current_user_id]
        
        pending_dict={}
        for wc in list(all_currencies):
            df_temp_pendings=(df_pending.loc[df_pending['currency_from']==wc])
            wc_pendings_list=[]
            for i in range(0,(df_temp_pendings).shape[0]):
                wc_pendings_list.append({'currency_to':df_temp_pendings.iloc[i]['currency_to'] ,'amount':df_temp_pendings.iloc[i]['amount_from'] ,'until':df_temp_pendings.iloc[i]['until'] })
            pending_dict[wc]=wc_pendings_list
                

        n_wallets=current_wallet.shape[0]
        json_output=json.dumps({'wallets':[{'currency':df_current_wallet.iloc[i]['currency'] , 'amount':str(df_current_wallet.iloc[i]['amount']),'is_main':i==0,'pending':pending_dict[df_current_wallet.iloc[i]['currency']] } for i in range(0,n_wallets) ]})
        

        
        str_output=str(json.loads(json_output))
    

    except:
        json_output=json.dumps({'status':'unsuccessful'})

    
    #return(str(current_wallet))
    #return(current_user)
    #return('hellolo')
    #return(output)
    #return(str(current_user_rowindex))
    #return(str(current_wallet))
    return(json_output)
    #return(str_output)

@app.route("/transaction",methods=['GET','POST'])
def transaction():
    heads=request.headers
    X_Token=heads['X-Token']

    #fixer_resp=requests.get('http://data.fixer.io/api/latest?access_key=a0522fd9aa2fffffaa87f8767375886f')
    #fixer_latest=json.loads(fixer_resp.content)
    #fixer_rates=fixer_latest['rates']

    try:
        content=request.json #decoded here into dict
    
        conn=sq3.connect(dbpath)
        df_user=pd.read_sql_query("SELECT * FROM user;",conn)
        df_wallets=pd.read_sql_query("SELECT * FROM wallets;",conn)
        df_trans=pd.read_sql_query("SELECT * FROM trans;",conn)

        current_user=((df_user.loc[df_user['xtoken']==X_Token])['username'].tolist())[0]
        #current_user=app.config['USERNAME']

        current_user_rowindex=(df_user.index[df_user['username']==current_user].tolist())[0]
        current_user_id=df_user['id'][current_user_rowindex]
        df_wallet_from=df_wallets.loc[df_wallets['user_id']==current_user_id]
        df_wallets_of_user=df_wallet_from.copy()
        wallet_from=df_wallet_from.values
        
        #check if wallet exists
        if not(content['currency_from'] in (df_wallet_from['currency'].tolist())):
            json_output=json.dumps({'success':False})


        #check if balance is enough for a transaction
        elif (df_wallet_from.loc[df_wallet_from['currency']==content['currency_from']])['amount'][0] - float(content['amount']) > 0:


            cur=conn.cursor()

            
            deduct_from_wallet_query="update wallets set amount=%d where(user_id=%d and currency='%s');"%( (df_wallet_from.loc[df_wallet_from['currency']==content['currency_from']])['amount'][0]-float(content['amount']) , current_user_id,content['currency_from'] )

            cur.execute(deduct_from_wallet_query)
            conn.commit()

            write_to_trans_query="insert into trans(wallet_from_id, wallet_to_id, currency_from, currency_to, until, amount_from, processed) values(%d,%d,'%s','%s','%s',%.2f,'%s');"%(current_user_id,current_user_id,content['currency_from'],content['currency_to'],content['until'],float(content['amount']),'False')
            
            cur.execute(write_to_trans_query) 
            #to implement functionality to account for modification of column names
            
            #cur.execute("insert into trans(id, wallet_from_id, wallet_to_id, currency_from, currency_to, until, amount_from) values(1,1,1,'EUR','USD','2018-09-18',50.00);")
            
            conn.commit()
            
            if not(content['currency_to'] in df_wallets_of_user['currency'].tolist()): #create wallet if doesn't exist
                create_wallet_query="insert into wallets(user_id,currency,amount) values(%d,'%s',%f)"%(current_user_id,content['currency_to'],0.0)
                cur.execute(create_wallet_query)
                conn.commit()
            #try:
            #success=True
            #except:
            #success=False
            #json_output=json.dumps([{'success':success}])
        
            
            output_message='success'
            json_output=json.dumps({'success':True})

        else:
            json_output=json.dumps({'success':False})

        conn.close()
    
    
    except:
        output_message='unsuccessful'
        json_output=json.dumps({'success':False})
        conn.close()
    #return(str(content))
    #return(current_user_id)
    #return(output_message)
    return(json_output)
    #return(write_query)
    #return()

#@app.route("/send-transaction",methods=['GET','POST'])
#def send_transaction():
#    content=request.json
#    cur_from=
#    cur_to=
#    return(jsonify({''}))


if __name__=="__main__":
    app.run(debug=True)
    


