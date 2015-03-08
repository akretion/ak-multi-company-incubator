# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Akretion
#    author Raphaël Valyi
#           Sébastien Beau
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

from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _


class purchase_order(osv.osv):

    _inherit = "purchase.order"

    _columns = {
        'is_intercompany': fields.boolean('Intercompany Purchase'),
    }

    def _prepare_linked_sale_order(self, cr, uid, po, shop_id, context=None):
        sale_obj = self.pool.get("sale.order")
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.find_company_customer_id(
            cr, uid,
            po.company_id.id,
            po.partner_id.partner_company_id.id,
            context=context
        )
        vals = {'partner_id': partner_id}
        vals.update(sale_obj.onchange_partner_id(cr, uid, [], vals['partner_id'])['value'])
        vals.update({
            'shop_id': shop_id,
            'origin': 'PO:%s' % str(po.name),
            'purchase_id': po.id,
            'partner_shipping_id': partner_id,
            'is_intercompany': True,
        })
        return vals

    def _find_supplier_product_id(self, cr, uid, po_line, context=None):
        supplier_company = po_line.order_id.partner_id.partner_company_id
        for supplierinfo in po_line.product_id.seller_ids:
            if supplierinfo.supplier_company_id and supplierinfo.supplier_company_id.id == supplier_company.id:
                return supplierinfo.supplier_product_id.id
        return po_line.product_id.id

    def _prepare_linked_sale_order_line(self, cr, uid, po_line, so_vals, context=None):
        sale_line_obj = self.pool.get("sale.order.line")
        product_id = self._find_supplier_product_id(
            cr, uid, po_line, context=context
        )
        if not product_id:
            raise osv.except_osv(
                _('Error'),
                _('The product %s (id:%d) is not associated with the one in '
                'the supplier\'s company') % (
                    po_line.product_id.name, po_line.product_id.id
                )
            )
        on_change_vals = sale_line_obj.product_id_change(
            cr, uid, [], so_vals['pricelist_id'], product_id,
            po_line.product_qty, po_line.product_uom.id, False, False, False,
            so_vals['partner_id'], False, True, False, False,
            so_vals['fiscal_position'], False, context
        )
        vals = {'product_id': product_id}
        vals.update(on_change_vals['value'])
        vals['tax_id'] = [(6, 0, on_change_vals['value']['tax_id'])]
        vals.update({
            'price_unit': po_line.price_unit,
            'product_uom_qty': po_line.product_qty,
            'product_uom': po_line.product_uom.id,
            'purchase_line_id': po_line.id,
        })
        return vals

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get("sale.order")
        purchase_line_obj = self.pool.get("purchase.order.line")
        company_obj = self.pool.get("res.company")
        shop_obj = self.pool.get("sale.shop")
        move_obj = self.pool.get("stock.move")
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        for po in self.browse(cr, uid, ids, context=context):
            company = po.partner_id.partner_company_id
            if not company:
                continue
            supplier_uid = company.automatic_action_user_id.id
            partner_id = po.partner_id.id
            comp_id = company.id
            shop_ids = shop_obj.search(cr, supplier_uid, [('company_id', '=', comp_id)])
            if not shop_ids:
                continue
            so_vals = self._prepare_linked_sale_order(cr, supplier_uid, po, shop_ids[0], context=context)
            order_lines = []
            for po_line in po.order_line:
                order_line = self._prepare_linked_sale_order_line(
                    cr, supplier_uid, po_line, so_vals, context=context
                )
                order_lines.append((0, 0, order_line))
            so_vals['order_line'] = order_lines
            so_id = sale_obj.create(cr, supplier_uid, so_vals, context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(supplier_uid, 'sale.order', so_id, 'order_confirm', cr)
            po.write({'is_intercompany': True}, context=context)
        return res

    def action_invoice_create(self, cr, uid, ids, context=None):
        ids = self.search(cr, uid,[
                        ('id', 'in', ids),
                        ('is_intercompany', '=', False)
                    ], context=context)
        return super(purchase_order, self).action_invoice_create(cr, uid,
                                                            ids, context=context)

