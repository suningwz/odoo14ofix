# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class pos_config(models.Model):
    _inherit = "pos.config"

    coupon_program_ids = fields.Many2many(
        'coupon.program',
        'pos_config_coupon_program_rel',
        'pos_config_id',
        'coupon_id',
        domain=[('program_type', '=', 'promotion_program'), ('promo_applicability', '=', 'on_current_order')],
        string='Coupon Program')
