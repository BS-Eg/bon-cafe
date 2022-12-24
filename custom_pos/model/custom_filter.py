from datetime import datetime, timedelta
from dateutil.relativedelta import *
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosDetailsCustom(models.TransientModel):
    _inherit = 'pos.details.wizard'

    def calculate_date(self):
        context = self.env.context
        current_day = datetime.now()

        if context.get('day') == 'today':
            temp_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 00)
            self.start_date = temp_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            temp_end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 00) + timedelta(days=1)
            self.end_date = temp_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if context.get('day') == 'yesterday':
            temp_start = datetime(current_day.year, current_day.month, current_day.day, 0, 00) - timedelta(days=1)
            self.start_date = temp_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            temp_end = datetime(current_day.year, current_day.month, current_day.day, 0, 00)
            self.end_date = temp_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if context.get('day') == 'thisweek':
            today = datetime.now()
            last_monday = today - timedelta(days=today.weekday()) - timedelta(days=1)
            temp_start = datetime(last_monday.year, last_monday.month, last_monday.day, 0, 00)
            self.start_date = temp_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            temp_end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 00)
            self.end_date = temp_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if context.get('day') == 'thismonth':
            temp_start = datetime(datetime.now().year, datetime.now().month, 1, 0, 00)
            self.start_date = temp_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            temp_end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 00)
            self.end_date = temp_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if context.get('day') == 'lastmonth':
            temp_start = datetime(datetime.now().year, datetime.now().month, 1, 0, 00) - relativedelta(months=1)
            self.start_date = temp_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            temp_end = datetime(datetime.now().year, datetime.now().month, 1, 0, 00)
            self.end_date = temp_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return {
                'name': _('Sales Details'),
                'view_mode': 'form',
                'res_model': 'pos.details.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': self.id,
                'context': {},
            }

