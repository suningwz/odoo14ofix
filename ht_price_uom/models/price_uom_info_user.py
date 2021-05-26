# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PriceUomInfoUser(models.Model):
    _name = "price.uom.user"

    product_tmpl_id = fields.Many2one("product.template", string="Product", required=1, ondelete="cascade")
    uom_id_selected = fields.Many2one("uom.uom", string="Unit Of Measures", required=1, ondelete="cascade")
    visitor_id = fields.Many2one("website.visitor", string="Visitor", required=1, ondelete="cascade")

    _sql_constraints = [
        # Partial constraint, complemented by a python constraint (see below).
        ('login_key', 'unique (visitor_id, product_tmpl_id)', 'You can not have two users with the same Product!'),
    ]
