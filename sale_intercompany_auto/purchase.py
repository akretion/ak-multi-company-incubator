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

#TODO: share picking
#TODO: dest address can be customer address when depends on purchase_to_sale

class purchase_order(osv.osv):

    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get("sale.order")
        sale_line_obj = self.pool.get("sale.order.line")
        company_obj = self.pool.get("res.company")
        shop_obj = self.pool.get("sale.shop")
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
                    print "po part", po.partner_id.name, ('partner_id', '=', po.partner_id.id), comp_id, shop_id
                    order_line = []
                    for po_line in po.order_line:
                        line_vals = {'product_id': po_line.product_id.id}
                        #TODO onchange
                        line_vals['name'] = "blabla"
                        line_vals['price_unit'] = po_line.price_unit
                        line_vals['product_uom_qty'] = po_line.product_qty
                        line_vals['product_uom'] = po_line.product_uom.id
                        order_line.append((0, 0, line_vals))
                    so_vals['order_line'] = order_line
                    print "******************", so_vals
                    so_id = sale_obj.create(cr, uid, so_vals, context)
#                   sale_obj.write(cr, uid, [so_id], {'company_id': comp_id})
        return super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context)
