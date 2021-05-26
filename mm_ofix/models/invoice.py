# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Invoice(models.Model):
    _inherit = 'account.move'
    mm_envio = fields.Char("Envío")
    mm_embalaje = fields.Char("Embalaje")
    mm_destino = fields.Char("Destino")
