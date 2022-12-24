# Part of warlock. See LICENSE file for full copyright and licensing details.

import logging
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import datetime
import json
_logger = logging.getLogger(__name__)

class PortalTimeOff(http.Controller):
    @http.route(['/take/leave'], type='http', auth="user", website=True)
    def make_leave(self, **post):
        domain = ['|', ('requires_allocation', '=', 'no'), ('has_valid_allocation', '=', True)]
        leave_types = request.env['hr.leave.type'].search(domain)
        if not request.env.user.employee_id:
            return request.redirect('/my')
        values = {
            'leave_types': leave_types,
            'employee_id': request.env.user.employee_id
        }
        if post.get('submit'):
            dates = post.get('daterange').split('-')
            date_from = datetime.strptime(dates[0].strip(), '%m/%d/%Y').strftime('%Y-%m-%d 00:00:00')
            date_to = datetime.strptime(dates[1].strip(), '%m/%d/%Y').strftime('%Y-%m-%d 23:59:59')
            del post['submit']
            try:
                hr_leave_off_obj = request.env['hr.leave']
                domain = [
                ('date_from', '<', date_to),
                ('date_to', '>', date_from),
                ('employee_id', '=', request.env.user.employee_id.id),
                ('state', 'not in', ['cancel', 'refuse']),
                ]
                nholidays = hr_leave_off_obj.search_count(domain)
                if nholidays:
                    leave_type = request.env['hr.leave.type'].browse(int(post.get('leave_type')))
                    msg = request.env.user.employee_id.name + ' on '+ leave_type.name + ' '+ post.get('number_of_days') + ' days ' + datetime.strptime(dates[0].strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
                    raise ValidationError(
                        _('You can not set 2 time off that overlaps on the same day for the same employee.') + '\n- %s' % (msg))
                rec = hr_leave_off_obj.create({
                    'name': post.get('name'),
                    'holiday_status_id': int(post.get('leave_type')),
                    'date_from': date_from,
                    'date_to': date_to,
                    'duration_display': float(post.get('number_of_days')),
                    'holiday_type': 'employee',
                    'state': 'draft',
                    'employee_id': request.env.user.employee_id.id,
                    'employee_ids': [(6, 0, request.env.user.employee_id.ids)],
                    'request_date_from': datetime.strptime(dates[0].strip(), '%m/%d/%Y').strftime('%Y-%m-%d'),
                    'request_date_to': datetime.strptime(dates[1].strip(), '%m/%d/%Y').strftime('%Y-%m-%d'),
                    'user_id': request.env.user.id
                    })
                if rec:
                    return request.redirect('/my/leave/%s' %(rec.id))
            except Exception as e:
                values.update({
                    'error': str(e)
                    })
                return request.render('wt_portal_attendances.portal_time_off_form', values)   
        return request.render('wt_portal_attendances.portal_time_off_form', values)