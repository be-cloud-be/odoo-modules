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

import zipfile
from StringIO import StringIO

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.addons.base.res.res_bank import sanitize_account_number

_logger = logging.getLogger(__name__)

class BulkImportStatement(models.TransientModel):
    _name = "account_bulk_import_wizard.account_bulk_import_wizard"
    _description = "Bulk Import Statement"
    
    zip_file = fields.Binary(string='Bank Statement File', required=True, help='Bulk import all files in a zip...')
    
    @api.multi
    def bulk_import_statement(self):
        self.ensure_one()
        bin_data = self.zip_file and self.zip_file.decode('base64') or ''
        zippedFiles = zipfile.ZipFile(StringIO(bin_data))
        statement_ids = []
        notifications = []
        for filename in zippedFiles.namelist():
            try :
                data = zippedFiles.read(filename)
                base_import = self.env['account.bank.statement.import'].create({
                    'data_file' : data.encode('base64'),
                })
                currency_code, account_number, stmts_vals = base_import.with_context(active_id=self.ids[0])._parse_file(data)
                if account_number:
                    sanitized_account_number = sanitize_account_number(account_number)
                    journal_id = self.env['account.journal'].search([('bank_account_id.sanitized_acc_number', '=', sanitized_account_number)])
                    if journal_id:
                        ret = base_import.with_context({'journal_id' : journal_id.id}).import_file()
                        statement_ids.extend(ret['context']['statement_ids'])
                        notifications.extend(ret['context']['notifications'])
            except UserError:
                pass
        if len(statement_ids) == 0:
            raise UserError(_('You have already imported all these files.'))
        # Finally dispatch to reconciliation interface
        action = self.env.ref('account.action_bank_reconcile_bank_statements')
        return {
            'name': action.name,
            'tag': action.tag,
            'context': {
                'statement_ids': statement_ids,
                'notifications': notifications
            },
            'type': 'ir.actions.client',
        }