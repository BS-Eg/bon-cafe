# -*- coding: utf-8 -*-


from odoo import models, api, _, _lt, fields


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"


    filter_date = {'mode': 'range', 'filter': 'this_year'}
    filter_all_entries = False
    filter_unfold_all = False
    filter_analytic = True
    filter_account_type = [
        {'id': 'receivable', 'name': _lt('Receivable'), 'selected': False},
        {'id': 'payable', 'name': _lt('Payable'), 'selected': False},
    ]
    filter_unreconciled = False
    filter_partner = True

