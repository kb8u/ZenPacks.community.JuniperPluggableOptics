################################################################################
#
# This program is part of the JuniperPluggableOptics Zenpack for Zenoss.
# Copyright 2014 by Russell Dwarshuis, Merit Network, Inc.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""interfaces

describes the form field to the user interface.

"""

from Products.Zuul.interfaces import IThresholdInfo, IComponentInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IJuniperPluggableOpticsInfo(IComponentInfo):
    """
    Info adapter for JuniperPluggableOptics components.
    """
    description = schema.Text(
        title=u"Description", readonly=True, group='Overview')
