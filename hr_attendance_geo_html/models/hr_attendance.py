# -*- coding: utf-8 -*-
# Copyright 2019 Artem Shurshilov
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"


    geo_check_in = fields.Char(string="Geolocation check in")
    geo_check_out = fields.Char(string="Geolocation check out")
    map_url_check_in = fields.Html(string="Map url check in", compute='_compute_map_url_check_in', sanitize_attributes=False, store=True)
    map_url_check_out = fields.Html(string="Map url check out", compute='_compute_map_url_check_out', sanitize_attributes=False, store=True)
    geo_access_check_in = fields.Html(string="Geolocation in", readonly=True)
    geo_access_check_out = fields.Html(string="Geolocation out", readonly=True)

    @api.depends('geo_check_in')
    def _compute_map_url_check_in(self):
        for rec in self:
            if rec.geo_check_in:
                latitude = rec.geo_check_in.split()[0]
                longitude = rec.geo_check_in.split()[1]
                url = 'https://www.google.com/maps/search/?api=1&query={latitude},{longitude}'.format(latitude=latitude,longitude=longitude)
                rec.map_url_check_in = '<a href="'+url+'">'+url+'</a>'

    @api.depends('geo_check_out')
    def _compute_map_url_check_out(self):
        for rec in self:
            if rec.geo_check_out:
                latitude = rec.geo_check_out.split()[0]
                longitude = rec.geo_check_out.split()[1]
                url = 'https://www.google.com/maps/search/?api=1&query={latitude},{longitude}'.format(latitude=latitude,longitude=longitude)
                rec.map_url_check_out = '<a href="'+url+'">'+url+'</a>'
