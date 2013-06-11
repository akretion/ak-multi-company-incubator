# -*- coding: utf-8 -*-
##############################################################################
#
#    sale_intercompany_purchase_to_sale module for OpenERP,
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
from openerp.osv import fields
from openerp import SUPERUSER_ID

class stock_move(Model):
    _inherit = 'stock.move'


class stock_picking(Model):
    _inherit = 'stock.picking'

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        res = super(stock_picking, self).do_partial(cr, uid, ids, partial_datas, context=None)
        #TODO support partial picking
        for picking in self.browse(cr, SUPERUSER_ID, ids, context=context):
            if picking.type == 'out' and picking.sale_id.is_intercompany:#Only if drop?
                for related_picking in picking.sale_id.purchase_id.picking_ids:
                    uid = 4 #TODO FIXME
                    self.validate_picking(cr, uid, [related_picking.id], context=context)
                    related_picking.write({
                        'carrier_id': picking.carrier_id.id,
                        'carrier_tracking_ref': picking.carrier_tracking_ref,
                    })
        return res

    #Keep it here? importing a tracking number in company A should update the tacking in B?
    def write(self, cr, uid, ids, vals, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        res = super(stock_picking, self).write(cr, uid, ids, vals, context=context)
        if 'carrier_tracking_ref' in vals:
            for picking in self.browse(cr, SUPERUSER_ID, ids, context=context):
                if picking.type == 'out' and picking.sale_id.is_intercompany:#Only if drop?
                    for related_picking in picking.sale_id.purchase_id.picking_ids:
                        uid = 4 #TODO FIXME
                        related_picking.write({
                            'carrier_tracking_ref': vals['carrier_tracking_ref'],
                        })
        return res
