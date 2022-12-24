from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route, Controller
from collections import OrderedDict
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter
from odoo.addons.portal.controllers.mail import _message_post_helper
from dateutil.relativedelta import relativedelta

from odoo.osv.expression import OR

import io
import re

from PyPDF2 import PdfFileReader, PdfFileWriter
from odoo.tools.safe_eval import safe_eval
from odoo import api, fields, models, SUPERUSER_ID, _

class HrPayrollPortal(Controller):

    @route(["/print/portal/payslips"], type='http', auth='user')
    def get_payroll_portal_report_print(self, list_ids='', **post):
        if not list_ids or re.search("[^0-9|,]", list_ids):
            return request.not_found()

        ids = [int(s) for s in list_ids.split(',')]
        payslips = request.env['hr.payslip'].sudo().browse(ids)

        pdf_writer = PdfFileWriter()

        for payslip in payslips:
            if not payslip.struct_id or not payslip.struct_id.report_id:
                report = request.env.ref('hr_payroll.action_report_payslip', False)
            else:
                report = payslip.struct_id.report_id
            report = report.sudo().with_context(lang=payslip.employee_id.sudo().address_home_id.lang)
            pdf_content, _ = report.with_user(SUPERUSER_ID).sudo()._render_qweb_pdf(payslip.id, data={'company_id': payslip.company_id})
            reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

            for page in range(reader.getNumPages()):
                pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()

        if len(payslips) == 1 and payslips.struct_id.report_id.print_report_name:
            report_name = safe_eval(payslips.struct_id.report_id.print_report_name, {'object': payslips})
        else:
            report_name = "Payslips"

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)

class PayslipPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)],limit=1)
        HrPayslip = request.env['hr.payslip']
        if 'payslip_count' in counters:
            payslip_count = HrPayslip.sudo().search_count([('employee_id', '=', employee.id)])
            values['payslip_count'] = payslip_count
        return values
    
    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):        
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)],limit=1)
        user = request.env.user
        HrPayslip = request.env['hr.payslip']
        
        domain = [
            ('employee_id', '=', employee and employee.id or False),
        ]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draf': {'label': _('Draf'), 'domain': [('state', '=', 'draf')]},
            'varify': {'label': _('Varify'), 'domain': [('state', '=', 'varify')]},
            'done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
            'paid': {'label': _('Paid'), 'domain': [('state', '=', 'paid')]},
            'cancel': {'label': _('Cancel'), 'domain': [('state', '=', 'cancel')]},
        }
        
        searchbar_inputs = {
            'state': {'input': 'State', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'state', 'label': _('State')},
        }
        
        # default sortby value
        if not sortby:
            sortby = 'date'        
        order = searchbar_sortings[sortby]['order']
        
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('status', 'all'):
                search_domain = OR([search_domain, [('state', 'ilike', search)]])
            domain += search_domain
        
        # count for pager
        leave_count = HrPayslip.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/payslips",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=leave_count,
            page=page,
            step=self._items_per_page
        )    
        
        # default group by value
        if groupby == 'state':
            order = "state, %s" % order
        payslips = HrPayslip.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        if groupby == 'none':
            grouped_payslips = []
            if payslips:
                grouped_payslips = [payslips]
        else:
            grouped_payslips = [HrPayslip.sudo().concat(*g) for k, g in groupbyelem(payslips, itemgetter('state'))]
        
        values.update({
            'payslips': payslips,
            'date': date_begin,
            'date_end': date_end,
            'grouped_payslips': grouped_payslips,
            'page_name': 'payslips',
            'default_url': '/my/payslips',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("portal_payslip.portal_my_payslips", values)

    @http.route(['/my/payslip/<int:payslip_id>'], type='http', auth="public", website=True)
    def portal_my_payslip(self, payslip_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if payslip_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_payslip_%s' % payslip_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_hr_payslip_%s' % payslip_sudo.id] = now
                body = _('Payslip viewed by Employee %s', payslip_sudo.employee_id.name)
                _message_post_helper(
                    "hr.payslip",
                    payslip_sudo.id,
                    body,
                    token=payslip_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=payslip_sudo.employee_id.sudo().user_id.ids,
                )
        
        history = request.session.get('my_payslip_history', [])     
        
        values = {
            'payslip': payslip_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'employee_id': payslip_sudo.employee_id.id,
            'report_type': 'html',
            'action': payslip_sudo._get_portal_return_action(),
        }
        if payslip_sudo.employee_id.company_id:
            values['res_company'] = payslip_sudo.employee_id.company_id
        values.update(get_records_pager(history, payslip_sudo))
        return request.render('portal_payslip.portal_my_payslip', values)
    