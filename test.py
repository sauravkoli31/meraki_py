import requests
import csv
from time import strftime
import datetime
import psycopg2
from config import config
weekday = datetime.datetime.now().isoweekday()

file = open("serial.csv","r")

data = csv.reader(file)
timestamp_now = strftime("%H%M%S")

#Login URL for Cisco Meraki
LURL = 'https://account.meraki.com/login/login'

#Payload(Cisco Meraki Username and Password)
payload = {
    'email': 'email',
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

    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        print('Successfully Connected to the database')
        #iterating through all the serial numbers and sending get request
        for serial_number in data:
            print("Fetching Data for " + serial_number[0])
            # Pull data URL
            Request_URL = 'https://n240.meraki.com/api/v0/devices/'+serial_number[0]+'/clients?timespan=3600'
            rawdata = session.get(Request_URL)
            json_data = rawdata.json()
            client_count = len(json_data)
            sent, recv = 0, 0
            for items in json_data:
                sent += items['usage']['sent']
                recv += items['usage']['recv']
                network_id = items['id']

            print("Connected Clients for (" + serial_number[0] + ") : [" + str(client_count)+"]    ---------------------------- Sent : "+str(sent) + " KB, Received : "+str(recv)+" KB")

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            reformatdata = [serial_number[0],client_count,recv,sent,timestamp_now,weekday]
            cur.execute("""INSERT INTO livedata(device_sn,client_count,sent_data,recv_data,timestamp,dow ) VALUES (%s,%s,%s,%s,%s,%s)""",(reformatdata))
            conn.commit()
            print("Commited to Database")
            # close the communication with the PostgreSQL
            cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
