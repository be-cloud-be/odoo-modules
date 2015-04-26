# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from osv import fields, osv

import logging

_logger = logging.getLogger(__name__)

class BuildingLand(osv.osv):
    '''Building Land'''
    
    _columns = {

        'owner_id': fields.many2one('hr.employee', 'Manager'),                
        'address_id': fields.many2one('res.partner', 'Working Address'),
        'land_division':fields.char('Land Division', size = 20, help = "The land division reference."),
        'area':fields.integer('Sequence', size = 20, help = "Area in ares."),   
        
    }
BuildingLand()