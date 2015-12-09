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
    
    type = fields.Selection(selection_add=[('ag_grid', 'AG Grid')])
    
view()