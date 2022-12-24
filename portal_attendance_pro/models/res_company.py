from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    portal_attendance_geolocation = fields.Boolean(string="Geolocation", default=False)
    portal_attendance_geofence = fields.Boolean(string="Geofence", default=False)
    portal_attendance_photo = fields.Boolean(string="Photo", default=False)