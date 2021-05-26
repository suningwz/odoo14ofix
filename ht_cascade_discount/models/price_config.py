# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplateInhePrice(models.Model):
    _inherit = "product.template"

     # price_presentation = fields.Many2one()
    price_config_ids = fields.One2many('price.configuration', "product_id")
    price_cost_of_sale = fields.Float("Net cost of sales")
    price_application_date = fields.Date("Date")



class PriceConfiguration(models.Model):
    _name = "price.configuration"
    _description = "Cost Configuration"

    product_id = fields.Many2one('product.template', string="Product")
    net_cost_sale = fields.Many2one('cost.configuration')
    scale_type = fields.Char("Scale Type")
    about_net = fields.Float("About Net")
    price_before_VAT = fields.Float("Price Before VAT")
    price_including_VAT = fields.Float("Price Including VAT")