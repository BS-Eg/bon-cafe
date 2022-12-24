from odoo import fields, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

class CustomerPortal(portal.CustomerPortal):
    @http.route(['/portal/attendance/check_in_check_out'], type='http', auth="user", website=True)
    def portal_attendance(self, **kw):
        return request.render('wt_portal_attendances.portal_attendace', {})

    @http.route(['/portal/attendance/employee'], type='json', auth="user", website=True)
    def portal_employee_info_attendance(self, **kw):
        rec = request.env['hr.employee.public'].sudo().search([('user_id', '=', request.env.user.id), ('company_id', '=', request.env.user.company_id.id)])
        if rec:
            return {
                'employee_id': rec.employee_id.id if rec.employee_id else False,
                'employee_name': rec.employee_id.name if rec.employee_id else '',
                'employee_state': rec.attendance_state,
                'employee_hours_today': rec.hours_today
           }
        else:
           return {
                'employee_id': '',
                'employee_name': '',
                'employee_state': '',
                'employee_hours_today':''
           }

    def _payslip_get_page_view_values(self, payslip, access_token, **kwargs):
        values = {
            'page_name': 'payslip',
            'payslip': payslip,
            'o':payslip
        }
        return self._get_page_view_values(payslip, access_token, values, 'my_payslip_history', False, **kwargs)

    def _prepare_payslips_domain(self, partner):
        return [
            ('state', 'in', ['draft', 'done', 'paid'])
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user
        HrAttendance = request.env['hr.attendance']
        HrAttendanceLeave = request.env['hr.leave']
        payslip = request.env['hr.payslip']
        if 'attendances_count' in counters:
            if not user.employee_id:
                values['attendances_count'] = 0
            else:
                values['attendances_count'] = HrAttendance.sudo().search_count(self._prepare_attendace_domain(user))
        if 'myleaves_count' in counters:
            if not user.employee_id:
                values['myleaves_count'] = 0
            else:
                values['myleaves_count'] = HrAttendanceLeave.sudo().search_count(self._prepare_attendace_leave_domain(user))

        if 'slip_count' in counters:
            values['slip_count'] = request.env['hr.payslip'].search_count(self._prepare_payslip_domain(user))\
                if payslip.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_attendace_leave_domain(self, user):
        return [
            ('employee_id', '=', user.employee_id.id)
        ]

    def _prepare_attendace_domain(self, user):
        return [
            ('employee_id', '=', user.employee_id.id)
        ]

    def _prepare_payslip_domain(self, user):
        return [
            ('employee_id', '=', user.employee_id.id)
        ]

    def _get_attendance_leave_searchbar_sortings(self):
        return {
            'date_from': {'label': _('Date From'), 'order': 'date_from desc'},
            'date_to': {'label': _('Date To'), 'order': 'date_to desc'},
            'duration_display': {'label': _('Duration'), 'order': 'duration_display desc'},
        }

    def _get_attendance_searchbar_sortings(self):
        return {
            'check_in': {'label': _('Check In'), 'order': 'check_in desc'},
            'check_out': {'label': _('Check Out'), 'order': 'check_in desc'},
            'worked_hours': {'label': _('Work Hourse'), 'order': 'worked_hours desc'},
        }

    @http.route(['/my/leaves', '/my/leaves/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_leave_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        HrAttendanceLeave = request.env['hr.leave']
        domain = self._prepare_attendace_leave_domain(user)
        searchbar_sortings = self._get_attendance_leave_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date_from'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        hr_leave_count = HrAttendanceLeave.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/leaves",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=hr_leave_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        HrLeaves = HrAttendanceLeave.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_hr_leave_history'] = HrLeaves.ids[:100]

        values.update({
            'date': date_begin,
            'HrLeaves': HrLeaves.sudo(),
            'page_name': 'myleave',
            'pager': pager,
            'default_url': '/my/leaves',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("wt_portal_attendances.portal_my_leave_attendances", values)

    @http.route(['/my/leave/<int:leave_id>'], type='http', auth="user", website=True)
    def portal_time_off_page(self, leave_id, **kw):
        try:
            leave_sudo = request.env['hr.leave'].browse(leave_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = {
            'leave_sudo': leave_sudo,
        }
        history = request.session.get('my_hr_leave_history', [])
        values.update(get_records_pager(history, leave_sudo))
        return request.render('wt_portal_attendances.my_leave_main_page', values)

    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        HrAttendance = request.env['hr.attendance']
        domain = self._prepare_attendace_domain(user)
        searchbar_sortings = self._get_attendance_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'check_in'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        attendances_count = HrAttendance.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=attendances_count,
            page=page,
            step=self._items_per_page
        )
        attendances = HrAttendance.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_attendances_history'] = attendances.ids[:100]

        values.update({
            'date': date_begin,
            'attendances': attendances.sudo(),
            'page_name': 'attendance',
            'pager': pager,
            'default_url': '/my/attendances',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("wt_portal_attendances.portal_my_attendances", values)

    @http.route('/my/payslip',  type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        HrPayslip = request.env['hr.payslip']
        domain = self._prepare_payslips_domain(partner)
        if not sortby:
            sortby = 'date'
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        slip_count = HrPayslip.sudo().search_count([])
        pager = portal_pager(
            url="/my/payslip",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=slip_count,
            page=page,
        )
        employee_ids = request.env['hr.employee'].search(
            [('user_id', '=', request.env.user.id)]).ids

        playslips = HrPayslip.search([('employee_id', 'in', employee_ids)])

        values = ({
            'date': date_begin,
            'playslips': playslips.sudo(),
            'page_name': 'slip',
            'pager': pager,
            'default_url': '/my/payslip',
            'sortby': sortby,
        })
        return request.render("wt_portal_attendances.portal_my_payslips",values)

    @http.route(['/my/payslip/<int:id>'], type='http', auth="public", website=True)
    def portal_my_payslip_detail(self, id, access_token=None, report_type=None, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type, report_ref='hr_payroll.action_report_payslip', download=download)

        values = self._payslip_get_page_view_values(payslip_sudo, access_token, **kw)

        return request.render("wt_portal_attendances.payslip_template", values)

