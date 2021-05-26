# -*- coding: utf-8 -*-

from odoo import models, fields, api


class addendas(models.Model):
    #_inherit = 'purchase.order'
    _inherit = 'sale.order'

    orden_compra = fields.Char(string='Orden De Compra')
