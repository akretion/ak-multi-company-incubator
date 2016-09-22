# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def mark_as_reconciled(self):
        return self.suspend_security().write({
            'last_reconciliation_date': time.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)})
