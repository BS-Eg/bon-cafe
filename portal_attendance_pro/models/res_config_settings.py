from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    portal_attendance_geolocation = fields.Boolean(related="company_id.portal_attendance_geolocation", string="Geolocation", readonly=False)
    portal_attendance_geofence = fields.Boolean(related="company_id.portal_attendance_geofence", string="Geofence", readonly=False)
    portal_attendance_photo = fields.Boolean(related="company_id.portal_attendance_photo", string="Photo", readonly=False)