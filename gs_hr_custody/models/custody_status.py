# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class HrCustodyStatus(models.Model):
    _name = 'hr.custody.status'

    name = fields.Char(string="Name")
