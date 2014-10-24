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
    posName = 'Not set by modeler'
    intf = 'Not set by modeler'

    _properties = (
        {'id': 'posName', 'type':'string', 'mode':''},
        {'id': 'intf', 'type':'string', 'mode':''},
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
        return self.title
    name = viewName

    def getRRDTemplateName(self):
        if self.device().zCommandProtocol == 'ssh' and \
           self.device().zCommandPassword and \
           self.device().zCommandUsername:
            return 'JuniperPluggableOpticsSensorSsh'
        else:
            return 'JuniperPluggableOpticsSensorSnmp'

    def manage_deleteComponent(self, REQUEST=None):
        """
        Delete Component
        """
        self.getPrimaryParent()._delObject(self.id)
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.device().hw.absolute_url())


InitializeClass(JuniperPluggableOptics)

