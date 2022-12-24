# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    gs_employee_ids = fields.Many2many('hr.employee', 'gs_emp_employee_ids_01', 'gs_emp_employee_ids_001', 'gs_emp_employee_ids_0001', string='Alternative Employee')
