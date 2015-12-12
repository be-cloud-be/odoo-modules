# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from openerp import api, fields, models, _

from openerp.addons.base.ir.ir_actions import VIEW_TYPES

import logging

_logger = logging.getLogger(__name__)

VIEW_TYPE = ('ag_grid', _('AG Grid'))
VIEW_TYPES.append(VIEW_TYPE)

class view(models.Model):

    _name = 'ir.ui.view'
    _inherit = ["ir.ui.view"]
    
    type = fields.Selection(selection_add=[('ag_grid', 'AG Grid')])
    
view()