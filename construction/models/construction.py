# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import api, fields, models, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class BuildingSite(models.Model):
    '''Building Site'''
    _name = 'construction.building_site'
    _description = 'Building Site'
    
    _inherits = {'project.project': "project_id"}
    
    construction_state = fields.Selection([
            ('development', 'In development'),
            ('onsale', 'On Sale'),
            ('construction', 'In Construction'),
            ('waranty', 'Waranty'),
            ('long_waranty', 'Long Wanranty'),
            ('archived', 'Archived'),
        ], string='State', required=True, help="")
    
    @api.onchange('construction_state')
    def update_project_state(self):
        if self.construction_state == 'construction':
            self.state = 'open'
        if self.construction_state == 'waranty':
            self.state = 'close'
    
    project_id = fields.Many2one('project.project', 'Project',
            help="Link this site to a project",
            ondelete="cascade", required=True, auto_join=True)
    
    @api.onchange('project_id')
    def update_project(self):
        self.building_site_id = self.id
        
    type = fields.Selection([
            ('single', 'Single'),
            ('double', 'Double'),
            ('residency', 'Residency'),
        ], string='Type of building', required=True, help="")
    
    address_id = fields.Many2one('res.partner', string='Site adress', domain="[('type', '=', 'delivery')]")
    notes = fields.Text(string='Notes')
    
    acquisition_lead = fields.Many2one('crm.lead', string='Acquisition Lead')
    asset_ids = fields.One2many('construction.building_asset', 'site_id', string="Building Assets")
    
class Project(models.Model):
    _inherit = "project.project"
    
    building_site_id = fields.Many2one('construction.building_site', string='Building Site', ondelete='cascade')
    
class BuildingAsset(models.Model):
    '''Building Asset'''
    _name = 'construction.building_asset'
    _description = 'Building Asset'
    
    name = fields.Char(string="Name")
    
    state = fields.Selection([
            ('development', 'In development'),
            ('onsale', 'On sale'),
            ('proposal', 'Proposal'),
            ('sold', 'Sold'),
        ], string='State', required=True, help="",default="development")
    
    type = fields.Selection([
            ('appartment', 'Appartment'),
            ('duplex', 'Duplex'),
            ('house', 'House'),
            ('contiguous', 'Contiguous House'),
            ('prking', 'Parking'),
        ], string='Type of asset', required=True, help="")
    
    site_id = fields.Many2one('construction.building_site', string='Building Site')
    
    confirmed_lead_id = fields.Many2one('crm.lead', string='Confirmed Lead')
    candidate_lead_ids = fields.One2many('crm.lead', 'building_asset_id', string='Candidate Leads', domain=['|',('active','=',True),('active','=',False)])
    sale_order_ids = fields.One2many('sale.order', 'building_asset_id', string="Sale Orders")
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    building_asset_id = fields.Many2one('construction.building_asset', string='Building Asset', ondelete='set null')
    
    @api.onchange('state')
    def update_asset_state(self):
        if self.state == 'sent':
            self.building_asset_id.state = 'proposal'
            # TODO add to the candidate lead_ids
        if self.state == 'sale':
            self.building_asset_id.state = 'sold'
            self.confirmed_lead_id.id = self.opportunity_id.id
            
class CrmLean(models.Model):
    _inherit = "crm.lead"
    
    building_asset_id = fields.Many2one('construction.building_asset', string='Building Asset', ondelete='set null')
    building_site_id = fields.Many2one('construction.building_site', string='Building Site', related="building_asset_id.site_id",store=True)
    
class Invoice(models.Model):
    '''Invoice'''
    _inherit = 'account.invoice'
    
    building_asset_id = fields.Many2one('construction.building_asset', string='Building Asset', ondelete='set null')