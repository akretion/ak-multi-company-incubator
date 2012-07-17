# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Akretion
#    author Raphaël Valyi
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


class purchase_order(osv.osv):

    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get("sale.order")
        sale_line_obj = self.pool.get("sale.order.line")
        purchase_line_obj = self.pool.get("purchase.order.line")
        company_obj = self.pool.get("res.company")
        shop_obj = self.pool.get("sale.shop")
        move_obj = self.pool.get("stock.move")
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
        for po in self.browse(cr, uid, ids, context=context):
            partner_id = po.partner_id.id
            comp_ids = self.pool.get('res.company').search(cr, uid, [('partner_id', '=', partner_id)])
            if comp_ids:
                so_vals = {'partner_id': po.company_id.partner_id.id}
                so_vals.update(sale_obj.onchange_partner_id(cr, uid, [], so_vals['partner_id'])['value'])
                comp_id = comp_ids[0]
                shop_ids = shop_obj.search(cr, uid, [('company_id', '=', comp_id)])
                if shop_ids:
                    shop_id = shop_ids[0]
                    so_vals['shop_id'] = shop_id
                    so_vals['origin'] = 'PO:%s' % str(po.name)
                    so_vals['purchase_id'] = po.id
                    so_vals['partner_shipping_id'] = po.dest_address_id.id #manual or automatic drop shipping
                    po_line_dict = {}
                    order_line = []
                    for po_line in po.order_line:
                        line_vals = {'product_id': po_line.product_id.id}
                        #TODO extract in overridable method
                        line_vals.update(sale_line_obj.product_id_change(cr, uid, [], so_vals['pricelist_id'], po_line.product_id.id, po_line.product_qty, po_line.product_uom.id, False, False, False, so_vals['partner_id'], False, True, False, False, False, False, context)['value'])
                        line_vals['price_unit'] = po_line.price_unit
                        line_vals['product_uom_qty'] = po_line.product_qty
                        line_vals['product_uom'] = po_line.product_uom.id
                        line_vals['purchase_line_id'] = po_line.id
                        order_line.append((0, 0, line_vals))
                    so_vals['order_line'] = order_line
                    so_id = sale_obj.create(cr, uid, so_vals, context)
                            
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'sale.order', so_id, 'order_confirm', cr) #TODO optional
        return res

    def action_picking_create(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).action_picking_create(cr, uid, ids, context)
        sale_obj = self.pool.get('sale.order')
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for po in self.browse(cr, uid, ids):
            sale_ids = sale_obj.search(cr, uid, [('purchase_id', '=', po.id)]) #TODO create function field?
            if sale_ids:
                so = sale_obj.browse(cr, uid, sale_ids[0], context=context)
                picking_ids = set()
                for so_line in so.order_line:
                    if so_line.purchase_line_id:
                        move_obj.write(cr, uid, [move.id for move in so_line.purchase_line_id.move_ids], {'sale_line_id': so_line.id})
                        for move in so_line.purchase_line_id.move_ids:
                            picking_ids.add(move.picking_id.id)
                picking_obj.write(cr, uid, [i for i in picking_ids], {'sale_id': so.id})
                sale_obj.write(cr, uid, [so.id], {'shipped': False})
        return res 
