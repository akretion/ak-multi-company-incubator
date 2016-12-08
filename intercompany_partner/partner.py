# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    erp_company_partner_ids = fields.One2many(
        comodel_name='res.company', inverse_name='partner_id',
        string="ERP Company Partners",
        help="Partners associated to ERP companies")
