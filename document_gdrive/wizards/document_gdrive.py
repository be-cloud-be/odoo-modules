# -*- coding: utf-8 -*-
# Copyright 2015 be-cloud.be Jerome Sonnet <jerome.sonnet@be-cloud.be>
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
try:
    # Python 3
    from urllib import parse as urlparse
except:
    from urlparse import urlparse


class AddGDriveWizard(models.TransientModel):
    _name = 'ir.attachment.add_gdrive'

    name = fields.Char(string='Document Name')
    url = fields.Char(string='Document Url')

    @api.model
    def action_add_gdrive(self, docs):
        """Adds the Google Drive Document with an ir.attachment record."""
        context = self.env.context
        if not context.get('active_model'):
            return
        for doc in docs:
            url = urlparse(doc['url'])
            if not url.scheme:
                url = urlparse('%s%s' % ('http://', url))
            for active_id in context.get('active_ids', []):
                self.env['ir.attachment'].create({
                    'name': doc['name'],
                    'type': 'url',
                    'url': url.geturl(),
                    'res_id': active_id,
                    'res_model': context['active_model'],
                })
        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}
