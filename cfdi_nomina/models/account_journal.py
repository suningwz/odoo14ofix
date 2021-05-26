from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'

    place = fields.Char('Expedition place', size=128)
    serie = fields.Char(size=32)

class AccountMove(models.Model):
    
    _inherit = 'account.move'
    
    branch_id = fields.Many2one('company.branch','Branch')
    