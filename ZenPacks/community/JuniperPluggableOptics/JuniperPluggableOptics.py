################################################################################
#
# This program is part of the JuniperPluggableOptics Zenpack for Zenoss.
# Copyright (C) 2014 Russell Dwarshuis
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""JuniperPluggableOptics

JuniperPluggableOptics is used to measure temperature, supply voltage, bias
current, transmit power and receiver power on Juniper pluggable optical
modules.
"""

from Globals import DTMLFile
from Globals import InitializeClass

from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_VIEW, ZEN_CHANGE_SETTINGS, ZEN_VIEW_HISTORY

from Products.ZenModel.ExpansionCard import ExpansionCard

import logging
log = logging.getLogger('JuniperPluggableOptics')


class JuniperPluggableOptics(ExpansionCard, ManagedEntity):
    """JuniperPluggableOptics object"""

    portal_type = meta_type = 'JuniperPluggableOptics'

    # set default _properties
    ifDescr = 'Not set by modeler'   # from IF-MIB ifEntry table
    physDescr = 'Not set by modeler' # entPhysicalDescr from entPhysicalTable
    # the following are from the entSensorValues table
    entSensorType = 'unknown' # like amperes, celsius, dBm, voltsDC

    _properties = (
        {'id': 'ifDescr', 'type':'string', 'mode':''},
        {'id': 'physDescr', 'type':'string', 'mode':''},
        {'id': 'entSensorType','type': 'string','mode':''},
    )

    factory_type_information = (
        {
            'id'             : 'JuniperPluggableOptics',
            'meta_type'      : 'JuniperPluggableOptics',
            'description'    : 'Sensor monitoring of optical modules',
            'product'        : 'ZenModel',
            'factory'        : 'manage_addJuniperPluggableOptics',
            'immediate_view' : 'viewJuniperPluggableOptics',
            'actions'        :
            (
                { 'id'            : 'status'
                , 'name'          : 'Status'
                , 'action'        : 'viewJuniperPluggableOptics'
                , 'permissions'   : (ZEN_VIEW)
                },
                { 'id'            : 'perfConf'
                , 'name'          : 'Template'
                , 'action'        : 'objTemplates'
                , 'permissions'   : (ZEN_CHANGE_SETTINGS)
                },
                { 'id'            : 'viewHistory'
                , 'name'          : 'Modifications'
                , 'action'        : 'viewHistory'
                , 'permissions'   : (ZEN_VIEW_HISTORY)
                },
            )
          },
        )

    def viewName(self):
        return self.physDescr
    name = viewName

    def getRRDTemplateName(self):
        if self.device().zCommandProtocol == 'ssh':
            return 'JuniperPluggableOpticsSensorSsh' \
                + self.entSensorType.capitalize()
        else:
            return 'JuniperPluggableOpticsSensor' + self.entSensorType.capitalize()

    def manage_deleteComponent(self, REQUEST=None):
        """
        Delete Component
        """
        self.getPrimaryParent()._delObject(self.id)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.device().hw.absolute_url())


InitializeClass(JuniperPluggableOptics)

