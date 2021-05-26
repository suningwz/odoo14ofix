# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosAnalytic(models.Model):
    _inherit = 'account.move'

    orden_compra = fields.Char(string="Orden De Compra", compute="get_order_date")

    def get_order_date(self):
            self.orden_compra = self.env['sale.order'].search([('name', '=', self.invoice_origin)]).orden_compra
            #self.orden_compra = self.env['purchase.order'].search([('name', '=', self.invoice_origin)]).orden_compra
