#!/usr/bin/env python
import sys
import Globals
import yaml
from operator import itemgetter

hubLookup = {
    '205.153.31.150': 'IMAX-ZNS-HUB-001.inframax.ncare',
    '205.153.31.151': 'IMAX-ZNS-HUB-002.inframax.ncare',
    '205.153.31.152': 'IMAX-ZNS-HUB-003.inframax.ncare',
    '205.153.31.153': 'IMAX-ZNS-HUB-004.inframax.ncare',
    '205.153.31.154': 'IMAX-ZNS-HUB-005.inframax.ncare',
    '205.153.31.155': 'IMAX-ZNS-HUB-006.inframax.ncare',
    '205.153.31.156': 'IMAX-ZNS-HUB-007.inframax.ncare',
    '205.153.31.157': 'IMAX-ZNS-HUB-008.inframax.ncare',
    '205.153.31.158': 'IMAX-ZNS-HUB-009.inframax.ncare',
    '205.153.31.159': 'IMAX-ZNS-HUB-010.inframax.ncare'
}

def resolveHostname(hname):
    import socket
    return socket.gethostbyname(hname)

from Products.ZenUtils.ZenScriptBase import ZenScriptBase
dmd = ZenScriptBase(connect=True).dmd

header = ['collectorName', 'collectorIP', 'hubIP']
collectorList = []
for hub in dmd.Monitors.Hub.getHubs():
    for collector in hub.collectors():
        collectorDict = {}
        collectorDict['collectorName'] = collector.id
        collectorDict['collectorIP'] = collector.hostname
        collectorDict['hubIP'] = resolveHostname(hub.hostname)
        # if needed, convert hub IP to FQDN
        hubFQDN = hubLookup.get(hub.hostname, hub.hostname)
        collectorDict['hubhost'] = hubFQDN.replace('.inframax.local', '.inframax.ncare')
        collectorList.append(collectorDict)
sortedList = sorted(collectorList, key=itemgetter('collectorName'))
with open('collectors.yaml', 'w') as outfile:
    outfile.write( yaml.dump(sortedList, default_flow_style=False) )
print "ANSIBLE OUTPUT"
for item in collectorList:
    aname=item['collectorName'].replace('.', '-') + ".inframax.ncare"
    aip="ansible_ssh_host=" + item['collectorIP']
    auser="ansible_ssh_user=root"
    hubhost="hubhost=" + item['hubhost']
    print " ".join([aname, aip, auser, "namespace=NCARE", hubhost])
