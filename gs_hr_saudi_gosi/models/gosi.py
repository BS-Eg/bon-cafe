from odoo import fields, api, models, _


class Saudi(models.Model):
    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department = fields.Char(string="Department", required=True, help="Department")
    position = fields.Char(string='Job Position', required=True, help="Job Position")
    nationality = fields.Char(string='Nationality', required=True, help="Nationality")
    type_gosi = fields.Char(string='Type', required=True, track_visibility='onchange', help="Gosi Type")
    dob = fields.Char(string='Date Of Birth', required=True, help="Date Of Birth")
    gos_numb = fields.Char(string='GOSI Number', required=True, track_visibility='onchange', help="Gosi number")
    issued_dat = fields.Char(string='Issued Date', required=True, track_visibility='onchange', help="Issued date")
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip')
        return super(Saudi, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                department = rec.employee_id
                rec.department = department.department_id.name if department.department_id else False
                rec.position = department.job_id.name
                rec.nationality = department.country_id.name
                rec.type_gosi = department.type
                rec.dob = department.birthday
                rec.gos_numb = department.gosi_number
                rec.issued_dat = department.issue_date


class Gosi(models.Model):
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi'),('not_saudi','Non Saudi')], string='Type', compute='_get_nationality', store=1, help="Select the type")
    gosi_number = fields.Char(string='GOSI Number', help="Gosi Number")
    issue_date = fields.Date(string='Issued Date', help="Issued Date")



    company_share_per = fields.Float('Company Share %',compute="_compute_share_amount",store=1)
    company_share_amount = fields.Float('Company Share Amount',compute="_compute_share_amount",store=1)
    employee_share_per = fields.Float('Employee Share %',compute="_compute_share_amount",store=1)
    employee_share_amount = fields.Float('Employee Share Amount',compute="_compute_share_amount",store=1)
    gosi_salary_amount = fields.Float('Gosi Salary', compute='_compute_gosi_salary')
    maximum_gosi_salary = fields.Float('Maximum Gosi Salary',compute="_compute_share_amount",store=1)
    gosi_conf = fields.Many2one('gosi.config', readonly=1, compute='_compute_gosi_config') # default=lambda self: self.env['gosi.config'].search([],limit=1), default=_default_gosi_config,
    run_com = fields.Boolean(compute="_compute_share_amount")

    def _compute_gosi_config(self):
        gosi_config = self.env['gosi.config'].search([], limit=1)
        if gosi_config:
            self.gosi_conf = gosi_config.id
        else:
            self.gosi_conf = False

    # This function calculating values depends on the percentage in the gosi configuration (Contract > Configuration > Gosi Configuration)
    @api.depends('gosi_salary_amount', 'type', 'gosi_conf.max_gosi_salary',
                 'gosi_conf.company_share_per', 'gosi_conf.company_share_per_non',
                 'gosi_conf.employee_share_per', 'gosi_conf.employee_share_per_non',)
    def _compute_share_amount(self):
        for line in self:
            # percentage = self.env['gosi.config'].search([],limit=1)
            line.run_com = True
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', line.id)], limit=1)
            if contract:
                percentage = line.gosi_conf
                if percentage:
                    line.maximum_gosi_salary = percentage.max_gosi_salary
                    line.company_share_per = 0
                    line.employee_share_per = 0
                    line.company_share_amount = 0
                    line.employee_share_amount = 0
                    if line.gosi_salary_amount > line.maximum_gosi_salary:
                        if line.type == 'saudi':
                            if percentage.company_share_per > 0:
                                line.company_share_per = percentage.company_share_per
                                line.company_share_amount = (percentage.company_share_per / 100) * line.maximum_gosi_salary
                            if percentage.employee_share_per > 0:
                                line.employee_share_per = percentage.employee_share_per
                                line.employee_share_amount = (percentage.employee_share_per / 100) * line.maximum_gosi_salary
                        elif line.type == 'not_saudi':
                            line.company_share_per = 0
                            line.employee_share_per = 0
                            if percentage.company_share_per_non > 0:
                                line.company_share_per = percentage.company_share_per_non
                                line.company_share_amount = (percentage.company_share_per_non / 100) * line.maximum_gosi_salary
                            if percentage.employee_share_per_non > 0:
                                line.employee_share_per = percentage.employee_share_per_non
                                line.employee_share_amount = (percentage.employee_share_per_non / 100) * line.maximum_gosi_salary

                    else:
                        if line.type == 'saudi':
                            if percentage.company_share_per > 0:
                                line.company_share_per = percentage.company_share_per
                                line.company_share_amount = (percentage.company_share_per / 100) * line.gosi_salary_amount
                            if percentage.employee_share_per > 0:
                                line.employee_share_per = percentage.employee_share_per
                                line.employee_share_amount = (percentage.employee_share_per / 100) * line.gosi_salary_amount
                        elif line.type == 'not_saudi':
                            line.company_share_per = 0
                            line.employee_share_per = 0
                            if percentage.company_share_per_non > 0:
                                line.company_share_per = percentage.company_share_per_non
                                line.company_share_amount = (percentage.company_share_per_non / 100) * line.gosi_salary_amount
                            if percentage.employee_share_per_non > 0:
                                line.employee_share_per = percentage.employee_share_per_non
                                line.employee_share_amount = (percentage.employee_share_per_non / 100) * line.gosi_salary_amount
            else:
                line.company_share_per = 0.0
                line.employee_share_per = 0.0
                line.company_share_amount = 0.0
                line.employee_share_amount = 0.0
                line.maximum_gosi_salary = 0.0

    # @api.depends('wage','house_allowance_val','is_paid_housing')
    def _compute_gosi_salary(self):
        for line in self:
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', line.id)], limit=1)
            line.gosi_salary_amount = contract.wage
            line.gosi_salary_amount = contract.wage + contract.house_allowance_val

    age = fields.Float(string='AGE', digits=(2,1), compute='_calc_age',store=1)
    limit = fields.Boolean(string='Eligible For GOSI', compute='_compute_age', default=False)

    def _compute_age(self):
        for res in self:
            if int(res.age) <= 60 and int(res.age) >= 18:
                res.limit = True
            else:
                res.limit = False

    @api.depends('birthday')
    def _calc_age(self):
        for line in self:
            line.age = 0
            if line.birthday:
                line.age = (fields.Date.today() - line.birthday).days / 365
            print('line.age: ',line.age)

    @api.depends('country_id')
    def _get_nationality(self):
        for line in self:
            if line.country_id.name == 'Saudi Arabia':
                line.type = 'saudi'
            else:
                line.type = 'not_saudi'

            print('line.type: ',line.type)

class Pay(models.Model):
    _inherit = 'hr.payslip'

    gosi_no = fields.Many2one('gosi.payslip', string='GOSI Reference', readonly=True, help="Gosi Number")
    employee_share_amount = fields.Float('Employee Share Amount')

    @api.onchange('employee_id')
    def onchange_employee_ref(self):
        for rec in self:
            gosi_no = rec.env['gosi.payslip'].search([('employee_id', '=', rec.employee_id.id)])
            rec.gosi_no = gosi_no.id
            rec.employee_share_amount = rec.employee_id.employee_share_amount

