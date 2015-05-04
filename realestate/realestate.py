# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

## Add real estate information to CRM Lead.
class crm_lead (models.Model):
    """ CRM Lead with Real Estate Extension """
    _name = "crm.lead"
    _description = "Lead/Opportunity"
    _inherit = {'crm.lead'}
    
    type_of_lead = fields.Selection(selection = [ ('acquisition','Acquisition'), ('sale','Sale'), ], string = 'Type of lead', help="Type of lead is used to separate Acquisition and Sales")
    
    item_of_interest_id = fields.Many2one('realestate.building_land', string='Item of Interest', ondelete='set null', track_visibility='onchange',
            select=True, help="Linked item of interest (optional). Usually created when converting the lead.")

    def default_get(self, fields):
        res = super(crm_lead, self).default_get(fields)
        context = self.env.context        
        if(context['type_of_lead']):
            res['type_of_lead'] = context['type_of_lead']
        return res

crm_lead()

class building_land(models.Model):
    '''Building Land'''
    _name = 'realestate.building_land'
        
    owner_id = fields.Many2one('res.partner', string = 'The land owner.')
    address_id = fields.Many2one('res.partner', string = 'The land address')
    land_division = fields.Char(string = "The land division reference.")
    land_size = fields.Integer(string = "Size in ares.")   
    
    public_price = fields.Integer(string = "The public price.")
    estimated_price = fields.Integer(string = "The estimated price.")
    
    parent_id = fields.Many2one('realestate.building_land', string = 'The parent land.')
       
building_land()