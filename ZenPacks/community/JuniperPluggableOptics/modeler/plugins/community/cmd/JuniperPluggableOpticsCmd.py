################################################################################
#
# This program is part of the JuniperPluggableOptics Zenpack for Zenoss.
# Copyright (C) 2014 Russell Dwarshuis
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""Log into a Juniper switch or router using ssh and issue commands
to locate pluggable optics modules.
"""

import re
import pprint
import xml.etree.ElementTree as ET
import string
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap




class JuniperPluggableOpticsCmd(CommandPlugin):
    """Map Juniper optical modules on intefaces to the python class for them.
Assumes data that looks like file sample_output.txt"""


    # The command to run.
    command = "show interfaces diagnostics optics | display xml\r"
    modname = "ZenPacks.community.JuniperPluggableOptics.JuniperPluggableOptics"
    relname = "cards"
    compname = "hw"


    def process(self, device, results, log):
        log.info("Starting process() for modeler JuniperPluggableOpticsCmd")

        # remove promp at end if necessary
        try:
            root = ET.fromstring(results)
        except ET.ParseError:
            log.debug('malformed XML found in JuniperPluggableOpticsCmd')
            return

        try:
            ns = re.match(r'({.*})',root[0].tag).group(0)
            rootns = string.replace(ns,'junos-interface','junos')
        except:
            log.debug("Unknown namespace in xml in JuniperPluggableOpticsCmd")
            return
        log.debug('found namespace %s', ns)

        rm = self.relMap()

        for physicalInterface in root[0]:
            try:
                intf = physicalInterface.find(ns + 'name').text
            except:
                log.debug("Can't find interface name")
                continue
            try:
                intfDiags = physicalInterface.find(ns + 'optics-diagnostics')
                try:
                    intfDiags.find(ns + 'laser-bias-current').text
                    om = self.objectMap()
                    om.id = self.prepId("%s %s" % (intf,'cmdMilliamps'))
                    om.title = intf + ' ' + 'Bias Current Sensor'
                    om.ifDescr = intf
                    om.entSensorType = 'cmdMilliamps'
                    rm.append(om)
                    log.info('Found Bias Current Sensor for %s' % intf)
                except:
                    log.debug('No Bias Current Sensor for %s' % intf)

                try:
                    intfDiags.find(ns + 'laser-output-power-dbm').text
                    om = self.objectMap()
                    om.id = self.prepId("%s %s" % (intf,'cmdTxDbm'))
                    om.title = intf + ' ' + 'Transmit Power Sensor'
                    om.ifDescr = intf 
                    om.entSensorType = 'cmdTxDbm'
                    rm.append(om)
                    log.info('Found Transmit Power Sensor for %s' % intf)
                except:
                    log.debug('No Transmit Power Sensor for %s' % intf)
                    
                try:
                    intfDiags.find(ns + 'module-temperature').\
                              attrib[rootns + 'celsius']
                    om = self.objectMap()
                    om.id = self.prepId("%s %s" % (intf,'cmdCelcius'))
                    om.title = intf + ' ' + 'Module Temperature Sensor'
                    om.ifDescr = intf
                    om.entSensorType = 'cmdCelcius'
                    rm.append(om)
                    log.info('Found Module Temperature Sensor for %s' % intf)
                except:
                    log.debug('No Module Temperature Sensor for %s' % intf)

                try:
                    intfDiags.find(ns + 'laser-rx-optical-power-dbm').text
                    om = self.objectMap()
                    om.id = self.prepId("%s %s" % (intf,'cmdRxDbm'))
                    om.title = intf + ' ' + 'Receive Power Sensor'
                    om.ifDescr = intf
                    om.entSensorType = 'cmdRxDbm'
                    rm.append(om)
                    log.info('Found Receive Power Sensor for %s' % intf)
                except:
                    log.debug('No Receive Power Sensor for %s' % intf)
            except:
                log.info('Error parsing optics-diagnostics xml in JuniperPluggableOpticsCmd')
                continue
        log.info(pprint.pformat(rm))
        return rm
