# -*- coding: utf-8 -*-
#
# Author : Jerome Sonnet - jerome.sonnet@be-cloud.be
#
#
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

## Add real estate information to CRM Lead.
class crm_lead (models.Model):
    """ CRM Lead with Real Estate Extension """
    _name = "crm.lead"
    _description = "Lead/Opportunity"
    _inherit = {'crm.lead'}
    
    type_of_lead = fields.Selection(selection = [ ('acquisition','Acquisition'), ('sale','Sale'), ], select=True, string = 'Type of lead', help="Type of lead is used to separate Acquisition and Sales")
    
    item_of_interest_id = fields.Many2one('realestate.building_land', string='Item of Interest', ondelete='set null', track_visibility='onchange',
            select=True, help="Linked item of interest (optional). Usually created when converting the lead.")

    @api.model
    def default_get(self, fields):
        res = super(crm_lead, self).default_get(fields)
        context = self.env.context        
        if context and 'type_of_lead' in context:
            res['type_of_lead'] = context['type_of_lead']
        return res

crm_lead()

class realestate_abstract_asset(models.AbstractModel):
    '''Real Estate Asset Abstract Class'''
    _name = 'realestate.realestate_abstract_asset'
    
    _inherits = { 'res.partner' : 'address_id'}
    
    description = fields.Text(string="Description of the building land.")
    
    owner_id = fields.Many2one('res.partner', string = 'The land owner.')
    address_id = fields.Many2one('res.partner', string = 'The land address',required=True, ondelete='cascade')
    
    public_price = fields.Integer(string = "The public price.")
    estimated_price = fields.Integer(string = "The estimated price.")

    # Better to delegate ;-)
    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {}

realestate_abstract_asset()

class realestate_asset(models.Model):
    '''Real Estate Asset'''
    _name = 'realestate.realestate_asset'
    
    _inherit = {'realestate.realestate_abstract_asset'} 
    
    to_buy = fields.Boolean(string='This asset can be bought')
    to_sale = fields.Boolean(string='This asset can be sold')
    parent_id = fields.Many2one('realestate.realestate_asset', string = 'Procurement Group'),
    component_ids = fields.One2many('realestate.realestate_asset', 'parent_id', string = 'The component of the asset.')

realestate_asset()

class building_land(models.Model):
    '''Building Land'''
    _name = 'realestate.building_land'
        
    _inherit = {'realestate.realestate_asset'}
    
    land_division = fields.Char(string = "The land division reference.")
    land_size = fields.Integer(string = "Size in ares.")   
    
    parent_id = fields.Many2one('realestate.building_land', string = 'The parent land in case it has been splitted.')
       
building_land()

class building(models.AbstractModel):
    '''Building'''
    _name ='realestate.building'
    
    _inherit = {'realestate.realestate_asset'}
    
    land_id = fields.Many2one('realestate.building_land', string = 'The land the building is built upon.')
    land_portion = fields.Float(string='Portion of the land linked to the building.')

    type = fields.Selection(string="The type of building",selection=[ ('house','House'), ('flat','Flat'), ], select=True)

    rooms = fields.Integer(string="Number of rooms")
    size = fields.Integer(string="Size in square meters")
    parking = fields.Integer(string="Number of parkings")

building()