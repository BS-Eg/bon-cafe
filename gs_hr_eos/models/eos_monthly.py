# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta, time
import calendar
from odoo.exceptions import UserError


class GsEOSMonthly(models.Model):
    _name = 'gs.eos.monthly'
    _description = 'End Of Service Monthly'

    name = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    eos_total_amount_month = fields.Monetary('EOS Monthly', readonly=1)
    date = fields.Date(string='Date')
    journal_id = fields.Many2one('account.journal', copy=False)


    @api.model
    def create(self, vals):
        res = super(GsEOSMonthly, self).create(vals)
        res.get_name()
        return res

    def get_name(self):
        for rec in self:
            rec.name = "End of service for " + str(rec.employee_id.name)

    def _check(self):
        if self.env['ir.config_parameter'].sudo().get_param('gs_hr_eos.journal_id'):
            self.create_eos_monthly()
        else:
            raise UserError(_("Enable configuration settings (EOS Monthly Accrual)"))

    def create_eos_monthly(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        today = fields.Date.today()
        emp_ids = []
        lines = [(5, 0, 0)]
        journal_id = int(self.env['ir.config_parameter'].sudo().get_param('gs_hr_eos.journal_id'))
        account_id = int(self.env['ir.config_parameter'].sudo().get_param('gs_hr_eos.account_id'))
        account_journal = self.env['account.journal'].search([('id', '=', journal_id)])
        for con2 in contracts:
            con2._onchange_eos_total_amount()
            emp_ids.append(con2.employee_id.id)

        employee = self.env['hr.employee'].search([('id', 'in', emp_ids)])
        for emp in employee:
            emp._compute_action_get_data()
            emp.action_get_data()
            if emp.contract_id.date_start and emp.contract_id.date_end:
                if emp.contract_id.date_end >= today:
                    if emp.eos_total_amount_month:
                        val = {
                            'name':  "End of service for " + str(emp.name),
                            'employee_id': emp.id,
                            'eos_total_amount_month': emp.eos_total_amount_month,
                            'date': today,
                        }

                        eos = self.env['gs.eos.monthly'].search([('employee_id', '=', emp.id)])
                        if not eos:
                            self.env['gs.eos.monthly'].create(val)

            elif emp.contract_id.date_start and not emp.contract_id.date_end:
                if emp.contract_id.date_start <= today:
                    if emp.eos_total_amount_month:
                        val = {
                            'name': "End of service for " + str(emp.name),
                            'employee_id': emp.id,
                            'eos_total_amount_month': emp.eos_total_amount_month,
                            'date': today,
                        }

                        eos = self.env['gs.eos.monthly'].search([('employee_id', '=', emp.id)])
                        if not eos:
                            self.env['gs.eos.monthly'].create(val)

        eos_monthly = self.env['gs.eos.monthly'].search([('date', '=', today)])
        for eos in eos_monthly:
            move_line_1 = {
                'name': eos.name,
                'partner_id': eos.employee_id.address_home_id.id,
                'account_id': account_id,
                'debit': 0.0,
                'credit': eos.eos_total_amount_month,
            }
            move_line_2 = {
                'name': eos.name,
                'partner_id': eos.employee_id.address_home_id.id,
                'account_id': account_journal.gs_def_debit_acc.id,
                'credit': 0.0,
                'debit': eos.eos_total_amount_month,
            }
            lines.append((0, 0, move_line_1))
            lines.append((0, 0, move_line_2))

        move_vals = {
            'ref': 'EOS Monthly',
            'move_type': 'entry',
            'journal_id': journal_id,
            'date': today,
            'line_ids': lines,
        }

        account_move = self.env['account.move'].search([('date', '=', today), ('ref', '=', 'EOS Monthly')])
        if not account_move:
            self.env['account.move'].create(move_vals)