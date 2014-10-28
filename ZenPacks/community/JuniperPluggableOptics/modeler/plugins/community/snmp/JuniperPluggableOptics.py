################################################################################
#
# This program is part of the JuniperPluggableOptics Zenpack for Zenoss.
# Copyright (C) 2013 Russell Dwarshuis
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__=\
"""Walk jnxDomCurrentTable to find pluggable optics modules for temperature,
bias current, transmit and receive optical power.  Walk ifName for interface
name."""

import re
from Products.DataCollector.plugins.CollectorPlugin \
    import SnmpPlugin, GetTableMap
from pprint import pprint


class JuniperPluggableOptics(SnmpPlugin):
    "Map Juniper pluggable optics on intefaces to the python class for them"

    modname = "ZenPacks.community.JuniperPluggableOptics.JuniperPluggableOptics"
    relname = "cards"
    compname = "hw"

    snmpGetTableMaps = ( GetTableMap('ifEntry',
                                     '1.3.6.1.2.1.2.2.1',
                                     { '.2' : 'ifDescr' }
                                    ),
                         GetTableMap('jnxDomCurrentEntry',
                                     '1.3.6.1.4.1.2636.3.60.1.1.1.1',
                                     { '.5' : 'rxLaserPower',
                                       '.6' : 'txLaserBiasCurrent',
                                       '.7' : 'txLaserOutputPower',
                                       '.8' : 'moduleTemperature' }
                                    ),
                       )

    def process(self, device, results, log):
        """
Run SNMP queries, process returned values, find Juniper PluggableOptics sensors
        """
        log.info('Starting process() for modeler JuniperPluggableOpticsMap')

        getdata, tabledata = results
        rm = self.relMap()

        # build dictionary of ifDescr,index
        ifDescrs = {}
        for index, ifDescr in tabledata.get("ifEntry").iteritems():
            ifDescrs[ifDescr['ifDescr']] = index

        if not ifDescrs:
            log.info('No ifDescrs found in ifEntry SNMP table')
            return

        jnxDomCurrentEntry = tabledata.get('jnxDomCurrentEntry')
        if not jnxDomCurrentEntry:
            log.info('No data returned from jnxDomCurrentEntry SNMP table')
            return
        # iterate over ifDescr to find matching sensors
        for ifDescr, ifIndex in ifDescrs.iteritems():
            if ifIndex in jnxDomCurrentEntry:
                log.info('Found sensors on %s' % ifDescr)
                om = self.objectMap()
                om.id = self.prepId(ifDescr)
                om.title = om.posName = ifDescr + ' ' + 'Pluggable Optics'
                om.intf = ifDescr
                om.snmpindex = int(ifIndex.strip('.'))
                om.monitor = True
                rm.append(om)

        return rm
