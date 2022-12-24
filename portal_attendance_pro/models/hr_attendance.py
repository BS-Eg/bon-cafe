import uuid
import werkzeug.urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons import decimal_precision as dp

GEOLOCATION = dp.get_precision("Gelocation")

class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread']
    
    def _get_default_access_token(self):
        return str(uuid.uuid4())
    
    access_url = fields.Char('Portal Access URL', compute='_compute_access_url',help='Contract Portal URL')
    access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)
    check_in_latitude = fields.Float("Check-in Latitude", digits=GEOLOCATION, readonly=True)
    check_in_longitude = fields.Float("Check-in Longitude", digits=GEOLOCATION, readonly=True)
    check_in_geofence_ids = fields.Many2many('hr.attendance.geofence', 'check_in_geofence_attendance_rel', 'attendance_id', 'geofence_id', string='Geofences')
    check_out_latitude = fields.Float("Check-out Latitude", digits=GEOLOCATION, readonly=True)
    check_out_longitude = fields.Float("Check-out Longitude", digits=GEOLOCATION, readonly=True)
    check_out_geofence_ids = fields.Many2many('hr.attendance.geofence', 'check_out_geofence_attendance_rel', 'attendance_id', 'geofence_id', string='Geofences')
    check_in_photo = fields.Binary(string="Check In Photo", readonly=False)
    check_out_photo = fields.Binary(string="Check Out Photo", readonly=False)
    check_in_map_link = fields.Char('Check In Location', compute='_compute_check_in_map_link')
    check_out_map_link = fields.Char('Check Out Location', compute='_compute_check_out_map_link')
    
    def _compute_access_url(self):
        for attendance in self:
            attendance.access_url = '/my/hr_attendance/%s' % attendance.id
    
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
        return self.env.ref('hr_attendance.hr_attendance_action')

    def preview_hr_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
        
    @api.depends('check_in_latitude','check_in_longitude')
    def _compute_check_in_map_link(self):
        for attendance in self:
            params = {
                'q': '%s,%s' % (attendance.check_in_latitude or '',attendance.check_in_longitude or ''),'z': 10,
            }
            attendance.check_in_map_link ='%s?%s' % ('https://maps.google.com/maps',werkzeug.urls.url_encode(params or None))

    @api.depends('check_out_latitude','check_out_longitude')
    def _compute_check_out_map_link(self):
        for attendance in self:
            params = {
                'q': '%s,%s' % (attendance.check_out_latitude or '',attendance.check_out_longitude or ''),'z': 10,
            }
            attendance.check_out_map_link = '%s?%s' % ('https://maps.google.com/maps',werkzeug.urls.url_encode(params or None))