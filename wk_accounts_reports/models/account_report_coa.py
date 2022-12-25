# -*- coding: utf-8 -*-

from copy import deepcopy
import io
from odoo import models, fields, api, _
from odoo.tools.misc import xlsxwriter




class AccountChartOfAccountReport(models.AbstractModel):
    _inherit = "account.coa.report"
    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_partner=True
    MAX_LINES = None

   
