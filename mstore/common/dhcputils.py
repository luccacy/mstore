# 
# dhcpd_leases_parser.py
#
# Copyright 2008, Paul McGuire
#
# Sample parser to parse a dhcpd.leases file to extract leases 
# and lease attributes
#
# format ref: http://www.linuxmanpages.com/man5/dhcpd.leases.5.php
#
import os
from pyparsing import *
import datetime,time
from mstore.common import logger

LOG = logger.get_logger(__name__)

LBRACE,RBRACE,SEMI,QUOTE = map(Suppress,'{};"')
ipAddress = Combine(Word(nums) + ('.' + Word(nums))*3)
hexint = Word(hexnums,exact=2)
macAddress = Combine(hexint + (':'+hexint)*5)
hdwType = Word(alphanums)

yyyymmdd = Combine((Word(nums,exact=4)|Word(nums,exact=2))+
                    ('/'+Word(nums,exact=2))*2)
hhmmss = Combine(Word(nums,exact=2)+(':'+Word(nums,exact=2))*2)
dateRef = oneOf(list("0123456"))("weekday") + yyyymmdd("date") + \
                                                        hhmmss("time")

def utcToLocalTime(tokens):
    utctime = datetime.datetime.strptime("%(date)s %(time)s" % tokens,
                                                    "%Y/%m/%d %H:%M:%S")
    localtime = utctime-datetime.timedelta(0,time.timezone,0)
    tokens["utcdate"],tokens["utctime"] = tokens["date"],tokens["time"]
    tokens["localdate"],tokens["localtime"] = str(localtime).split()
    del tokens["date"]
    del tokens["time"]
dateRef.setParseAction(utcToLocalTime)

startsStmt = "starts" + dateRef + SEMI
endsStmt = "ends" + (dateRef | "never") + SEMI
tstpStmt = "tstp" + dateRef + SEMI
tsfpStmt = "tsfp" + dateRef + SEMI
clttStmt = "cltt" + dateRef + SEMI
hdwStmt = "hardware" + hdwType("type") + macAddress("mac") + SEMI
uidStmt = "uid" + QuotedString('"')("uid") + SEMI
bindingStmt = "binding" + Word(alphanums) + Word(alphanums) + SEMI

leaseStatement = startsStmt | endsStmt | tstpStmt | tsfpStmt | clttStmt | hdwStmt | \
                                                        uidStmt | bindingStmt
leaseDef = "lease" + ipAddress("ipaddress") + LBRACE + \
                            Dict(ZeroOrMore(Group(leaseStatement))) + RBRACE

def get_dhcpd_ips():
    DHCPD_LEASE_FILE='/var/lib/dhcpd/dhcpd.leases'
    ips = {}

    if not os.path.exists(DHCPD_LEASE_FILE):
        raise 'Not found dhcp lease file : %s' % DHCPD_LEASE_FILE
    try:
        with open(DHCPD_LEASE_FILE, 'r') as fp:
            fcontext = fp.read()

        if fcontext is not None:
            for lease in leaseDef.searchString(fcontext):
                ips[lease.ipaddress] = lease.hardware.mac

        return ips

    except Exception ,e:
        LOG.error('failed to read dhcp lease file : %s', e)
        raise 'failed to read dhcpd lease file'

