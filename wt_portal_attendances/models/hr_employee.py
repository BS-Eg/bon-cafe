from odoo import models, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def change_attandance_by_user(self):
        action_message = {}
        if self.user_id:
            modified_attendance = self.with_user(self.user_id).sudo()._attendance_action_change()
        else:
            modified_attendance = self.sudo()._attendance_action_change()
        action_message['attendance'] = modified_attendance.sudo().read()[0]
        return action_message

class HrPayslip(models.Model):
    _name="hr.payslip"
    _inherit = ['portal.mixin','hr.payslip']

    def _get_report_base_filename(self):
        return "{} - {}".format(("Payslip"), self.number)

    def _compute_access_url(self):
        super()._compute_access_url()
        for record in self:
            record.access_url = "/my/payslip/%s" % (record.id)