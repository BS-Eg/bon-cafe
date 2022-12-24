import uuid

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import pytz

from pytz import timezone, UTC
from datetime import datetime, time, timedelta, date


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"
    
    def _get_default_access_token(self):
        return str(uuid.uuid4())
    
    access_url = fields.Char('Portal Access URL', compute='_compute_access_url',help='Contract Portal URL')
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)
    
    def _compute_access_url(self):
        for leave in self:
            leave.access_url = '/my/leave/%s' % leave.id
    
    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token
    
    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
    
    def convert_tz_utc(self, tz_date):
        fmt = "%Y-%m-%d %H:%M:%S"
        now_utc = datetime.now(timezone('UTC'))
        now_timezone = now_utc.astimezone(timezone(self.env.user.tz))
        UTC_OFFSET_TIMEDELTA = datetime.strptime(now_utc.strftime(fmt), fmt) - datetime.strptime(now_timezone.strftime(fmt), fmt)
        result_utc_datetime = tz_date + UTC_OFFSET_TIMEDELTA
        return result_utc_datetime.strftime(fmt)
    
    @api.model
    def update_timeoff_portal(self, values):
        self = self.sudo()
        user = self.env.user
        if not (self.env.user.employee_id):
            raise AccessDenied()
        
        if not (values['holiday_status_id'] and values['name']):
            return {
                'errors': _('All fields are required !')
            }
            
        # Values from Portal Form
        leave_id = values['leave_id']
        name = values['name']
        holiday_status_id = values['holiday_status_id']
        request_date_from = values['request_date_from']
        request_date_to = values['request_date_to']
        request_unit_half = values['request_unit_half']
        request_date_from_period = values['request_date_from_period']
        request_unit_hours = values['request_unit_hours']
        request_hour_from = values['request_hour_from']
        request_hour_to = values['request_hour_to']
        
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)],limit=1)        
        hr_leave_type = self.env['hr.leave.type'].search([('id', '=', holiday_status_id)],limit=1)
        if (hr_leave_type.request_unit == 'hour' or hr_leave_type.request_unit == 'half_day'):
            request_date_to = values['request_date_from']    
        
        dt_from = fields.Datetime.from_string(request_date_from)
        dt_to = fields.Datetime.from_string(request_date_to)

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        date_from = pytz.utc.localize(dt_from).astimezone(timezone)
        date_to = pytz.utc.localize(dt_to).astimezone(timezone)                
        
        values = {
            'holiday_status_id': int(holiday_status_id),
            'request_date_from':  date_from,
            'request_date_to': date_to,
            'name': name,
            'holiday_type' : 'employee',
            'employee_id' : employee.id,
            'request_unit_half': request_unit_half,
            'request_date_from_period': request_date_from_period,
            'request_unit_hours': request_unit_hours,
            'request_hour_from': request_hour_from,
            'request_hour_to': request_hour_to,                
        }
        values.update(self.env['hr.leave'].with_user(employee.user_id)._default_get_request_parameters(values))

        

        tmp_leave = self.env['hr.leave'].with_user(employee.user_id).new(values)
        tmp_leave._compute_date_from_to()
        values  = tmp_leave._convert_to_write(tmp_leave._cache)
        
        if leave_id:
            leave = self.env['hr.leave'].sudo().browse(int(leave_id)).write(values)        
            return {
                'leave': leave
            }
        else:
            raise UserError(_('Something went wrong during your Time off updation.'))
        
    @api.model
    def create_timeoff_portal(self, values):
        self = self.sudo()
        user = self.env.user
        if not (self.env.user.employee_id):
            raise AccessDenied()
        
        if not (values['holiday_status_id'] and values['name']):
            return {
                'errors': _('All fields are required !')
            }
            
        # Values from Portal Form
        name = values['name']
        holiday_status_id = values['holiday_status_id']
        request_date_from = values['request_date_from']
        request_date_to = values['request_date_to']
        request_unit_half = values['request_unit_half']
        request_date_from_period = values['request_date_from_period']
        request_unit_hours = values['request_unit_hours']
        request_hour_from = values['request_hour_from']
        request_hour_to = values['request_hour_to']
        
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)],limit=1)        
        hr_leave_type = self.env['hr.leave.type'].search([('id', '=', holiday_status_id)],limit=1)
        if (hr_leave_type.request_unit == 'hour' or hr_leave_type.request_unit == 'half_day'):
            request_date_to = values['request_date_from']
        
        dt_from = fields.Datetime.from_string(request_date_from)
        dt_to = fields.Datetime.from_string(request_date_to)

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC') 
        date_from = pytz.utc.localize(dt_from).astimezone(timezone)
        date_to = pytz.utc.localize(dt_to).astimezone(timezone)
        
        values = {
            'holiday_status_id': int(holiday_status_id),
            'request_date_from':  date_from,
            'request_date_to': date_to,
            'name': name,
            'holiday_type' : 'employee',
            'employee_id' : employee.id,
            'request_unit_half': request_unit_half,
            'request_date_from_period': request_date_from_period,
            'request_unit_hours': request_unit_hours,
            'request_hour_from': request_hour_from,
            'request_hour_to': request_hour_to,                
        }
        values.update(self.env['hr.leave'].with_user(employee.user_id)._default_get_request_parameters(values))
        tmp_leave = self.env['hr.leave'].with_user(employee.user_id).new(values)
        tmp_leave._compute_date_from_to()
        values  = tmp_leave._convert_to_write(tmp_leave._cache)
        leave = self.env['hr.leave'].sudo().create(values)
        return {
            'id': leave.id,
            'access_token': leave.sudo()._portal_ensure_token(),
        }
    
    @api.model
    def unlink_portal(self, values):
        leave_id = values['leave_id']
        if self.user_has_groups('base.group_portal'):
            leave = self.env['hr.leave'].sudo().browse(int(leave_id))            
            if leave.state == 'confirm':
                leave.sudo().action_draft()
                unlink = leave.sudo().unlink()
                if unlink:
                    return True
                else:
                    return  False
                
                