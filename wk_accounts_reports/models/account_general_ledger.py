# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True
    filter_unfold_all = False
    filter_partner = True

    
