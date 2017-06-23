# -*- encoding: utf-8 -*-
# Subject to license. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, tools, _
from openerp.exceptions import UserError
import logging

import dbf
import tempfile, os, shutil
from os.path import join, dirname
import zipfile
import base64
import re
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class ExportFile(models.Model):
    '''Export Sage 50'''
    _name = 'export_sage_50.export_file'
    _description = 'Export File For Sage 50'
    
    _order = 'date_to desc'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('completed', 'Completed'),
        ], string='Status', index=True, readonly=True, default='draft',
        copy=False,
        help=" * The 'Draft' status is used when a new export is created but not yet filled.\n"
             " * The 'Completed' status is when an export has been filled and is ready for import.\n")
    
    name = fields.Char(compute="_compute_vals",store=True)
    filename = fields.Char(compute="_compute_vals",store=True)
    
    date_from = fields.Date(string="Date From", compute="_compute_vals",store=True)
    date_to = fields.Date(string="Date To", compute="_compute_vals",store=True)
    
    invoice_ids = fields.Many2many('account.invoice', 'export_sage_50_invoice_rel','export_id','invoice_id',string="Invoices",readonly=True)
    invoice_count = fields.Integer(string="Invoices Count", compute="_compute_vals",store=True)
    
    
    export_file = fields.Binary(attachment=True, help="This field holds the export file for Sage 50.",readonly=True)
    export_file_name = fields.Char(compute="_compute_vals")
    
    @api.depends('invoice_ids')
    @api.one
    def _compute_vals(self):
        date_from = False
        date_to = False
        for invoice in self.invoice_ids:
            if date_to == False or invoice.date >= date_to:
                date_to = invoice.date
            if date_from == False or invoice.date <= date_from:
                date_from = invoice.date
        self.date_from = date_from
        self.date_to = date_to
        self.name = 'export%s' % (date_to)
        self.filename = 'export%s.zip' % (date_to)
        self.export_file_name = 'export%s.zip' % (date_to)
        self.invoice_count = len(self.invoice_ids)
    
    @api.multi
    def action_export_all_missing(self):
        self.ensure_one()
        self.invoice_ids = self.env['account.invoice'].search([('is_exported_to_sage_50', '=', False),('state','in',['open','paid'])])
        self._create_export_from_invoices()
        
    @api.multi
    def action_export_last_month(self):
        self.ensure_one()
        date_from = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        date_to = date.today().replace(day=1) - timedelta(days=1)
        
        self.invoice_ids = self.env['account.invoice'].search([('date','<=',date_to),('date','>=',date_from),('state','in',['open','paid'])])
        self._create_export_from_invoices()
        
    @api.multi
    def action_export_last_quarter(self):
        self.ensure_one()
        date_from = ((date.today().replace(day=1) - timedelta(days=1)).replace(day=1)) - relativedelta(months=+3)
        date_to = date.today().replace(day=1) - timedelta(days=1)
        
        self.invoice_ids = self.env['account.invoice'].search([('date','<=',date_to),('date','>=',date_from),('state','in',['open','paid'])])
        self._create_export_from_invoices()
    
    @api.multi
    def action_export_custom(self, date_from, date_to):
        self.ensure_one()
        self.invoice_ids = self.env['account.invoice'].search([('date','<=',date_to),('date','>=',date_from),('state','in',['open','paid'])])
        self._create_export_from_invoices()
    
    @api.one
    def _create_export_from_invoices(self):
        tmpdir = tempfile.mkdtemp()
        shutil.copy(join(dirname(__file__),"BOBLINK.TXT"), tmpdir)
        
        ## Create CLIENTS.DBF
        partner_ids = self.invoice_ids.mapped('partner_id')
        db_part = dbf.Table(join(tmpdir, "CLIENTS.DBF"), codepage='utf8', field_specs='CID C(10); CCUSTYPE C(1); CSUPTYPE C(1); CNAME1 C(40); CADDRESS1 C(40); CADDRESS2 C(40); CZIPCODE C(10); CLOCALITY C(40); CCOUNTRY C(6); CVATREF C(2); CVATNO C(12); CVATCAT C(1);')
        db_part.open()
        for partner in partner_ids:
            rec = dbf.create_template(db_part)
            rec.cid = partner.ref if partner.ref else ""
            rec.ccustype = "C"
            rec.csuptype = "U"
            rec.cname1 = partner.name if partner.name else ""
            rec.caddress1 = partner.street if partner.street else ""
            rec.caddress2 = partner.street2 if partner.street2 else ""
            rec.czipcode = partner.zip if partner.zip else ""
            rec.clocality = partner.city if partner.city else ""
            rec.ccountry = partner.country_id.code if partner.country_id else ""
            rec.cvatref = partner.vat[:2] if partner.vat else ""
            rec.cvatno = partner.vat[2:] if partner.vat else ""
            rec.cvatcat = ""
            db_part.append(rec) 
        db_part.close()
        
        ## Create SALES.DBF
        db_inv = dbf.Table(join(tmpdir, "SALES.DBF"), codepage='utf8', 
        field_specs='TDBK C(4); TFYEAR C(5); TYEAR N(4,0); TMONTH N(2,0); TDOCNO N(10,0); TDOCDATE D; TTYPCIE C(1); TCOMPAN C(10); TDUEDATE D; TAMOUNT N(10,2); TREMINT C(40); TREMEXT C(40); TINTMODE C(1); TINVVCS C(12)')
        db_inv_line = dbf.Table(join(tmpdir, "SALESL.DBF"), codepage='utf8', 
        field_specs='TDBK C(4); TFYEAR C(5); TYEAR N(4,0); TMONTH N(2,0); TDOCNO N(10,0); TDOCLINE N(5,0); TTYPELINE C(1); TACTTYPE C(1); TACCOUNT C(10); TAMOUNT N(10,2); TBASVAT N(10,2); TVATTOTAMN N(10,2); TVATAMN N(10,2); TVATDBLAMN N(10,2); TBASLSTAMN N(10,2); TVSTORED C(10); TDC C(1); TREM C(40)')

        db_inv.open()
        db_inv_line.open()
        for invoice in self.invoice_ids:
            rec = dbf.create_template(db_inv)
            rec.tdbk = "VEN"
            date = fields.Date.from_string(invoice['date'])
            rec.tfyear = date.strftime("%Y")
            rec.tyear = date.year
            rec.tmonth = date.month
            rec.tdocno = int(re.sub("\D", "", invoice.number))
            rec.tdocdate = dbf.Date(date)
            rec.ttypcie = 'C'
            rec.tcompan = invoice.partner_id.ref if invoice.partner_id.ref else ""
            rec.tduedate = dbf.Date(fields.Date.from_string(invoice['date_due']))
            rec.tamount = invoice.amount_total
            rec.tremint = invoice.name if invoice.name else ""
            rec.tremext = invoice.reference if invoice.reference else ""
            rec.tintmode = "S"
            rec.tinvvcs= re.sub("\D", "", invoice.reference) if invoice.reference else ""
            line_nb = 0
            for invoice_line in invoice.invoice_line_ids:
                rec_line = dbf.create_template(db_inv_line)
                rec_line.tdbk = rec.tdbk
                rec_line.tfyear = rec.tfyear
                rec_line.tyear = rec.tyear
                rec_line.tmonth = rec.tmonth
                rec_line.tdocno = rec.tdocno
                rec_line.tdocline = line_nb
                line_nb += 1
                rec_line.ttypeline = "S"
                rec_line.tacttype = "A"
                rec_line.taccount = "700000" # TODO : Make this a config param
                rec_line.tamount = invoice_line.price_subtotal
                rec_line.tbasvat = invoice_line.price_subtotal
                vat = 0.0
                taxes = invoice_line.get_taxes_values()
                for tax in taxes:
                    vat += taxes[tax]['amount'] # SHOULD WE FILTER TO GET ONLY VAT
                rec_line.tvattotamn = vat
                rec_line.tvatamn = vat
                rec_line.tvatdblamn = 0
                rec_line.tbaslstamn = invoice_line.price_subtotal
                code = invoice_line.invoice_line_tax_ids[0].sage_50_code if invoice_line.invoice_line_tax_ids else ""
                rec_line.tvstored = code if code else ""
                rec_line.tdc = "C" if invoice_line.price_subtotal_signed > 0 else "D"
                rec_line.trem = invoice.partner_id.name
                db_inv_line.append(rec_line) 
            db_inv.append(rec) 
        db_inv.close()
        db_inv_line.close()
        
        temp = tempfile.mktemp(suffix='')
        shutil.make_archive(temp, 'zip', tmpdir)
        fn = open('%s.zip' % temp, 'r')
        self.export_file = base64.encodestring(fn.read())
        fn.close()
        
        for invoice in self.invoice_ids:
            invoice.is_exported_to_sage_50 = True
            
class ExportFileCustom(models.Model):
    '''Export Sage 50 Wizard'''
    _name = 'export_sage_50.export_file_wizard'
    _description = 'Export File For Sage 50 Wizard'
    
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    
    export_file_id = fields.Many2one('export_sage_50.export_file',string="Export File")
    
    @api.multi
    def action_export_custom(self):
        self.ensure_one()
        return self.export_file_id.action_export_custom(self.date_from, self.date_to)
