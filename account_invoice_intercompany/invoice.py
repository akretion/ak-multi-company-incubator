# -*- coding: utf-8 -*-
###############################################################################
#
#   account_invoice_intercompany for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm, osv
from tools.translate import _
import netsvc
from openerp import SUPERUSER_ID


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def _get_intercompany_invoice(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.read(cr, SUPERUSER_ID, ids, ['customer_related_invoice_id'], context=context):
            if invoice['customer_related_invoice_id']:
                res[invoice['id']] = True
        return res

    _columns = {
        'customer_related_invoice_id': fields.many2one(
            'account.invoice',
            'Related Invoice of the other company'),
        'intercompany_invoice': fields.function(
            _get_intercompany_invoice,
            type="boolean",
            string='Intercompany invoice',
            help="Is this box is checked, an intercompany invoice has already "
            "been created.",
            store={
                'account.invoice':
                    (lambda self, cr, uid, ids, c=None:
                        ids,
                        ['customer_related_invoice_id'],
                        10),
                }),
    }

    def _prepare_intercompany_invoice(self, cr, uid, invoice, company_id, context=None):
        journal_obj = self.pool['account.journal']
        onchange_vals = self.onchange_partner_id(cr, uid, False, 'in_invoice',
                                                 invoice.company_id.partner_id.id,
                                                 date_invoice=invoice.date_invoice,
                                                 payment_term=invoice.payment_term,
                                                 partner_bank_id=False,
                                                 company_id=company_id)
        invoice_vals = onchange_vals['value']
        journal_ids = journal_obj.search(cr, uid, [('company_id','=',company_id),
                                                   ('type', '=', 'purchase')],
                                         context=context)
        currency_obj = self.pool['res.currency']
        currency_id = currency_obj.search(cr, uid, [
            ['name', '=', invoice.currency_id.name],
            ['company_id', '=', company_id],
            ], context=context)
        if not currency_id:
            raise orm.orm_except(_('USER ERROR'),
                _('No currency %s found in the company id %s')
                %(invoice.currency_id.name, company_id))
        elif len(currency_id) > 1:
            raise orm.orm_except(_('USER ERROR'),
                _('Too many currency found for the code %s in the company id %s')
                %(invoice.currency_id.name, company_id))
        else:
            currency_id = currency_id[0]
        invoice_vals.update({
                        'type': 'in_invoice',
                        'partner_id': invoice.company_id.partner_id.id,
                        'date_invoice': invoice.date_invoice,
                        'date_due': invoice.date_due,
                        'origin': invoice.number,
                        'currency_id': currency_id,
                        'name': 'Intercompany invoice from %s' % invoice.name,
                        'journal_id': journal_ids and journal_ids[0] or False,
                        'comment': invoice.comment,
        })
        return invoice_vals

    def _prepare_intercompany_line(self, cr, uid, line, invoice_vals, company_id, context=None):
        invoice_line_obj = self.pool['account.invoice.line']
        onchange_vals = invoice_line_obj.product_id_change(cr, uid, False,
                           line.product_id.id,
                           False,
                           qty=line.quantity,
                           name=line.name,
                           type='in_invoice',
                           partner_id=line.invoice_id.company_id.partner_id.id,
                           fposition_id=invoice_vals.get('fiscal_position', False),
                           price_unit=line.price_unit,
                           currency_id=invoice_vals.get('currency_id', False),
                           context=context,
                           company_id=company_id)
        line_vals = onchange_vals['value']
        line_vals.update({
                'origin': line.invoice_id.number,
                'name': line.name,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                'company_id': company_id,
                'invoice_line_tax_id': [(6, 0, onchange_vals['value']['invoice_line_tax_id'])],
            })
        return line_vals


    def _create_intercompany_invoice(self, cr, uid, invoice, company_id, context=None):
        wf_service = netsvc.LocalService("workflow")
        invoice_vals = self._prepare_intercompany_invoice(cr, uid, invoice, company_id, context=context)
        lines = []
        for line in invoice.invoice_line:
            line_vals = self._prepare_intercompany_line(cr, uid,
                                                         line,
                                                         invoice_vals,
                                                         company_id,
                                                         context=context)
            lines.append((0, 0, line_vals))
        invoice_vals.update({'invoice_line': lines})
        new_invoice_id = self.create(cr, uid, invoice_vals, context=context)
        self.button_reset_taxes(cr, uid, [new_invoice_id], context=context)
        amounts = self.read(cr, SUPERUSER_ID,
                                  [invoice.id, new_invoice_id],
                                  ['amount_total', 'amount_tax'],
                                  context=context)
        if amounts[0]['amount_total'] != amounts[1]['amount_total'] or \
        amounts[0]['amount_tax'] != amounts[1]['amount_tax']:
            raise osv.except_osv(_('Error !'),
                                 _("The total amount or the tax amount of the "
                                   "two invoices is different !"))
        wf_service.trg_validate(uid, 'account.invoice', new_invoice_id, 'invoice_open', cr)
        return new_invoice_id

    def create_intercompany_invoice(self, cr, uid, ids, context=None):
        company_obj = self.pool['res.company']
        for invoice in self.browse(cr, uid, ids, context=None):
            if invoice.type != 'out_invoice' or invoice.customer_related_invoice_id:
                continue
            company_ids = company_obj.search(cr, SUPERUSER_ID,
                                             [('partner_id', '=', invoice.partner_id.id)],
                                             context=context)
            if company_ids:
                if len(company_ids) > 1:
                    raise  osv.except_osv(_('Configuration Error !'),
                                          _('The partner : %s of the invoice : '
                                            '%s is linked to several companies.')
                                          % (invoice.partner_id.name, invoice.number))
                other_company_uid = company_obj.get_company_action_user(cr, SUPERUSER_ID,
                                                                        company_ids[0],
                                                                        context=context)
                new_invoice_id = self._create_intercompany_invoice(cr, other_company_uid, invoice,
                                                 company_ids[0], context=context)
                invoice.write({'customer_related_invoice_id': new_invoice_id})
        return True
