import requests
import csv
import json

file = open("serial.csv","r")
sent = 0
recv = 0

data = csv.reader(file)

#Login URL for Cisco Meraki
LURL = 'https://account.meraki.com/login/login'

#Payload(Cisco Meraki Username and Password)
payload = {
    'email': 'username',
    'password': 'password'
}
print("CISCO MERAKI - Trying to Log IN")
print("Please wait")
print("-----------------------------------------------------------------")

#Session Code
with requests.Session() as session:
    post = session.post(LURL, data=payload)
    print("CISCO MERAKI - Logged in Successfully")
    print("-----------------------------------------------------------------")

#iterating through all the serial numbers and sending get request
for sn in data:
    print("Fetching Data for " + sn[0])
    # Pull data URL
    RURL = 'https://n240.meraki.com/api/v0/devices/'+sn[0]+'/clients?timespan=3600'
    r = session.get(RURL)
    j_data = r.json()
    count = len(j_data)
    sent, recv = 0, 0
    for val in j_data:
        sent += val['usage']['sent']/1048576
        recv += val['usage']['recv']/1048576

    sentcul = sent/1048576
    print("Connected Clients for (" + sn[0] + ") : [" + str(count)+"]    ---------------------------- Sent : "+str(sent) + " GB, Received : "+str(recv)+" GB")
