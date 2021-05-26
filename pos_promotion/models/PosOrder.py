# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class pos_order_line(models.Model):

    _inherit = "pos.order.line"

    coupon_program_id = fields.Many2one('coupon.program', 'Coupon Program')
    coupon_id = fields.Many2one('coupon.coupon', 'Coupon')

    @api.model
    def create(self, vals):
        line = super(pos_order_line, self).create(vals)
        if vals.get('coupon_id', None):
            self.env['coupon.coupon'].browse(vals.get('coupon_id')).write({
                'state': 'used',
                'pos_order_id': vals.get('order_id'),
            })
        return line