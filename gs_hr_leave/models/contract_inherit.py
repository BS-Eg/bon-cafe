# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models ,_
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time


class GsContractsInherit(models.Model):
    _inherit = 'hr.contract'

    allocation_count = fields.Integer(compute='get_gs_allocation_count')

    def open_gs_allocation(self):
        return {
            'name': _('Allocations'),
            'domain': [('contract_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hr.leave.allocation',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_number_of_days_display': self.vac_days,
            }
        }

    def get_gs_allocation_count(self):
        count = self.env['hr.leave.allocation'].search_count([('contract_id', '=', self.id)])
        self.allocation_count = count
