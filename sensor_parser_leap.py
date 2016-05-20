#!/usr/bin/env python
import urllib2
import re
import time
import json
import httplib
# Lists for differential
leftright = []
sumright = []
sumleft = []
sumrear = []
sumfront = []
P1FSUM = []
P1RSUM = []
P2FSUM = []
P2RSUM = []
P3FSUM = []
P3RSUM = []
P4FSUM = []
P4RSUM = []
P5FSUM = []
P5RSUM = []

# lists for average values
FLlist = []
FRlist = []
RRlist = []
RLlist = []
P1list = []
P2list = []
P3list = []
P4list = []
P5list = []
P1_F_avglist = []
P2_F_avglist = []
P3_F_avglist = []
P4_F_avglist = []
P5_F_avglist = []
P1_R_avglist = []
P2_R_avglist = []
P3_R_avglist = []
P4_R_avglist = []
P5_R_avglist = []
leftright = []
sumright = []
sumleft = []
resultarray= []
mydict = {}
sensorlist=[]
sensordict = {}
opentsdb_data1 = []
key = 0
values = 1
ts = time.time()
container = []
prev_ts = 0
measure_every = 2 #seconds. Don't set this veriable to less than 1.
vaguino_temperatures_url = "http://192.168.1.100/temp"
logfile = "parser.log"

