from odoo import api, models, fields, _

class HRDepartment(models.Model):
    
    _inherit = 'hr.department'
    
    branch_ids = fields.Many2many('company.branch','rel_hr_department_company_branch','department_id','branch_id',string='Branch')
