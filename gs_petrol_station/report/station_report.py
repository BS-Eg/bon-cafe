# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StationReportView(models.AbstractModel):
    _name = "report.gs_petrol_station.station_report"
    _description = "Station Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        stations = self.env['gs.pump'].search([('id', '=', docids)])

        for station in stations.pump_line_ids:
            docs.append({
                'pump': station.pump,
                'type_pump_id': station.type_pump_id.name,
                'nozzle_petrol_id': station.nozzle_petrol_id.name,
                'opening_pump': station.opening_pump,
                'ending_pump': station.ending_pump,
                'sales': station.sales,
                'user_id': station.user_id.name,

            })

        return {
            'docs1': docs,
            'station_id': stations.station_id.name,
            'sum_petrol_91': stations.sum_petrol_91,
            'sum_petrol_95': stations.sum_petrol_95,
            'sum_petrol_diesel': stations.sum_petrol_diesel,
        }
