# -*- coding: utf-8 -*-
# Copyright 2020 Artem Shurshilov
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

from odoo import http
from pyproj import Proj
from pyproj import Proj, transform

from odoo.http import request
from shapely.geometry import Point

from odoo.addons.hr_attendance_base.controllers.controllers import HrAttendanceBase


class HrAttendanceGeospatial(HrAttendanceBase):
    @http.route('/hr_attendance_base', auth='user', type="json")
    def index(self, **kw):
        res = super(HrAttendanceGeospatial, self).index(**kw)
        geospatial_access_enable = request.env['ir.config_parameter'].sudo().get_param(str(request.env.user.company_id.id)+'hr_attendance_geospatial_access')
        res.update({'geospatial_enable': True if geospatial_access_enable else False})
        if kw.get('latitude') and kw.get('longitude'):
            P3857 = Proj(init='epsg:3857')
            P4326 = Proj(init='epsg:4326')
            x,y = transform(P4326, P3857, kw.get('longitude'), kw.get('latitude'))
            point3 = Point(x, y)
            the_geom_ids = []
            for i in request.env['hr.attendance.geospatial'].sudo().search([('company_id', '=', request.env.user.company_id.id)]):
                if i.employee_ids:
                    users = i.employee_ids.mapped('user_id')
                    if  request.env.user in users:
                        if point3.within(i.the_geom2) or i.the_geom2.contains(point3):
                            the_geom_ids = i
                            break
                else:
                    if point3.within(i.the_geom2) or i.the_geom2.contains(point3):
                        the_geom_ids = i
                        break

            # the_geom_ids = request.env['hr.attendance.geospatial'].sudo().search([]).geo_search(
            #     geo_domain=[('the_geom', 'geo_contains', point)], limit=1)

            res.update({'geospatial_access': True if the_geom_ids else False})
            if the_geom_ids:
                res.update({'geospatial_description': the_geom_ids.description if the_geom_ids else False})
                res.update({'geospatial_name': the_geom_ids.name if the_geom_ids else False})
                res.update({'geospatial_id': the_geom_ids.id if the_geom_ids else False})
        return res
