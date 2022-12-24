# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    
    penalties_awards_ids = fields.Many2many('gs.penalties.awards', string='Penalties & Awards Deduction')
    deduction_amount = fields.Float('Deduction Amount', compute='get_penalties_awards_amount')
    awards_amount = fields.Float('Awards Amount', compute='get_penalties_awards_amount')

    def compute_sheet(self):
        for rec in self:
            penalties_awards_ids = self.env['gs.penalties.awards'].search([('employee_id', '=', rec.employee_id.id),
                                                                      ('state', '=', 'approve'),
                                                                      ('date', '>=', rec.date_from),
                                                                      ('date', '<=', rec.date_to),
                                                                      ])
            if penalties_awards_ids:
                rec.penalties_awards_ids = [(6, 0, penalties_awards_ids.ids)]
            return super(hr_payslip,self).compute_sheet()

    @api.depends('penalties_awards_ids')
    def get_penalties_awards_amount(self):
        for payslip in self:
            deduction_amount = 0
            awards_amount = 0
            if payslip.penalties_awards_ids:
                for penalties_awards in payslip.penalties_awards_ids:
                    if penalties_awards.type == 'deduction':
                        deduction_amount += penalties_awards.amount
                    elif penalties_awards.type == 'award':
                        awards_amount += penalties_awards.amount

            payslip.deduction_amount = deduction_amount
            payslip.awards_amount = awards_amount

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if self.employee_id:
                penalties_awards_ids = self.env['gs.penalties.awards'].search([('employee_id', '=', rec.employee_id.id),
                                                                               ('state', '=', 'approve'),
                                                                               ('date', '>=', rec.date_from),
                                                                               ('date', '<=', rec.date_to),
                                                                               ])
                if penalties_awards_ids:
                    rec.penalties_awards_ids = [(6, 0, penalties_awards_ids.ids)]

