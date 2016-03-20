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

import logging

_logger = logging.getLogger(__name__)

class Partner(osv.osv):
    '''Partner'''
    _inherit = 'res.partner'
    
    _columns = {
        'team': fields.many2one('membership.team', 'Team', ondelete='set default', help = "The team the member belongs to."),
        'license': fields.char('License', size = 20, help = "The license of the team player."),
    }
    
    def update_all_membership_state(self, cr, uid, context=None):
        _logger.info('Update all membership state')
        ids = self.pool.get('res.partner').search(cr, uid, [])
        self._store_set_values(cr, uid, ids, ['membership_state'], context)
        _logger.info("Processed %s partner(s)",len(ids))
        return True
    
Partner()

class Team(osv.osv):
    '''Team'''
    _description = __doc__
    _name = 'membership.team'
    _columns = {
        'sequence': fields.integer('Sequence', size = 20, help = "The sequence to display the teams."),        
        'name': fields.char('Name', size = 20, help = "The name of the team."),
        'default_analytic_account' : fields.many2one ('account.analytic.account', 'Default analytic account', ondelete='set default', help = "The default analytic account for the team."),
    }
    
    _order = 'sequence'
        
Team()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'team' : fields.related(
                            'partner_id',
                            'team',
                            type="many2one",
                            relation="membership.team",
                            string="Team",
                            store=False)
    }
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def create(self, cr, uid, vals, context=None):
        """Overrides orm create method
        """
        result = super(account_invoice_line, self).create(cr, uid, vals, context=context)
        member_line = self.browse(cr, uid, result, context=context)
        if member_line.partner_id.team and member_line.partner_id.team.default_analytic_account:
            self.write(cr, uid, [member_line.id], {'account_analytic_id': member_line.partner_id.team.default_analytic_account.id}, context=context)
        return result

account_invoice_line()

class membership_line(osv.osv):
    
    _inherit='membership.membership_line'
    
    _columns = {
        'team': fields.many2one('membership.team', 'Team', ondelete='set default', help = "The team the member belongs to."),       
    }
    
    def create(self, cr, uid, vals, context=None):
        """Overrides orm create method
        """
        result = super(membership_line, self).create(cr, uid, vals, context=context)
        member_line = self.browse(cr, uid, result, context=context)
        if member_line.partner.team:
            self.write(cr, uid, [member_line.id], {'team': member_line.partner.team.id}, context=context)
        return result
                            
membership_line()