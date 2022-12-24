# -*- coding: utf-8 -*-

import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class HrManagementSystem(http.Controller):

    @http.route(['/request_review/<id>'], type='http', auth="public", website=True)
    def request_review(self, **kw):
        request_id = int(kw['id'])
        values = request.env['hr.custody'].sudo().search([('id', '=', request_id)])
        print('testtt1')
        value = {
            'values': values,
        }
        return request.render("gs_hr_custody.request_review", value)

    @http.route('/request_approve', type='http', auth='public',website=True, csrf=False)
    def action_request_approve(self, *args, **post):
        print("request_idz")
        request_id = int(post.get('hr_custody'))
        request_obj = http.request.env['hr.custody'].sudo().search([('id', '=', request_id)])

        if request_obj:
            print('successsss')
            value = {
                'values': request_obj,
            }

            request_obj.renew_approve()
            # template_id = request.env.ref('gs_hr_custody.request_approve_mail')
            # template_id.send_mail(request_id, force_send=True)

            return http.request.render('gs_hr_custody.submit')

    @http.route('/request_refuse', type='http', auth='public',website=True, csrf=False)
    def action_request_refuse(self, *args, **post):
        print("request_idz")
        request_id = int(post.get('hr_custody'))
        request_obj = http.request.env['hr.custody'].sudo().search([('id', '=', request_id)])

        if request_obj:
            print('success1')
            value = {
                'values': request_obj,
            }

            request_obj.reject_request()
            # template_id = request.env.ref('gs_hr_custody.request_refuse_mail')
            # template_id.send_mail(request_id, force_send=True)

            return http.request.render('gs_hr_custody.submit')









