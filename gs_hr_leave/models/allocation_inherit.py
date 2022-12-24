# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_


class HrLeaveAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    create_by = fields.Selection([('manually', 'Manually'), ('automatically', 'Automatically')], string="Created", default="manually")
    start_date = fields.Date(string="Start Date",)
    end_date = fields.Date(string="End Date",)
    vacation_accrued = fields.Selection(string='Vacation Accrued', selection=[('monthly', 'Monthly'), ('yearly', 'Yearly')
                                                                            ,('every_2_years', 'Every 2 Years'), ],)
    contract_id = fields.Many2one('hr.contract', string='Contract',)

    @api.onchange('employee_id')
    def domain_employee_id(self):
        return {'domain': {'contract_id': [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')]}}

    def make_activity_allocation_user(self, user):
        date_deadline = fields.Date.today()
        note = _("Please Review This Allocations")
        summary = _("Allocations")

        self.sudo().activity_schedule(
            'mail.mail_activity_data_todo', date_deadline,
            note=note,
            user_id=user.id,
            res_id=self.id,
            summary=summary
        )

    @api.model
    def create(self, vals):
        res = super(HrLeaveAllocationInherit, self).create(vals)
        res.send_notif()
        return res

    def send_notif(self):
        for rec in self:
            if rec.state == 'draft':
                employees = self.env['res.groups'].search([('id', '=', self.env.ref('hr.group_hr_user').id)]).users
                for employee in employees:
                    self.make_activity_allocation_user(employee)

    def _cron_create_allocations(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        for contract in contracts:
            vals = []
            for renew in contract.renew_date_ids:
                if renew.date_start == fields.Date.today():
                    vals.append({
                        'name': 'Entitlement Time Off For ' + str(contract.employee_id.name) + ' From ' + str(renew.date_start) + ' To ' + str(renew.date_end),
                        'employee_id': contract.employee_id.id,
                        'state': 'draft',
                        'holiday_type': 'employee',
                        'create_by': 'automatically',
                        'contract_id': contract.id,
                        'start_date': renew.date_start,
                        'end_date': renew.date_end,
                        'number_of_days': contract.vac_days,
                        'number_of_days_display': contract.vac_days,
                        'vacation_accrued': contract.vacation_accrued,
                        'holiday_status_id': self.env.ref('gs_hr_entitlement.entitlement_time_off').id,
                    })
                    if vals:
                        self.env['hr.leave.allocation'].create(vals)
