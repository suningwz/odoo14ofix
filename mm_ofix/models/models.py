# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mm_ofix(models.Model):
    _inherit = 'stock.location'

    diario_venta = fields.Many2one('account.journal', 'name')
    diario_compra = fields.Many2one('account.journal', 'name')

