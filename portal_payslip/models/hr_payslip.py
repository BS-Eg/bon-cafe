import uuid
from odoo import models, fields

class User(models.Model):
    _inherit = ['res.users']

    marital = fields.Selection(related='employee_id.marital', readonly=False, related_sudo=False)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['marital']

class HrPaylsip(models.Model):
    _inherit = 'hr.payslip'

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    access_url = fields.Char('Portal Access URL', compute='_compute_access_url',help='Contract Portal URL')
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)

    def _compute_access_url(self):
        for record in self:
            record.access_url = '/my/payslip/%s' % record.id
    
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

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('hr_payroll.act_hr_employee_payslip_list')