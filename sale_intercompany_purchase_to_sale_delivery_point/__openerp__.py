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

{
    'name': 'sale_intercompany_purchase_to_sale_delivery_point_base_compatibility',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module make compatible the module sale intercompany_purchase to sale and delivery_point_base
    You will need it in order to have the sale order workflow working for the two company""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'delivery_base_dropoff',
        'sale_intercompany_purchase_to_sale',
    ], 
    'init_xml': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'auto_install': True,
}
