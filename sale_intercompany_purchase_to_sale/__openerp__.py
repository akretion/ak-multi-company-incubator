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


{
    "name" : "Sale Intercompany Purchase Auto Sale",
    "version": "1.0",
    "author" : "Akretion",
    "website" : "www.akretion.com",
    "category" : "Generic Modules/Purchase",
    "depends" : [
        "purchase_to_sale"
    ],
    "description": """This module make compatible the module purchase to sale and sale intercompany
    You will need it in order to have the sale order workflow working for the two company
    """,
    "init_xml" : [
    ],
    "demo_xml" : [],
    "test" : [],
    "update_xml": [
    ],
    'installable': True,
    'active': False,
    'certificate': None,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
