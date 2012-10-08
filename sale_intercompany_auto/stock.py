# -*- coding: utf-8 -*-
##############################################################################
#
#    sale_intercompany_auto module for OpenERP,
#    Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>. All Rights Reserved
#       @author Sébastien BEAU <sebastien.beau@akretion.com>
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
###############################################################################

from openerp.osv.orm import Model

class stock_move(Model):
    _inherit = 'stock.move'

    #TODO FIXME do something better, need some refactor in addons
    def create_chained_picking(self, cr, uid, moves, context=None):
        if moves[0].picking_id.sale_id and moves[0].picking_id.sale_id.is_intercompany:
            if context is None: context = {}
            context['intercompany_partner_id'] = moves[0].picking_id.sale_id.partner_id.id
        return super(stock_move, self).create_chained_picking(cr, uid, moves, context=context)

class stock_location(Model):
    _inherit = 'stock.location'

    def chained_location_get(self, cr, uid, location, partner=None, product=None, context=None):
        #TODO add information in the context before calling this function

        result = super(stock_location, self).chained_location_get(cr, uid, location,
                                                                 partner=partner, product=product,
                                                                 context=context)
        if result and context:
            partner_id = context.get('intercompany_partner_id')
            if partner_id:
                result = list(result)
                partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
                result[0] = partner.property_stock_customer
                result = tuple(result)
        return result
