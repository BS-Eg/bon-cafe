# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
  
  
    filter_all_entries = False
    filter_hierarchy = False
    filter_partner=True
    filter_analytic=True
    
