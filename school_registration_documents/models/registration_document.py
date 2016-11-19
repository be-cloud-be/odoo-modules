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

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
    
    official_document_ids = fields.One2many('school.official_document', 'student_id', string="Official Documents")
    official_document_count = fields.Integer(string='Missing Official Documents Count', compute="_compute_official_document_missing_count")
    official_document_missing_count = fields.Integer(string='Missing Official Documents Count', compute="_compute_official_document_missing_count")
    
    @api.depends('official_document_ids','official_document_ids.is_available')
    @api.multi
    def _compute_official_document_missing_count(self):
        docs_data = self.env['school.official_document'].read_group(
            [('student_id', 'in', self.ids), ('is_available', '=', False)], ['student_id'], ['student_id'])
        result = dict((data['student_id'][0], data['student_id_count']) for data in docs_data)
        for partner in self:
            partner.official_document_count = len(partner.official_document_ids)
            partner.official_document_missing_count = result.get(partner.id, 0)
            
    @api.multi
    def action_view_documents(self):
        official_document_ids = self.mapped('official_document_ids')
        domain = "[('id', 'in', " + str(official_document_ids.ids) + ")]"
        return {
                'name': _('Documents'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'school.official_document',
                'domain': domain
        }
            
class OfficialDocument(models.Model):
    '''Official Document'''
    _name = 'school.official_document'
    _inherit = ['ir.needaction_mixin']
    
    name = fields.Char('Name',compute='compute_name')
    
    @api.depends('student_id.name','type_id.name')
    @api.multi
    def compute_name(self):
        for doc in self:
            doc.name = "%s - %s" % (doc.student_id.name, doc.type_id.name)
    
    student_id = fields.Many2one('res.partner', string='Student', domain="[('student', '=', '1')]",required = True, readonly=True)
    
    type_id = fields.Many2one('school.official_document_type',string="Type",required = True)
    
    is_available = fields.Boolean('Is Available',default = False)
    
    attachment_ids = fields.Many2many('ir.attachment','official_document_ir_attachment_rel', 'official_document_id','ir_attachment_id', 'Attachments', domain="[('res_model','=','res.partner'),('res_id','=',student_id)]")
    
    note = fields.Text('Notes')
    
    @api.model
    def _needaction_domain_get(self):
        return [('is_available', '=', False)]
    
class OfficialDocumentType(models.Model):
    '''Official Document'''
    _name = 'school.official_document_type'
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    note = fields.Text('Notes')
    default_add = fields.Boolean('Default Add', default=False)
    
    active = fields.Boolean('Active', default=True)