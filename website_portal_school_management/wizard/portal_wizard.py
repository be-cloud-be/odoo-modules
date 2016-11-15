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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_split
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class wizard(osv.osv_memory):
    _inherit = 'portal.wizard'

    def onchange_portal_id(self, cr, uid, ids, portal_id, context=None):
        # for each partner, determine corresponding portal.wizard.user records
        res_partner = self.pool.get('res.partner')
        partner_ids = context and context.get('active_ids') or []
        contact_ids = set()
        user_changes = []
        for partner in res_partner.browse(cr, SUPERUSER_ID, partner_ids, context):
            # do not get into child_ids here
            for contact in [partner]:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    # default to in_portal = True
                    in_portal = True
                    if contact.user_ids:
                        in_portal = portal_id in [g.id for g in contact.user_ids[0].groups_id]
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                    }))
        return {'value': {'user_ids': user_changes}}