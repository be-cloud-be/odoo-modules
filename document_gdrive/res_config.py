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
from openerp.osv import fields, osv

class knowledge_config_settings(osv.osv_memory):
    _inherit = 'knowledge.config.settings'
    
    _columns = {
        'document_gdrive_upload_dir': fields.char('Google Drive Upload Directory',
            help='Directory where the files will be uploaded using the Google File Picker.'),
    }
    
    _default = {
        'document_gdrive_upload_dir': _document_gdrive_upload_dir,
    }
    
    def _document_gdrive_upload_dir(self, cr, uid, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        return icp.get_param(cr, uid, 'document.gdrive.upload.dir')
    
    def set_document_gdrive_upload_dir(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        icp.set_param(cr, uid, 'document.gdrive.upload.dir', repr(config.document_gdrive_upload_dir))
        