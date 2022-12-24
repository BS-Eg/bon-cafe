# -*- coding: utf-8 -*-

import requests
import datetime
from odoo import fields, models, _
from odoo.exceptions import UserError
import json
import logging
import time
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class FoodicsConnector(models.Model):
    _name = 'foodics.connector'
    _description = "Foodics Connector"

    name = fields.Char('Name', required="True")
    data_access_url = fields.Char('Access Url')
    import_option = fields.Selection([
        ('branches', 'Branches'),
        ('payment_methods', 'Payment Methods'),
        ('categories', 'Categories'),
        ('products', 'Products'),
        ('product_modifiers', 'Product Modifier'),
        ('orders', 'Orders'),
    ], string="Import Option", default='branches')
    order_date = fields.Date()
    access_token = fields.Char(string='Access Token')
    updated_after = fields.Date()
    from_date = fields.Date(string='Updated After')
    to_date = fields.Date(string='To Date')
    page = fields.Integer(default=1)
    note = fields.Text()

    def authenticate(self, url):
        config = self.env['ir.config_parameter'].search([('key', '=', 'foodics_token')])
        if config:
            access_token = config.value
        else:
            access_token = self.access_token

        headers = {
            'authorization': "Bearer %s" % access_token,
            'content-type': 'text/plain',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        # else:
        #     raise UserError(_('something went wrong !'))

    def success_popup(self, data):
        return {
            "name": "Message",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "pop.message",
            "target": "new",
            "context": {
                "default_name": "Successfully %s Imported!"%data
            },
        }

    def get_branches(self):
        res = self.authenticate(self.data_access_url)
        Branch = self.env['pos.config']
        Branch.set_branches_to_odoo(res)
        last_page = int(res.get('meta').get('last_page'))
        if last_page > 1:
            for page_no in range(int(res.get('meta').get('current_page')) + 1, last_page + 1):
                res = self.authenticate(self.data_access_url + "?page={}".format(page_no))
                Branch.set_branches_to_odoo(res)
        return self.success_popup('Branches')

    def get_payment_methods(self):
        res = self.authenticate(self.data_access_url)
        PaymentMethods = self.env['pos.payment.method']
        PaymentMethods.set_payment_methods_to_odoo(res)
        last_page = int(res.get('meta').get('last_page'))
        if last_page > 1:
            for page_no in range(int(res.get('meta').get('current_page')) + 1, last_page + 1):
                res = self.authenticate(self.data_access_url + "?page={}".format(page_no))
                PaymentMethods.set_payment_methods_to_odoo(res)
        return self.success_popup('Payment Methods')

    def get_categories_methods(self):
        res = self.authenticate(self.data_access_url)
        PosCategory = self.env['pos.category']
        PosCategory.set_categories_to_odoo(res)
        last_page = int(res.get('meta').get('last_page'))
        if last_page > 1:
            for page_no in range(int(res.get('meta').get('current_page')) + 1, last_page + 1):
                res = self.authenticate(self.data_access_url + "?page={}".format(page_no))
                PosCategory.set_categories_to_odoo(res)
        return self.success_popup('Categories')

    def get_products_methods(self):
        ctx = {'is_modifier': False}
        if self.import_option == 'product_modifiers':
            ctx = {'is_modifier': True}
        res = self.authenticate(self.data_access_url)
        Product = self.env['product.product']
        Product.with_context(ctx).set_products_to_odoo(res)
        last_page = int(res.get('meta').get('last_page'))
        if last_page > 1:
            for page_no in range(int(res.get('meta').get('current_page')) + 1, last_page + 1):
                res = self.authenticate(self.data_access_url + "?page={}".format(page_no))
                Product.with_context(ctx).set_products_to_odoo(res)
        return self.success_popup('Products')

    def get_orders_methods(self):
        first_page = self.page
        # url = self.data_access_url + "?include=branch,customer,products.product,payments,payments.paymentMethod,products.taxes,creator,products.options.modifierOption&filter[updated_after]={}".format(self.updated_after)

        if not self.from_date:
            if not self.updated_after:
                from_date = str((datetime.datetime.now() - relativedelta(years=1000)).date())
            else:
                from_date = self.updated_after.strftime('%Y-%m-%d')
        else:
            from_date = self.from_date.strftime('%Y-%m-%d')

        if not self.to_date:
            to_date = str(datetime.datetime.now().date())
        else:
            to_date = self.to_date.strftime('%Y-%m-%d')

        # if from_date == to_date:
        #     raise UserError(_('From Date and To date can not be same !'))

        # if from_date > to_date:
        #     raise UserError(_('From Date is greater than To Date!'))

        # url = self.data_access_url + "?include=branch,customer,products.product,payments,payments.paymentMethod,products.taxes,creator,products.options.modifierOption&sort=reference&page={}&filter[updated_after]={}"
        
        url = self.data_access_url + "?include=branch,customer,products.product,payments,payments.paymentMethod,products.taxes,creator,products.options.modifierOption&sort=reference&page={}&filter[business_date_after]={}&filter[business_date_before]={}"
        # url = self.data_access_url
        res = self.authenticate(url.format(self.page, from_date, to_date))
        Order = self.env['pos.order']

        is_break = Order.set_orders_to_odoo(res, to_date)
        if not is_break:
            last_page = int(res.get('meta').get('last_page'))
            current_page = int(res.get('meta').get('current_page'))
            if last_page > 1:
                for page_no in range(current_page + 1, last_page + 1):
                    if page_no % 30 == 0:
                        time.sleep(60)

                    res = self.authenticate(url.format(page_no, from_date, to_date))
                    self.page = page_no
                    is_break = Order.set_orders_to_odoo(res, to_date)
                    if is_break:
                        break
            self.page = 1
            self.updated_after = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            return self.success_popup('Orders')

    def sync_pos_order(self):
        connector = self.search([('import_option', '=', 'orders')])
        if connector:
            connector.get_orders_methods()

