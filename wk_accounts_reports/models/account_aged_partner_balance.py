# -*- coding: utf-8 -*-


from odoo import models, api, fields, _
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_unfold_all = False
    filter_partner = True
    filter_analytic = True
    
