from odoo import models, fields, api, _


class LetterType(models.Model):
    _name = 'letter.type'
    _inherit = [ 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    _rec_name='name'

    name = fields.Char(string='Letter Name',required=True,track_visibility='onchange',)
    type = fields.Selection([
        ('fixed', 'Fixed'),
        ('open', 'Open '),

    ], required=1,string='Letter Type',track_visibility='onchange',)
    letter_template = fields.Html(readonly=False)

    employee_id=fields.Many2one('hr.employee',string='Employee',track_visibility='onchange',)
    company_id = fields.Many2one('res.company', string='Company',
                                 track_visibility='onchange', )
    employee_salary=fields.Float(string='Employee Salary')
    employee_number=fields.Char('Employee ID')
    employee_position = fields.Char('Employee Job')
    bank=fields.Char()





