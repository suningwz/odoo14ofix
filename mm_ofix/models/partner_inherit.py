# -*- coding: utf-8 -*-

from odoo import models, fields, api


class addendas(models.Model):
    _inherit = 'res.partner'

    numProvedor = fields.Integer(string='numProvedor', help='Numero de provedor')
