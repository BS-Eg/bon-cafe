# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DailySalesReportView(models.AbstractModel):
    _name = "report.gs_petrol_station.daily_sales_report"
    _description = "Daily Sales Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        daily_sales = self.env['gs.daily.sales'].search([('id', '=', docids)])

        for daily_sale in daily_sales.daily_sales_ids:
            docs.append({
                'date': daily_sale.date,
                'type_pump_id': daily_sale.type_pump_id.name,
                'nozzle_petrol_id': daily_sale.nozzle_petrol_id.name,
                'product_id': daily_sale.product_id.name,
                'opening_pump': daily_sale.opening_pump,
                'ending_pump': daily_sale.ending_pump,
                'sales': daily_sale.sales,
                'user_id': daily_sale.user_id.name,

            })

        return {
            'docs1': docs,
            'station_id': daily_sales.station_id.name,
            'date': daily_sales.date,
            'order_id': daily_sales.order_id.name,



            'sum_petrol_91': daily_sales.sum_petrol_91,
            'sum_petrol_end_91': daily_sales.sum_petrol_end_91,
            'sum_petrol_sales_91': daily_sales.sum_petrol_sales_91,
            'price_sales_91': daily_sales.price_sales_91,

            'sum_petrol_95': daily_sales.sum_petrol_95,
            'sum_petrol_end_95': daily_sales.sum_petrol_end_95,
            'sum_petrol_sales_95': daily_sales.sum_petrol_sales_95,
            'price_sales_95': daily_sales.price_sales_95,

            'sum_petrol_diesel': daily_sales.sum_petrol_diesel,
            'sum_petrol_end_diesel': daily_sales.sum_petrol_end_diesel,
            'sum_petrol_sales_diesel': daily_sales.sum_petrol_sales_diesel,
            'price_sales_diesel': daily_sales.price_sales_diesel,
        }
