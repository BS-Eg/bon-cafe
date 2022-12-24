from odoo import models, fields, api, _


class LetterTypeTemplate(models.Model):
    _name = 'letter.type.template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'type_id'

    type_id = fields.Many2one('letter.type',string='Letter', track_visibility='onchange', )

    type = fields.Selection([
        ('fixed', 'Fixed'),
        ('open', 'Open '),

    ], string='Letter Type', track_visibility='onchange',related='type_id.type' )
    letter_template=fields.Html()
    date=fields.Date()
    employee_id=fields.Many2one('hr.employee',string='Employee', track_visibility='onchange',)
    employee_department_id=fields.Many2one('hr.department',string='Employee Department', track_visibility='onchange',)
    company_id = fields.Many2one('res.company', string='Company',
                                track_visibility='onchange', default=lambda self: self.env.company, )
    employee_salary = fields.Float(string='Employee Salary', track_visibility='onchange',)
    employee_number = fields.Char('Employee ID', track_visibility='onchange',)
    bank = fields.Char( track_visibility='onchange',)
    employee_position = fields.Char('Employee Job')

    @api.onchange('type_id')
    def get_letter_type(self):
        self.letter_template=self.type_id.letter_template
        self.employee_id=self.type_id.employee_id
        self.company_id=self.type_id.company_id
        self.employee_number=self.type_id.employee_number
        self.bank=self.type_id.bank
        self.type=self.type_id.type
        self.employee_position=self.type_id.employee_position
