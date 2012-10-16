# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Akretion
#    author Benoît Guillot
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

from osv import osv, fields
import netsvc
from openerp import SUPERUSER_ID
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'customer_related_invoice_id': fields.many2one('account.invoice', 'Related Invoice of the other company'),
    }
    
    def create_related_invoice(self, cr, uid, company_id, inv, context=None):
        wf_service = netsvc.LocalService("workflow")
        action_user_id = self.pool.get('res.company').get_company_action_user(cr, SUPERUSER_ID, company_id, context=context)
        partner_id = inv.company_id.partner_id.id
        new_data = {
            'name': inv.name,
            'origin': inv.origin,
            'date_invoice': inv.date_invoice,
            'state': 'draft',
            'comment': inv.comment,
            'type': 'in_invoice',
            'partner_id': partner_id,
            'company_id': company_id,
            'currency_id': inv.currency_id.id,
            'invoice_line': []
        }
        partner_info = self.onchange_partner_id(cr, action_user_id, False, 'in_invoice', partner_id,\
            date_invoice=inv.date_invoice, payment_term=False, partner_bank_id=False, company_id=company_id)
        new_data.update(partner_info['value'])
        for line in inv.invoice_line:
            new_line = self.pool.get('account.invoice.line').product_id_change(cr, action_user_id, False, \
                        line.product_id.id, line.uos_id.id, line.quantity, name='', type='in_invoice', partner_id=partner_id,\
                        fposition_id=False, price_unit=line.price_unit, address_invoice_id=new_data['address_invoice_id'],\
                        currency_id=inv.currency_id.id, context=context, company_id=company_id)['value']
            taxes = self.pool.get('account.invoice.line').onchange_account_id(cr, action_user_id, False,\
                            line.product_id.id, partner_id, 'in_invoice', False, new_line['account_id'])['value']['invoice_line_tax_id']
            new_line['invoice_line_tax_id'] = [(6, 0, taxes)]
            new_line.update({
                'product_id': line.product_id.id,
                'quantity': line.quantity,
            })
            new_data['invoice_line'].append((0, 0, new_line))

        new_inv_id = self.create(cr, action_user_id, new_data, context=context)
        self.button_reset_taxes(cr, action_user_id, [new_inv_id], context=context)
        total_amounts = self.read(cr, SUPERUSER_ID, [inv.id, new_inv_id], ['amount_total'], context=context)
        if total_amounts[0]['amount_total'] != total_amounts[1]['amount_total']:
            raise osv.except_osv(_('Error !'),_("The total amount of the two invoices is different !"))
        wf_service.trg_validate(action_user_id, 'account.invoice', new_inv_id, 'invoice_open', cr)
        return new_inv_id
    
    def action_number(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, SUPERUSER_ID, ids, context=context):
            company_id = self.pool.get('res.company').search(cr, SUPERUSER_ID, [('partner_id', '=', inv.partner_id.id)], context=context)
            if company_id and not inv.customer_related_invoice_id and inv.type == 'out_invoice':
                new_invoice_id = self.create_related_invoice(cr, uid, company_id[0], inv, context=context)
                inv.write({'customer_related_invoice_id': new_invoice_id})
        return super(account_invoice, self).action_number(cr, uid, ids, context=context)