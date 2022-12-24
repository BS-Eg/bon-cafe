from odoo import models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super(Http, self).session_info()
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if self.env.user.has_group('base.group_user'):
            company = self.env.company
            result['portal_attendance_geolocation'] = company.portal_attendance_geolocation
            result['portal_attendance_geofence'] = company.portal_attendance_geofence
            result['portal_attendance_photo'] = company.portal_attendance_photo
        return result