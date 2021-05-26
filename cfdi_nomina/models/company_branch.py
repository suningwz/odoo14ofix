# -*- coding: utf-8 -*-
################################################
# Coded by: Jose Gpe Osuna joseg.osuna@gmail.com
################################################
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo import api, models, fields, _


class CompanyBranch(models.Model):
    _name = 'company.branch'
    _description = 'Company Branch'
    
    code = fields.Char("Code")
    name = fields.Char("Name")
    company_id = fields.Many2one("res.company",string="Company",default=lambda self: self.env.company)
    riesgo_puesto = fields.Many2one(
        "cfdi_nomina.riesgo.puesto", string="Risk class")
    registro_patronal = fields.Many2one('hr.ext.mx.regpat')
    xs_id_region = fields.Selection(selection=[
            ('shallows', 'Bajío'),
            ('center 1', 'Centro 1'),
            ('center 2', 'Centro 2'),
            ('gulf', 'Golfo'),
            ('northeast', 'Noreste'),
            ('south','Sur'),
            ('southeast','Sureste'),
        ], string='Region',store=True ,default="shallows")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name or ''
            if rec.code:
                name += ' ' + rec.code
            result.append((rec.id, name))
        return result
    
