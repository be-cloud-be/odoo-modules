# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class BuildingLand(models.Model):
    '''Building Land'''
    _name = 'property_managemnt.building_land'
        
    owner_id = fields.Many2one('res.partner', string = 'The land owner.')
    address_id = fields.Many2one('res.partner', string = 'The land address')
    land_division = fields.Char(string = "The land division reference.")
    size = fields.Integer(string = "Size in ares.")   
    price = fields.Integer(string = "Size in ares.")  
        
BuildingLand()