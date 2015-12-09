# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from openerp import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

class view(models.Model):

    _name = 'ir.ui.view'
    
    def __init__(self, pool, cr):
        init_res = super(Users, self).__init__(pool, cr)
        option = ('ag_grid', 'AG Grid')
        type_selection = self._columns['type'].selection
        if option not in type_selection:
            type_selection.append(option)
    
view()