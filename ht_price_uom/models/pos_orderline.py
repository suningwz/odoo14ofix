from odoo import _
from odoo.tools import float_is_zero
from odoo import models, fields, api


class PosOrderLinesExtended(models.Model):
    _inherit = 'pos.order.line'

    uom_id = fields.Many2one('uom.uom', string="UOM")

    @api.model
    def create(self, values):
        """updating uom to orderlines"""
        try:
            if values.get('uom_id'):
                values['uom_id'] = values['uom_id'][0]
        except Exception:
            values['uom_id'] = None
            pass
        res = super(PosOrderLinesExtended, self).create(values)
        return res
