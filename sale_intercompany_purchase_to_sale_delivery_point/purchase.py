# -*- coding: utf-8 -*-
###############################################################################
#
#   sale_intercompany_purchase_to_sale_delivery_point for OpenERP
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#     All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.osv import fields
from openerp.osv.orm import Model

class purchase_order(Model):
    _inherit = "purchase.order"

    def _prepare_linked_sale_order(self, cr, uid, po, shop_id, context=None):
        res = super(purchase_order, self)._prepare_linked_sale_order(cr, uid, po, shop_id, context=context)
        if po.sale_id:
            res.update({
                'dropoff_site_id': po.sale_id.dropoff_site_id.id,
            })
        return res

