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
from openerp.exceptions import MissingError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class AddDocuments(models.TransientModel):
    _name = "school.add_documents_wizard"
    _description = "Add Documents Wizard"
    
    student_id = fields.Many2one('res.partner', required=True)
    
    document_type_ids = fields.Many2many('school.official_document_type','add_documents_wizard_official_document_type_rel', 'add_documents_wizard_id','document_type_id', string="Official Document Types")
    
    @api.model
    def default_get(self, fields):
        res = super(AddDocuments, self).default_get(fields)
        document_type_ids = self.env['school.official_document_type'].search([('default_add','=',True)]).mapped('id')
        res['document_type_ids'] = document_type_ids
        return res
        
    @api.multi
    def on_confirm_documents(self):
        self.ensure_one()
        for doc_type in self.document_type_ids:
            new_doc = self.env['school.official_document'].create({'student_id':self.student_id.id,'type_id':doc_type.id})