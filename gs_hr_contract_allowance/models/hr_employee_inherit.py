# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time
import calendar


class GsEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    total_package_val = fields.Monetary(string="Total",)
    wage = fields.Monetary('Basic Salary', tracking=True, help="Employee's monthly gross wage.")
    house_allowance_val = fields.Monetary(string="House Amount")
    trans_allowance_val = fields.Monetary(string="Transportation Amount")
    contract_allowances = fields.One2many('hr.contract.allowance', 'employee_id')
    eos_total_amount = fields.Monetary('EOS Base Amount',)
    eos_total_amount_month = fields.Monetary('EOS Monthly')
    vacation_total_amount = fields.Monetary('Vacation Base Amount')
    run_compute = fields.Boolean(compute="_compute_action_get_data")
    total_paid = fields.Monetary(string="Total Paid")
    other_allowance = fields.Monetary(string="Other Allowance")
    ticket_base_amount = fields.Monetary(string="Ticket Base Amount")
    no_of_tickets = fields.Integer(string="No Of Tickets")
    annual_time_off_accrued = fields.Integer(string="Annual Time Off Accrued")
    medical_insurance_cost = fields.Integer(string="Medical insurance cost")

    employee_gosi_saudi = fields.Monetary(string="Employee Gosi (Saudi)")
    net_salary = fields.Monetary(string="Net Salary", compute='_get_net_salary')

    vacation_premium = fields.Monetary(string="Vacation Premium", compute='_get_vacation_premium')
    eos_premium = fields.Monetary(string="EOS Premium", compute='_get_eos_premium')
    ticket_premium = fields.Monetary(string="Ticket Premium", compute='_get_ticket_premium')
    iqama_renew_premium = fields.Monetary(string="Iqama Renew Premium")
    medical_insurance = fields.Monetary(string="Medical Insurance")
    gosi_company_share = fields.Monetary(string="Gosi Company Share",  compute='_get_gosi_company_share')
    total_unpaid = fields.Monetary(string="Total Unpaid",  compute='_get_total_unpaid')
    total_monthly_cost = fields.Monetary(string="Total Monthly Cost",  compute='_get_total_monthly_cost')

    children = fields.Integer(string='Number of Children', compute="_children_count")

    def _get_total_monthly_cost(self):
        for rec in self:
            rec.total_monthly_cost = rec.total_paid + rec.total_unpaid

    def _get_total_unpaid(self):
        for rec in self:
            rec.total_unpaid = rec.vacation_premium + rec.eos_premium + rec.ticket_premium + rec.iqama_renew_premium + \
                               rec.medical_insurance + rec.gosi_company_share + rec.total_unpaid

    def _get_gosi_company_share(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', rec.id)], limit=1)
            if contract:
                rec.gosi_company_share = rec.company_share_amount
            else:
                rec.gosi_company_share = 0

    def _get_ticket_premium(self):
        for rec in self:
            rec.ticket_premium = round(rec.ticket_base_amount / 11)

    def _get_net_salary(self):
        for rec in self:
            rec.net_salary = rec.total_paid - rec.employee_gosi_saudi

    def _get_eos_premium(self):
        for test in self:
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', test.id)], limit=1)
            rd = relativedelta(date.today(), contract.date_start)
            year = rd.years
            month = rd.months
            day = rd.days
            if year < 5:
                test.eos_premium = round((test.eos_total_amount / 2) / 12)
            if year >= 5:
                test.eos_premium = round(test.eos_total_amount / 12)

    def _get_vacation_premium(self):
        for rec in self:
            rec.vacation_premium = round(((rec.vacation_total_amount / 30) * rec.annual_time_off_accrued) / 11)

    def _children_count(self):
        for each in self:
            followers = self.env['gs.follower'].search([('employee_id', '=', each.id)])
            each.children = len(followers)

    def _compute_action_get_data(self):
        for rec in self:
            rec.total_paid = 0
            rec.run_compute = True
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', rec.id)], limit=1)
            if contract:
                rec.currency_id = contract.currency_id
                # rec.total_package_val = contract.total_package_val
                rec.wage = contract.wage
                rec.eos_total_amount = contract.eos_total_amount
                rec.eos_total_amount_month = contract.eos_total_amount_month
                rec.vacation_total_amount = contract.vacation_total_amount
                rec.ticket_base_amount = contract.tickets_val_company
                rec.no_of_tickets = contract.tickets_no_company
                rec.other_allowance = contract.other_allowance_val
                rec.annual_time_off_accrued = contract.vac_days

                rec.employee_gosi_saudi = rec.employee_share_amount

                if contract.is_paid_trans:
                    rec.trans_allowance_val = contract.trans_allowance_val
                else:
                    rec.trans_allowance_val = 0
                if contract.is_paid_housing:
                    rec.house_allowance_val = contract.house_allowance_val
                else:
                    rec.house_allowance_val = 0

                lines = [(5, 0, 0)]
                for line in contract.contract_allowances:
                    val = {
                        'allowance_id': line.allowance_id.id,
                        'amount': line.amount,
                        'is_paid': line.is_paid,
                    }
                    lines.append((0, 0, val))
                    rec.contract_allowances = lines

                if rec.wage:
                    rec.total_paid += rec.wage
                if rec.trans_allowance_val:
                    rec.total_paid += rec.trans_allowance_val
                if rec.house_allowance_val:
                    rec.total_paid += rec.house_allowance_val
                if rec.other_allowance:
                    rec.total_paid += rec.other_allowance
            else:
                rec.contract_allowances = [(5, 0, 0)]
                rec.wage = 0
                rec.eos_total_amount = 0
                rec.eos_total_amount_month = 0
                rec.vacation_total_amount = 0
                rec.ticket_base_amount = 0
                rec.no_of_tickets = 0
                rec.other_allowance = 0
                rec.annual_time_off_accrued = 0
                rec.employee_gosi_saudi = 0
                rec.trans_allowance_val = 0
                rec.house_allowance_val = 0
                rec.total_paid = 0

    def action_get_data(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', rec.id)], limit=1)
            rec.currency_id = contract.currency_id
            rec.total_package_val = contract.total_package_val
            rec.wage = contract.wage
            rec.house_allowance_val = contract.house_allowance_val
            rec.trans_allowance_val = contract.trans_allowance_val
            rec.eos_total_amount = contract.eos_total_amount
            rec.eos_total_amount_month = contract.eos_total_amount_month
            rec.vacation_total_amount = contract.vacation_total_amount

            lines = [(5, 0, 0)]
            for line in contract.contract_allowances:
                val = {
                    'allowance_id': line.allowance_id.id,
                    'amount': line.amount,
                    'is_paid': line.is_paid,
                }
                lines.append((0, 0, val))
                rec.contract_allowances = lines
