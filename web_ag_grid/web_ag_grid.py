# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from osv import fields, osv

import logging

_logger = logging.getLogger(__name__)

class view(osv.osv):

    _name = 'ir.ui.view'
    
    def __init__(self, cr, uid, name, context=None):
        super(view, self).__init__(cr, uid, name, context)
        option = ('ag_grid', 'AG Grid')
        type_selection = self._columns['type'].selection
        if option not in type_selection:
            type_selection.append(option)
    
view()