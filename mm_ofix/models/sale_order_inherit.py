# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosAnalytic(models.Model):
    _inherit = 'pos.order'

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,
                                          ondelete='set null',
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          check_company=True,
                                          help="Analytic account to which this project is linked for financial management. "
                                               "Use an analytic account to record cost and revenue on your project.")



