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
    _name = 'crm.lead'
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

# class sale_order_line(models.Model):
#     """ Sale Order Line with Real Estate Extension """
#     _name = 'sale.order.line'
#     _inherit = {'sale.order.line'}
#
#     asset_id = fields.Many2one(string='Real Estate Asset Reference',comodel_name='realestate.realestate_asset', ondelete='set null')
#
# sale_order_line()

class realestate_abstract_asset(models.Model):
    '''Real Estate Asset Abstract Class'''
    _name = 'realestate.realestate_abstract_asset'
    
    name = fields.Char(string="Name", description="Short description of the asset.", select=True)
    description = fields.Text(string="Description", description="Description of the asset.")
    
    type = fields.Selection(string="Asset Type", description="The type of asset",selection=[ ('composite','Composite'), ('land','Land'), ('house','House'), ('flat','Flat'), ('parking','Parking'),], select=True)
    
    owner_id = fields.Many2one('res.partner', string ="Owner", description="The land owner", select=True)
    
    active = fields.Boolean(string = "Is Active", description="Set to false if the assets is not available (destroyed, splitted, lost,...)", select=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    
    @api.model
    def _get_currency(self):
        if self.env.user.company_id:
            return self.env.user.company_id.currency_id.id
    
    @api.model
    def default_get(self, fields):
        res = super(realestate_abstract_asset, self).default_get(fields)
        if 'type' in fields and 'default_type' in self.env.context:
            res['type'] = self.env.context['default_type']
        res['active'] = True
        res['currency_id'] = self._get_currency()
        return res

realestate_abstract_asset()

class realestate_asset(models.Model):
    '''Real Estate Single Asset'''
    _name = 'realestate.realestate_asset'
    
    _inherit = ['mail.thread']
    
    _inherits = {'realestate.realestate_abstract_asset':'asset_id'} 
    
    asset_id = fields.Many2one(comodel_name='realestate.realestate_abstract_asset', ondelete='cascade', required=True)
    
    @api.multi
    def unlink(self):
        for asset in self:
            asset.asset_id.unlink()
        return super(realestate_asset, self.sudo()).unlink()
    
    to_buy = fields.Boolean(string="To Buy", description="This asset can be bought.", select=True)
    to_sale = fields.Boolean(string="To Sale", description="This asset can be sold.", select=True)
        
    buy_price = fields.Integer(string = "Buy Price", description="The public buy price.")
    sale_price = fields.Integer(string = "Sale Price", description="The public sale price.")
    
    component_ids = fields.Many2many(comodel_name='realestate.realestate_abstract_asset', relation = "re_asset_abstr_rel", column1="par_id", column2="comp_id", string = "Components", description="The component of the asset.")
    
realestate_asset()

class building_land(models.Model):
    '''Building Land'''
    _name = 'realestate.building_land'
        
    _inherit = ['mail.thread']
        
    _inherits = {'realestate.realestate_abstract_asset':'asset_id'}
    
    asset_id = fields.Many2one(comodel_name='realestate.realestate_abstract_asset', ondelete='cascade', required=True)
    
    @api.multi
    def unlink(self):
        for asset in self:
            asset.asset_id.unlink()
        return super(building_land, self.sudo()).unlink()
        
    street = fields.Char(string = 'Street')
    street2 = fields.Char(string = 'Street2')
    zip = fields.Char(string = 'Zip', size=24, change_default=True)
    city = fields.Char(string = 'City')
    state_id = fields.Many2one("res.country.state", string = 'State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string = 'Country', ondelete='restrict')
    
    municipality = fields.Char(string = "Municipality", description="The municipality where the land is.", select=True)
    land_division = fields.Char(string = "Land Division", description="The land division reference.", select=True)
    land_size = fields.Float(string = "Size", description="Size in ares.")
    public_price = fields.Integer(string = "Public Price", description="The public price.")

    is_subdivision = fields.Boolean(string="Is Subdivision", description="Set true if it is a subdivision of a land through quotities", select=True)
    quotity = fields.Integer(string="Quotity", description="Quotity in 1/1,000th")
    
    parent_land_id = fields.Many2one('realestate.building_land', string = "Parent", description="The parent land in case it has been splitted.")
    subdivision_ids = fields.One2many('realestate.building_land', 'parent_land_id', string = "Subdivisions", description='The subdivision of the land.')
       
    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {}
           
building_land()

class parking(models.Model):
    '''Building'''
    _name ='realestate.parking'
    
    _inherit = ['mail.thread']
    
    _inherits = {'realestate.realestate_abstract_asset':'asset_id'}
    
    asset_id = fields.Many2one(comodel_name='realestate.realestate_abstract_asset', ondelete='cascade', required=True)
    
    @api.multi
    def unlink(self):
        for asset in self:
            asset.asset_id.unlink()
        return super(parking, self.sudo()).unlink()
    
    land_id = fields.Many2one('realestate.building_land', string = "Land", description="The land the parking is upon.")
    city = fields.Char(related='land_id.city', store=True, select=True)
    
    public_price = fields.Integer(string = "Public Price", description="The public price.")

parking()

class building(models.Model):
    '''Building'''
    _name ='realestate.building'
    
    _inherit = ['mail.thread']
    
    _inherits = {'realestate.realestate_abstract_asset':'asset_id'}
    
    asset_id = fields.Many2one(comodel_name='realestate.realestate_abstract_asset', ondelete='cascade', required=True)
    
    @api.multi
    def unlink(self):
        for asset in self:
            asset.asset_id.unlink()
        return super(building, self.sudo()).unlink()
    
    land_id = fields.Many2one('realestate.building_land', string = "Land", description="The land the building is built upon.")
    city = fields.Char(related='land_id.city', store=True, select=True)
    
    rooms = fields.Integer(string="Rooms", description="Number of rooms", select=True)
    size = fields.Integer(string="Size", description="Size in square meters", select=True)
    parkings = fields.Integer(string="Parkings", description="Number of parkings", select=True)

    public_price = fields.Integer(string = "Public Price", description="The public price.")

building()