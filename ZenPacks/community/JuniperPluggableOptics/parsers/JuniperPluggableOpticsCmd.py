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
to get stats from Juniper pluggable optics.  Command should be:
show interfaces diagnostics optics ${here/ifDescr} | display xml
"""

import re
import xml.etree.ElementTree as ET
import string
import logging
from Products.ZenRRD.CommandParser import CommandParser

log = logging.getLogger('.'.join(['zen', __name__]))

class JuniperPluggableOpticsCmd(CommandParser):

    def processResults(self, cmd, result):
        log.debug("Starting processResults() for JuniperPluggableOpticsCmd")

        # parse XML from command
        try:
            root = ET.fromstring(cmd.result.output)
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

        for physicalInterface in root[0]:
            od = {}
            try:
                intf = physicalInterface.find(ns + 'name').text
            except:
                log.debug("Can't find interface name")
                continue
            try:
                intfDiags = physicalInterface.find(ns + 'optics-diagnostics')
                try:
                    od['mA'] = intfDiags.find(ns + 'laser-bias-current').text
                    log.debug('Bias Current for %s: %s' % (intf,od['mA']))
                except:
                    log.debug('No Bias Current Sensor for %s' % intf)

                try:
                    od['OPTdbm'] = \
                        intfDiags.find(ns + 'laser-output-power-dbm').text
                    log.debug('Transmit Power for %s: %s' % (intf,od['OPTdbm']))
                except:
                    log.debug('No Transmit Power Sensor for %s' % intf)
                    
                try:
                    od['C'] = intfDiags.find(ns + 'module-temperature').\
                                        attrib[rootns + 'celsius']
                    log.debug('Module Temperature %s: %s' % (intf,od['C']))
                except:
                    log.debug('No Module Temperature Sensor for %s' % intf)

                try:
                    od['OPRdbm'] = \
                        intfDiags.find(ns + 'laser-rx-optical-power-dbm').text
                    log.debug('Receive Power for %s: %s' % (intf,od['OPRdbm']))
                except:
                    log.debug('No Receive Power Sensor for %s' % intf)
            except:
                log.debug('Error parsing optics-diagnostics xml in JuniperPluggableOpticsCmd')
                continue
            
            for dp in cmd.points:
                if dp.id in od:
                    result.values.append((dp,od[dp.id]))

        return result
