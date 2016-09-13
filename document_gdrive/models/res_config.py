# -*- coding: utf-8 -*-
# Copyright 2015 be-cloud.be Jerome Sonnet <jerome.sonnet@be-cloud.be>
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

<<<<<<< HEAD
from odoo import models, fields, api
=======
from openerp import models, fields, api

>>>>>>> [FIX] used new_api for 9.0 branch

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    @api.multi
    def _document_gdrive_client_id(self):
        icp = self.env['ir.config_parameter'].sudo()
        return icp.get_param('document.gdrive.client.id')

    @api.multi
    def set_document_gdrive_client_id(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('document.gdrive.client.id',
                      self.document_gdrive_client_id)

    @api.multi
    def _document_gdrive_upload_dir(self):
        icp = self.env['ir.config_parameter'].sudo()
        return icp.get_param('document.gdrive.upload.dir')

    @api.multi
    def set_document_gdrive_upload_dir(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('document.gdrive.upload.dir',
                      self.document_gdrive_upload_dir)

    document_gdrive_upload_dir = fields.Char(
        'Google Drive Upload Directory',
        default=_document_gdrive_upload_dir,
        help='Directory where the files will be uploaded using the Google File Picker.')
    document_gdrive_client_id = fields.Char(
        'Google Drive Client Id',
        default=_document_gdrive_client_id,
        help='Generate a Client ID key from the Google Console and paste it here.')
