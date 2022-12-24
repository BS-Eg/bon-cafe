from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter
from odoo.addons.portal.controllers.mail import _message_post_helper
from dateutil.relativedelta import relativedelta

from odoo.osv.expression import OR

class HrAttendanceController (http.Controller):
    @http.route('/portal_attendance_pro/search_read/get_employee_data', type='json', auth='user', website=True)
    def get_employee_data(self, employee_id, **post):
        if employee_id:
            hr_employee =  request.env['hr.employee'].sudo().search_read([('id', '=', int(employee_id))])
            return hr_employee
        else:
            return False

class HrAttendancePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],limit=1)
        HrAttendance = request.env['hr.attendance']       
        if 'hr_attendance_count' in counters:
            hr_attendance_count = HrAttendance.search_count([('employee_id', '=', employee and employee.id or False)])     
            values['hr_attendance_count'] = hr_attendance_count
        return values
    
    @http.route(['/my/hr_attendances', '/my/hr_attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_hr_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],limit=1)       
        HrAttendance = request.env['hr.attendance']
        
        domain = [
            ('employee_id', '=', employee and employee.id or False),
        ]
        
        searchbar_sortings = {
            'check_in': {'label': _('Check In'), 'order': 'check_in desc'},
            'check_out': {'label': _('Check Out'), 'order': 'check_out'},
        }
        
        searchbar_inputs = { 
            'check_in': {'input': 'check_in', 'label': _('Search in Check In Date')},
            'check_out': {'input': 'check_out', 'label': _('Search in Check Out Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        # default sortby order
        if not sortby:
            sortby = 'check_in'
        sort_order = searchbar_sortings[sortby]['order']
               
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("check_in", ">=", today),("check_out", "<=", today)]},
            'week': {'label': _('This week'), 'domain': [('check_in', '>=', date_utils.start_of(today, "week")), ('check_out', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('check_in', '>=', date_utils.start_of(today, 'month')), ('check_out', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('check_in', '>=', date_utils.start_of(today, 'year')), ('check_out', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('check_in', '>=', quarter_start), ('check_out', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('check_in', '>=', date_utils.start_of(last_week, "week")), ('check_out', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('check_in', '>=', date_utils.start_of(last_month, 'month')), ('check_out', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('check_in', '>=', date_utils.start_of(last_year, 'year')), ('check_out', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('all', 'all'):
                search_domain = OR([search_domain, ['|', ('check_in', 'ilike', search), ('check_out', 'ilike', search)]])
            if search_in in ('check_in', 'all'):
                search_domain = OR([search_domain, [('check_in', 'ilike', search)]])
            if search_in in ('check_out', 'all'):
                search_domain = OR([search_domain, [('check_out', 'ilike', search)]])
            domain += search_domain

        # count for pager
        hr_attendance_count = HrAttendance.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/hr_attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search},
            total=hr_attendance_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        hr_attendances = HrAttendance.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_hr_attendance_history'] = hr_attendances.ids[:100]
        
        values.update({
            'date': date_begin,
            'hr_attendances': hr_attendances.sudo(),
            'page_name': 'hr_attendances',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'default_url': '/my/hr_attendances',
        })
        return request.render("portal_attendance_pro.portal_my_hr_attendances", values)
    
    @http.route(['/my/hr_attendance/<int:attendance_id>'], type='http', auth="public", website=True)
    def portal_my_pos_order(self, attendance_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            attendance_sudo = self._document_check_access('hr.attendance', attendance_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if attendance_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_attendance_%s' % attendance_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_hr_attendance_%s' % attendance_sudo.id] = now
                body = _('HR Attendance viewed by Employee %s', attendance_sudo.employee_id.name)
                _message_post_helper(
                    "hr.attendance",
                    attendance_sudo.id,
                    body,
                    token=attendance_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=attendance_sudo.employee_id.sudo().user_id.ids,
                )
        
        values = {
            'hr_attendance': attendance_sudo,
            'token': access_token,
            'bootstrap_formatting': True,
            'employee_id': attendance_sudo.employee_id.id,
            'report_type': 'html',
            'action': attendance_sudo._get_portal_return_action(),
        }
        if attendance_sudo.employee_id.company_id:
            values['res_company'] = attendance_sudo.employee_id.company_id
        
        return request.render('portal_attendance_pro.portal_my_hr_attendance', values)
    
    @http.route(['/my/hr_attendances/create_new'], type='http', auth="user", website=True)
    def create_new_attendance(self, access_token=None):
        if not request.session.uid:
            return {'error': 'anonymous_user'}
        
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],limit=1)        
        values = {
            'employee': employee,
            'page_name': 'create_new_attendance',
        }
        return request.render("portal_attendance_pro.my_attendance_create_new", values)
