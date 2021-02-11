""" Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# Import Section
from flask import Flask, render_template, request
import datetime
import requests
import json
from dotenv import load_dotenv
import os

headers = dict()
headers['Content-Type'] = "application/json"
headers['Accept'] = "application/json"
base_url = "https://api.meraki.com/api/v1"

# load all environment variables
load_dotenv()

#Global variables
app = Flask(__name__)

#Methods
#Returns location and time of accessing device
def getSystemTimeAndLocation():
    #request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    #request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    location = geoData['country']
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    timeAndLocation = "System Information: {}, {} (Timezone: {})".format(location, current_time, timezone)

    return timeAndLocation

def meraki_api(uri, headers):
    response = requests.get(base_url+uri, headers=headers)
    return json.loads(response.text)

def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days

def plus_days(d, p):
    d = datetime.datetime.strptime(d, "%Y-%m-%d") + datetime.timedelta(days=p)
    return d.strftime("%Y-%m-%d")

##Routes
@app.route('/')
def get_key():
    try:
        #Page without error message and defined header links
        return render_template('login.html', hiddenLinks=False, timeAndLocation=getSystemTimeAndLocation())
    except Exception as e:
        print(e)
        #OR the following to show error message
        return render_template('login.html', error=False, errormessage=f"ERROR: {e}", errorcode=e, timeAndLocation=getSystemTimeAndLocation())

@app.route('/home', methods=['POST'])
def index():
    try:
        headers['X-Cisco-Meraki-API-Key'] = request.form.get("key")

        orgs = meraki_api('/organizations', headers)

        #Page without error message and defined header links
        return render_template('line.html', hiddenLinks=False, timeAndLocation=getSystemTimeAndLocation(), orgs=orgs)
    except Exception as e:
        print(e)
        #OR the following to show error message
        return render_template('line.html', error=False, errormessage=f"ERROR: {e}", errorcode=e, timeAndLocation=getSystemTimeAndLocation())

@app.route('/get_networks/<org_id>')
def get_networks(org_id):
    try:
        nets = meraki_api(f'/organizations/{org_id}/networks', headers)

        return json.dumps(nets)
    except Exception as e:
        print(e)

@app.route('/get_wireless_health/<net_id>/<t0>/<t1>')
def get_wireless_health(net_id, t0, t1):
    try:
        if days_between(t0, t1) <= 7:
            connStats = meraki_api(f'/networks/{net_id}/wireless/connectionStats?t0={t0}&t1={t1}', headers)
            failedConns = meraki_api(f'/networks/{net_id}/wireless/failedConnections?t0={t0}&t1={t1}', headers)

            failedClients = []
            for failedConn in failedConns:
                failedClients.append((failedConn['clientMac'], failedConn['failureStep'], failedConn['type']))
            connStats['failedClients'] = failedClients

            return json.dumps(connStats)

        else:
            aggConnStats = dict()
            aggConnStats['assoc'] = 0
            aggConnStats['auth'] = 0
            aggConnStats['dhcp'] = 0
            aggConnStats['dns'] = 0
            aggConnStats['success'] = 0
            aggConnStats['failedClients'] = []
            while days_between(t0, t1) > 0:
                if days_between(t0, t1) <= 6:
                    t = t1
                else:
                    t = plus_days(t0, 6)
                print(f"t0 {t0} t {t}")
                connStats = meraki_api(f'/networks/{net_id}/wireless/connectionStats?t0={t0}&t1={t}', headers)
                failedConns = meraki_api(f'/networks/{net_id}/wireless/failedConnections?t0={t0}&t1={t}', headers)

                print(f"connStats {connStats}")
                print(f"failedConns {failedConns}")
                aggConnStats['assoc'] += connStats['assoc']
                aggConnStats['auth'] += connStats['auth']
                aggConnStats['dhcp'] += connStats['dhcp']
                aggConnStats['dns'] += connStats['dns']
                aggConnStats['success'] += connStats['success']
                for failedConn in failedConns:
                    aggConnStats['failedClients'].append((failedConn['clientMac'], failedConn['failureStep'], failedConn['type']))

                t0 = t
            print(aggConnStats)

            return json.dumps(aggConnStats)

    except Exception as e:
        print(e)

#Main Function
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

