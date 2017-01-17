import re
import urllib2
import os
import webbrowser
import time
import csv
import mechanize
from mechanize._opener import urlopen
from mechanize._form import ParseResponse
import cookielib
import requests
import urllib
import smtplib
import sqlite3
import datetime





while True:
    start = "09:30:00"
    end = "16:00:00"


    datetimeStart = datetime.datetime.strptime(start, "%H:%M:%S").time()
    datetimeEnd = datetime.datetime.strptime(end, "%H:%M:%S").time()


    datetimeNow = datetime.datetime.now().time()

    currentDay = datetime.datetime.today().weekday()
    
    if currentDay != 5 and currentDay != 6:
        if datetimeStart < datetimeNow < datetimeEnd:

            z = 0
            while z < 100:
                try:

                    sent = []
                    sent2 = []
                     
                    conn = sqlite3.connect("stock_data.db")
                    c = conn.cursor()




                    while True:
                        start = "09:30:00"
                        end = "16:00:00"


                        datetimeStart = datetime.datetime.strptime(start, "%H:%M:%S").time()
                        datetimeEnd = datetime.datetime.strptime(end, "%H:%M:%S").time()


                        datetimeNow = datetime.datetime.now().time()

                        currentDay = datetime.datetime.today().weekday()
                        
                        if currentDay != 5 and currentDay != 6:
                            if datetimeStart < datetimeNow < datetimeEnd:
                        
                                #delete the current quotes.csv file
                                now = datetime.datetime.now()
                                print 'Checking at ' + now.strftime('%I:%M %p') + ' of day ' + now.strftime('%m/%d')    
                                try:
                                    os.remove("C:\Users\G-unit\Downloads\quotes.csv")
                                except:
                                    print 'There was no quotes.csv file to delete.'
                                i = 0
                                while i < 10000:
                                    #logging in to yahoo and passing credentials
                                    try:
                                        br = mechanize.Browser()
                                        cj = cookielib.LWPCookieJar()
                                        br.set_cookiejar(cj)

                                        br.set_handle_robots(False)
                                        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
                                        br.addheaders = [('User-agent', 'Chrome/54.0.2840.71')]
                                        response = br.open("https://finance.yahoo.com/portfolio/p_0/view?bypass=true")
                                        br.select_form(nr=0)
                                        br.form['username'] = 'stocksystm'
                                        response = br.submit()
                                        br.select_form(nr=0)
                                        br.form['passwd'] = 'peo0813xme'
                                        response = br.submit()
                                        i+=10000
                                    except:
                                        'Error logging in, trying again....'
                                        i+=1


                                print 'Login successful.'

                                #Viewing the URLS to be scanned for symbols
                                url = br.open('https://finance.yahoo.com/portfolio/pf_1/view/v1?bypass=true')
                                htmltext = url.read()
                                regex = "<tr data-row-symbol='([A-Z]{,6})'"
                                pattern = re.compile(regex)
                                results = re.findall(pattern,htmltext)
                                
                                stocks = []
                                #appending the results to a list called stocks
                                for i in results:
                                    stocks.append("+" + i)

                                url2 = br.open('https://finance.yahoo.com/portfolio/p_3/view/v1?bypass=true')
                                htmltext2 = url2.read()
                                
                                
                                results2 = re.findall(pattern,htmltext2)
                                #appending more results (the + is how yahoos url works)
                                for i in results2:
                                    stocks.append("+" + i)
                                    

                                #filling in the stocks to the url
                                i = 0
                                stocksheet = 'http://finance.yahoo.com/d/quotes.csv?s=GE'
                                while i < len(stocks):
                                    stocksheet+=stocks[i]
                                    i+=1
                                stocksheet+='&f=sm6'

                                #fetching the symbols from the database
                                databaseN = c.execute("SELECT Symbol FROM negative")
                                databaseN = c.fetchall()
                                databaseN = [x[0] for x in databaseN]
                                databaseP = c.execute("SELECT Symbol FROM positive")
                                databaseP = c.fetchall()
                                databaseP = [x[0] for x in databaseP]

                                #opening browser and subsequently downloading the quotes.csv file    
                                webbrowser.open_new_tab(stocksheet)
                                time.sleep(4)
                                sent2 = []
                                length = 0
                                #Searching the excel file for the symbols in the database and removing
                                #the symbols from the database that no longer fit the desired range
                                with open('C:\Users\G-unit\Downloads\quotes.csv', 'rb') as f:
                                    while length < 10000:
                                        try:
                                            reader = csv.reader(f)
                                            
                                            for row in reader:
                                                for i in databaseN:
                                                    if row[0] == i:
                                                        if float(row[1].replace('-','').replace('%','')) < 30:
                                                            print row[0] + ' should not exist in the database.'
                                                            c.execute('DELETE FROM negative WHERE Symbol ="%s"' % row[0])
                                                            
                                                for i in databaseP:
                                                    if row[0] == i:
                                                        if float(row[1].replace('+','').replace('%','')) < 25:
                                                            print row[0] + ' should not exist in the database.'
                                                            c.execute('DELETE FROM positive WHERE Symbol ="%s"' % row[0])*0
                                                            



                                            
                                                #adding values to the database if they do not exist there
                                                #also appending list sent2 with the values to be extracted for the email
                                                if row[1][0] == '-':
                                                    newRow = row[1].replace('-','').replace('%','')
                                                    newRow = float(newRow)
                                                    
                                                    if newRow >= 30:
                                                        if row[0] in databaseN:
                                                            continue
                                                        elif row[0] not in databaseN:
                                                            sent2.append(row)
                                                            c.execute('INSERT INTO negative VALUES (?,?)',
                                                                      (row[0], newRow))
                                                            
                                            
                                                elif row[1][0] == '+':
                                                    newRow = row[1].replace('+','').replace('%','')
                                                    newRow = float(newRow)
                                                    
                                                    if newRow > 25:
                                                        if row[0] in databaseP:
                                                            continue
                                                        elif row[0] not in databaseP:
                                                            sent2.append(row)
                                                            c.execute('INSERT INTO positive VALUES (?,?)',
                                                                      (row[0], newRow))
                                                            
                                                
                                            length+=10000
                                                            
                                        except Exception, e:
                                            print e
                                            length+=1
                                    conn.commit()          
                                    #preparing to send the email
                                    content = '\nThese quotes are outside of the range specified: \n \n'
                                    
                                    #if there exists a list sent2, add each element to the variable content
                                    #then send the file via email
                                    if sent2:
                                        for i in sent2:
                                            content = content + i[0] + "'s 200 day moving average is " +  i[1] + '\n'
                                        print content

                                        mail = smtplib.SMTP('smtp.gmail.com',587)

                                        mail.ehlo()

                                        mail.starttls()

                                        mail.login('sgotting21@gmail.com','hq2xmo6r3')

                                        mail.sendmail('sgotting21@gmail.com',['robg77@aol.com','tbtitans21@yahoo.com'], content)

                                        mail.close()
                                    else:
                                        print 'There has been no change.\n'
                                            

                                print '----------------------------------------------------\n'
                                                    
                                               

                                time.sleep(3600)




                            else:
                                break

                            
                except Exception, e:
                    print e
                    z+=1
    
        else:
            print "The market is not currently open\n-----------------------"
            time.sleep(900)
    else:
        print "It's the weekend!"
        time.sleep(1800)

