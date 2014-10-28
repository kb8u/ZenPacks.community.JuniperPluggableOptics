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


    def condition(self, device, log):
        if device.zCommandProtocol == 'ssh' and \
           device.zCommandPassword and \
           device.zCommandUsername:
            return True
        else:
            return False


    def process(self, device, results, log):
        log.info("Starting process() for modeler JuniperPluggableOpticsCmd")

        # parse XML
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
                # Must have one or more sensors, not just an interface name
                foundSensor = False
                try:
                    intfDiags.find(ns + 'laser-bias-current').text
                    foundSensor = True
                    log.info('Found Bias Current Sensor for %s' % intf)
                except:
                    log.debug('No Bias Current Sensor for %s' % intf)
                try:
                    intfDiags.find(ns + 'laser-output-power-dbm').text
                    foundSensor = True
                    log.info('Found Transmit Power Sensor for %s' % intf)
                except:
                    log.debug('No Transmit Power Sensor for %s' % intf)
                try:
                    intfDiags.find(ns + 'module-temperature').\
                              attrib[rootns + 'celsius']
                    foundSensor = True
                    log.info('Found Module Temperature Sensor for %s' % intf)
                except:
                    log.debug('No Module Temperature Sensor for %s' % intf)
                try:
                    intfDiags.find(ns + 'laser-rx-optical-power-dbm').text
                    foundSensor = True
                    log.info('Found Receive Power Sensor for %s' % intf)
                except:
                    log.debug('No Receive Power Sensor for %s' % intf)

                if foundSensor:
                    om = self.objectMap()
                    om.id = self.prepId(intf)
                    om.title = om.posName = intf + ' ' + 'Pluggable Optics'
                    om.intf = intf
                    om.monitor = True
                    rm.append(om)
            except:
                log.info('Error parsing optics-diagnostics xml in JuniperPluggableOpticsCmd')
                continue
        return rm