try:
        while(1):
                ts = time.time()

                if (ts - prev_ts < measure_every):
                        time.sleep(measure_every - (ts - prev_ts))
                        ts = time.time()

                opentsdb_data = []
                with open(logfile, 'a') as logger:
                        log_message = ""
                        try:

                                arduino_response = urllib2.urlopen(vaguino_temperatures_url, timeout = 10)
                                for line in arduino_response.read().split('<br>'):
                                    r = re.findall('(.*)=(.*)\s+', line)    
                                    if (r):         
                                        container.append(r)
                                     
                                    z = re.findall('(.*)=(.*)\s+', line)
                                    
                                    if (z):
                                        sensorlist.append(z)
                                for item in sensorlist:
                                
                                
                                    sensordict.update(item)
                                allsensor_leap = open('sensordata.txt', 'a')     
                                for key, value in sensordict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                        stringvar = "%s \n" %(value)
                                        
                                        allsensor_leap.write(stringvar)
                                       
                                                
                                        #print z
                                        sensor_description = key
                                        value = value
                                        data = {}
                                        data['metric'] = 'serverrack.sensors.temp'
                                        data['timestamp'] = ts
                                        data['value'] = value
                                        data['tags'] = {}
                                        data['tags']['sensor_description'] = sensor_description
                                        opentsdb_data1.append(data)
                                #print opentsdb_data1
                                httpServ = httplib.HTTPConnection("128.39.120.212", 4242)
                                httpServ.connect()

                                http_headers = {'Content-Type': 'application/json; charset=UTF-8'}
                                json_data = json.dumps(opentsdb_data1)
                                #print json.dumps(opentsdb_data, indent=4, sort_keys=True)
                                httpServ.request('POST', '/api/put', json_data, http_headers)
                                response = httpServ.getresponse()
                                if response.status == 204:
                                        log_message = "{0}: Data has been stored succesfully".format(time.ctime(ts))

                                else:
                                        log_message = "{0}: An error occured. Response code {1}".format(time.ctime(ts), response.status)
                                        #print(response.read())

                                httpServ.close()

                        #except urllib2.URLError:
                                # If the URL cannot be reached, ignore this error and retry.
                                log_message = "{0}: The URL '{1}' could not be reached..".format(time.ctime(ts), vaguino_temperatures_url)

                                     
                                #print container
                                #print opentsdb_data1
                                for element in container:
                                    mydict.update(element)
                                    
                                
                               
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a = re.findall('(FR),(.*)\s+', stringvar)
                                    if (a):
                                        FRlist.append(float(value))
                                sensor_description = 'FR_Average'
                                FR = sum(FRlist) / float(len(FRlist))
                                value = FR
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    b = re.findall('(FL),(.*)\s+', stringvar)
                                    if (b):
                                        FLlist.append(float(value))
                               
                                sensor_description = 'FL_Average'
                                FL = sum(FLlist) / float(len(FLlist))
                                value = FL
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    c = re.findall('(RR),(.*)\s+', stringvar)
                                    if (c):
                                        RRlist.append(float(value))
                                sensor_description = 'RR_Average'
                                RR = sum(RRlist) / float(len(RRlist))
                                value = RR
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    d = re.findall('(RL),(.*)\s+', stringvar)
                                    if (d):
                                        RLlist.append(float(value))
                                sensor_description = 'RL_Average'
                                RL = sum(RRlist) / float(len(RLlist))
                                value = RL
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                #print opentsdb_data
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                   
                                    
                                    
                                    stringvar = "%s,%s " %(key,value)
                                    e = re.findall('(P1_[A-Z]{2}),(.*)\s+', stringvar)
                                    if (e):
                                        P1list.append(float(value))
                                sensor_description = 'P1_avg'
                                P1 = sum(P1list) / float(len(P1list))
                                
                                P1_leap = open('P1.AVG_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(P1)
                                P1_leap.write(leapstring)
                                   
                                value = P1
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    f = re.findall('(P2_[A-Z]{2}),(.*)\s+', stringvar)
                                    if (f):
                                        P2list.append(float(value))
                                sensor_description = 'P2_avg'
                                P2 = sum(P2list) / float(len(P2list))
                                
                                P2_leap = open('P2.AVG_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(P2)
                                P2_leap.write(leapstring)
                                value = P2
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    g = re.findall('(P3_[A-Z]{2}),(.*)\s+', stringvar)
                                    if (g):
                                        P3list.append(float(value))
                                sensor_description = 'P3_avg'
                                P3 = sum(P3list) / float(len(P3list))
                                
                                P3_leap = open('P3.AVG_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(P3)
                                P3_leap.write(leapstring)
                                
                                value = P3
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                               
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    h = re.findall('(P4_[A-Z]{2}),(.*)\s+', stringvar)
                                    if (h):
                                        P4list.append(float(value))
                                sensor_description = 'P4_avg'
                                P4 = sum(P4list) / float(len(P4list))
                                
                                P4_leap = open('P4.AVG_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(P4)
                                P4_leap.write(leapstring)
                                
                                value = P4
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    i = re.findall('(P5_[A-Z]{2}),(.*)\s+', stringvar)
                                    if (i):
                                        P5list.append(float(value))
                                sensor_description = 'P5_avg'
                                P5 = sum(P5list) / float(len(P5list))
                                
                                P5_leap = open('P5.AVG_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(P5)
                                P5_leap.write(leapstring)
                                
                                value = P5
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    j = re.findall('(P1_F[A-Z{R|L}]),(.*)\s', stringvar)

                                    if (j):
                                        P1_F_avglist.append(float(value))
                                sensor_description = 'P1_FRONT_AVG'
                                P1_FRONT_AVG = sum(P1_F_avglist) / float(len(P1_F_avglist))
                                value = P1_FRONT_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    j2 = re.findall('(P2_F[A-Z{R|L}]),(.*)\s', stringvar)

                                    if (j2):
                                        P2_F_avglist.append(float(value))
                                sensor_description = 'P2_FRONT_AVG'
                                P2_FRONT_AVG = sum(P2_F_avglist) / float(len(P2_F_avglist))
                                value = P2_FRONT_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    j3 = re.findall('(P3_F[A-Z{R|L}]),(.*)\s', stringvar)

                                    if (j3):
                                        P3_F_avglist.append(float(value))
                                sensor_description = 'P3_FRONT_AVG'
                                P3_FRONT_AVG = sum(P3_F_avglist) / float(len(P3_F_avglist))
                                value = P3_FRONT_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    j4 = re.findall('(P4_F[A-Z{R|L}]),(.*)\s', stringvar)

                                    if (j4):
                                        P4_F_avglist.append(float(value))
                                sensor_description = 'P4_FRONT_AVG'
                                P4_FRONT_AVG = sum(P4_F_avglist) / float(len(P4_F_avglist))
                                value = P4_FRONT_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    j5 = re.findall('(P5_F[A-Z{R|L}]),(.*)\s', stringvar)

                                    if (j5):
                                        P5_F_avglist.append(float(value))
                                sensor_description = 'P5_FRONT_AVG'
                                P5_FRONT_AVG = sum(P5_F_avglist) / float(len(P5_F_avglist))
                                value = P5_FRONT_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                            
                                #print opentsdb_data
                                httpServ = httplib.HTTPConnection("128.39.120.212", 4242)
                                httpServ.connect()

                                http_headers = {'Content-Type': 'application/json; charset=UTF-8'}
                                json_data = json.dumps(opentsdb_data)
                                #print json.dumps(opentsdb_data, indent=4, sort_keys=True)
                                httpServ.request('POST', '/api/put', json_data, http_headers)
                                response = httpServ.getresponse()
                                if response.status == 204:
                                        log_message = "{0}: Data has been stored succesfully".format(time.ctime(ts))

                                else:
                                        log_message = "{0}: An error occured. Response code {1}".format(time.ctime(ts), response.status)
                                        #print(response.read())

                                httpServ.close()

                        #except urllib2.URLError:
                                # If the URL cannot be reached, ignore this error and retry.
                                log_message = "{0}: The URL '{1}' could not be reached..".format(time.ctime(ts), vaguino_temperatures_url)

                
                                opentsdb_data = []
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a = re.findall('(P1_R[A-Z{R|L}]),(.*)\s', stringvar)
                                    if (a):
                                        P1_R_avglist.append(float(value))
                                sensor_description = 'P1_REAR_AVG'
                                P1_REAR_AVG = sum(P1_R_avglist) / float(len(P1_R_avglist))
                                value = P1_REAR_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a2 = re.findall('(P2_R[A-Z{R|L}]),(.*)\s', stringvar)
                                    if (a2):
                                        P2_R_avglist.append(float(value))
                                sensor_description = 'P2_REAR_AVG'
                                P2_REAR_AVG = sum(P2_R_avglist) / float(len(P2_R_avglist))
                                value = P2_REAR_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a3 = re.findall('(P3_R[A-Z{R|L}]),(.*)\s', stringvar)
                                    if (a3):
                                        P3_R_avglist.append(float(value))
                                sensor_description = 'P3_REAR_AVG'
                                P3_REAR_AVG = sum(P3_R_avglist) / float(len(P3_R_avglist))
                                value = P3_REAR_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a4 = re.findall('(P4_R[A-Z{R|L}]),(.*)\s', stringvar)
                                    if (a4):
                                        P4_R_avglist.append(float(value))
                                sensor_description = 'P4_REAR_AVG'
                                P4_REAR_AVG = sum(P4_R_avglist) / float(len(P4_R_avglist))
                                value = P4_REAR_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a5 = re.findall('(P5_R[A-Z{R|L}]),(.*)\s', stringvar)
                                    if (a5):
                                        P5_R_avglist.append(float(value))
                                sensor_description = 'P5_REAR_AVG'
                                P5_REAR_AVG = sum(P5_R_avglist) / float(len(P5_R_avglist))
                                value = P5_REAR_AVG
                                data = {}
                                data['metric'] = 'average.values.sensors'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                #print opentsdb_data
                                #print opentsdb_data
                                
                                
                            
                                httpServ = httplib.HTTPConnection("128.39.120.212", 4242)
                                httpServ.connect()

                                http_headers = {'Content-Type': 'application/json; charset=UTF-8'}
                                json_data = json.dumps(opentsdb_data)
                                #print json.dumps(opentsdb_data, indent=4, sort_keys=True)
                                httpServ.request('POST', '/api/put', json_data, http_headers)
                                response = httpServ.getresponse()
                                if response.status == 204:
                                        log_message = "{0}: Data has been stored succesfully".format(time.ctime(ts))

                                else:
                                        log_message = "{0}: An error occured. Response code {1}".format(time.ctime(ts), response.status)
                                httpServ.close()

                        #except urllib2.URLError:
                                # If the URL cannot be reached, ignore this error and retry.
                                log_message = "{0}: The URL '{1}' could not be reached..".format(time.ctime(ts), vaguino_temperatures_url)

                                
                                opentsdb_data = []
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    a = re.findall('([A-Z_{4}]L),(.*)\s', stringvar)
                                    #a1 = re.findall('([A-Z_{4}]R),(.*)\s', stringvar)
                                    if (a):
                                        sumleft.append(float(value))
                                    a1 = re.findall('([A-Z_{4}]R),(.*)\s', stringvar)   
                                    if (a1):
                                        sumright.append(float(value))
                                leftsum = sum(sumleft) / float(len(sumleft))
                                rightsum = sum(sumright) / float(len(sumright))
                                diffLR  = rightsum - leftsum
                                abs(diffLR)
                                #print diffLR
                                DIFFLR_leap = open('DIFFLR_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(diffLR)
                                DIFFLR_leap.write(leapstring)
                                
                                #print diffLR
                                sensor_description = 'RIGHT/LEFT_DIFF'
                                value = abs(diffLR)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    b = re.findall('([A-Z_{3}]F[R|L]),(.*)\s', stringvar)
                                    #a1 = re.findall('([A-Z_{4}]R),(.*)\s', stringvar)
                                    if (b):
                                        sumfront.append(float(value))
                                    b1 = re.findall('([A-Z_{3}]R[R|L]),(.*)\s', stringvar) 
                                    if (b1):
                                        sumrear.append(float(value))
                                frontsum = sum(sumfront) / float(len(sumfront))
                                rearsum = sum(sumrear) / float(len(sumrear))
                                frontbackdiff = rearsum - frontsum
                                abs(frontbackdiff)
                                
                                DIFF_Front_back_leap = open('DIFF_Front_back_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(frontbackdiff)
                                DIFF_Front_back_leap.write(leapstring)
                                
                                
                                sensor_description = 'FRONT/BACK_DIFF'
                                value = abs(frontbackdiff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    c = re.findall('(P1_F[A-Z]{1}),(.*)\s', stringvar)

                                    if (c):
                                        P1FSUM.append(float(value))
                                    c1 = re.findall('(P1_R[A-Z]{1}),(.*)\s', stringvar) 
                                    if (c1):
                                        P1RSUM.append(float(value))
                                P1diff = sum(P1RSUM) - sum(P1FSUM)
                                sensor_description = 'Plane1_DIFF'
                                value = abs(P1diff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    d = re.findall('(P2_F[A-Z]{1}),(.*)\s', stringvar)

                                    if (d):
                                        P2FSUM.append(float(value))
                                    d1 = re.findall('(P2_R[A-Z]{1}),(.*)\s', stringvar) 
                                    if (d1):
                                        P2RSUM.append(float(value))
                                P2diff = sum(P2RSUM) - sum(P2FSUM)
                                sensor_description = 'Plane2_DIFF'
                                value = abs(P2diff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    e = re.findall('(P3_F[A-Z]{1}),(.*)\s', stringvar)

                                    if (e):
                                        P3FSUM.append(float(value))
                                    e1 = re.findall('(P3_R[A-Z]{1}),(.*)\s', stringvar) 
                                    if (e1):
                                        P3RSUM.append(float(value))
                                P3diff = sum(P3RSUM) - sum(P3FSUM)
                                sensor_description = 'Plane3_DIFF'
                                value = abs(P3diff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    f = re.findall('(P4_F[A-Z]{1}),(.*)\s', stringvar)

                                    if (f):
                                        P4FSUM.append(float(value))
                                    f1 = re.findall('(P4_R[A-Z]{1}),(.*)\s', stringvar) 
                                    if (f1):
                                        P4RSUM.append(float(value))
                                P4diff = sum(P4RSUM) - sum(P4FSUM)
                                sensor_description = 'Plane4_DIFF'
                                value = abs(P4diff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                for key, value in mydict.iteritems():  ## loop through they dictiniary. iteriitems is needed to loop through values andn ot only key.
                                    #print key, value
                                    stringvar = "%s,%s " %(key,value)
                                    g = re.findall('(P5_F[A-Z]{1}),(.*)\s', stringvar)

                                    if (g):
                                        P5FSUM.append(float(value))
                                    g1 = re.findall('(P5_R[A-Z]{1}),(.*)\s', stringvar) 
                                    if (g1):
                                        P5RSUM.append(float(value))
                                P5diff = sum(P5RSUM) - sum(P5FSUM)
                                sensor_description = 'Plane5_DIFF'
                                value = abs(P5diff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                Ftopbotdiff= sum(P5FSUM) - sum(P1FSUM)
                                
                                ftopbot_leap = open('diff_ftopbot_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(Ftopbotdiff)
                                ftopbot_leap.write(leapstring)
                                
                                
                                sensor_description = 'FRONT_TOP/BOT_DIFF'
                                value = abs(Ftopbotdiff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                
                                Rtopbotdiff= sum(P5RSUM) - sum(P1RSUM)
                                
                                rtopbot_leap = open('diff_rtopbot_leapdetection.txt', 'a')
                                leapstring = "%s \n" %(Rtopbotdiff)
                                rtopbot_leap.write(leapstring)
                                
                                sensor_description = 'REAR_TOP/BOT_DIFF'
                                value = abs(Ftopbotdiff)
                                data = {}
                                data['metric'] = 'rack.differantials.temp'
                                data['timestamp'] = ts
                                data['value'] = value
                                data['tags'] = {}
                                data['tags']['sensor_description'] = sensor_description
                                opentsdb_data.append(data)
                                #print opentsdb_data
                                httpServ = httplib.HTTPConnection("128.39.120.212", 4242)
                                httpServ.connect()

                                http_headers = {'Content-Type': 'application/json; charset=UTF-8'}
                                json_data = json.dumps(opentsdb_data)
                                #print json.dumps(opentsdb_data, indent=4, sort_keys=True)
                                httpServ.request('POST', '/api/put', json_data, http_headers)
                                response = httpServ.getresponse()
                                if response.status == 204:
                                        log_message = "{0}: Data has been stored succesfully".format(time.ctime(ts))

                                else:
                                        log_message = "{0}: An error occured. Response code {1}".format(time.ctime(ts), response.status)
                                httpServ.close()
                                
                                
                        except urllib2.URLError:
                                # If the URL cannot be reached, ignore this error and retry.
                                log_message = "{0}: The URL '{1}' could not be reached..".format(time.ctime(ts), vaguino_temperatures_url)


                        print log_message
                        logger.write(log_message + '\n')

                prev_ts = ts
                opentsdb_data = []
                opentsdb_data1 = []
                FLlist = []
                FRlist = []
                RRlist = []
                RLlist = []
                P1list = []
                P2list = []
                P3list = []
                P4list = []
                P5list = []
                P1_F_avglist = []
                P2_F_avglist = []
                P3_F_avglist = []
                P4_F_avglist = []
                P5_F_avglist = []
                P1_R_avglist = []
                P2_R_avglist = []
                P3_R_avglist = []
                P4_R_avglist = []
                P5_R_avglist = []
                
                leftright = []
                sumright = []
                sumleft = []
                sumrear = []
                sumfront = []
                P1FSUM = []
                P1RSUM = []
                P2FSUM = []
                P2RSUM = []
                P3FSUM = []
                P3RSUM = []
                P4FSUM = []
                P4RSUM = []
                P5FSUM = []
                P5RSUM = []
except KeyboardInterrupt:
        print "\nStopping data collection..."
        exit(0)

