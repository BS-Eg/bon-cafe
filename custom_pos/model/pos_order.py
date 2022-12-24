import logging
from datetime import timedelta
import collections
from odoo import api, fields, models, tools, _
from functools import partial
from odoo.osv.expression import AND
from odoo.tools.safe_eval import pytz

_logger = logging.getLogger(__name__)

class CustomPosOrderCreate(models.Model):
    _inherit = "pos.order"   

    pos_delivery_partner = fields.Many2one('res.partner',string='Delivery Partner')

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
        return {
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'sequence_number': ui_order['sequence_number'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid':  ui_order['amount_paid'],
            'amount_total':  ui_order['amount_total'],
            'amount_tax':  ui_order['amount_tax'],
            'amount_return':  ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'to_invoice': ui_order['to_invoice'] if "to_invoice" in ui_order else False,
            'is_tipped': ui_order.get('is_tipped', False),
            'tip_amount': ui_order.get('tip_amount', 0),
            'pos_delivery_partner': ui_order['delivery_partner_id'] if "delivery_partner_id" in ui_order else False,

        }



    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id,
            # 'custom_note':order_line.note,
        }


class InheritReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'


    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        """ Serialise the orders of the requested time period, configs and sessions.

        :param date_start: The dateTime to start, default today 00:00:00.
        :type date_start: str.
        :param date_stop: The dateTime to stop, default date_start + 23:59:59.
        :type date_stop: str.
        :param config_ids: Pos Config id's to include.
        :type config_ids: list of numbers.
        :param session_ids: Pos Config id's to include.
        :type session_ids: list of numbers.

        :returns: dict -- Serialised sales.
        """
        # import pdb;pdb.set_trace()
        domain = [('state', 'in', ['paid','invoiced','done'])]

        if (session_ids):
            domain = AND([domain, [('session_id', 'in', session_ids)]])
        else:
            if date_start:
                date_start = fields.Datetime.from_string(date_start)
            else:
                # start by default today 00:00:00
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                date_start = today.astimezone(pytz.timezone('UTC'))

            if date_stop:
                date_stop = fields.Datetime.from_string(date_stop)
                # avoid a date_stop smaller than date_start
                if (date_stop < date_start):
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)

            domain = AND([domain,
                [('date_order', '>=', fields.Datetime.to_string(date_start)),
                ('date_order', '<=', fields.Datetime.to_string(date_stop))]
            ])

            if config_ids:
                domain = AND([domain, [('config_id', 'in', config_ids)]])

        orders = self.env['pos.order'].search(domain)

        user_currency = self.env.company.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        for order in orders:
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                # else:
                #     taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
                #     taxes[0]['base_amount'] += line.price_subtotal_incl

        non_delivery_p_order = []
        for order in orders:
            if not order.pos_delivery_partner:
                non_delivery_p_order.append(order.id)

        # payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if non_delivery_p_order:
            payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', non_delivery_p_order)]).ids
        else:
            payment_ids = []

        delivery_partner_ids_lst = []
        for line in orders:
            if line.pos_delivery_partner:
                delivery_partner_ids_lst.append(line.id)

        
        if payment_ids:
            self.env.cr.execute("""
                SELECT method.name, sum(amount) total
                FROM pos_payment AS payment,
                     pos_payment_method AS method
                WHERE payment.payment_method_id = method.id
                    AND payment.id IN %s
                GROUP BY method.name
            """, (tuple(payment_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        # if payment_ids and delivery_partner_ids_lst:
        if delivery_partner_ids_lst:
            self.env.cr.execute("""
               SELECT method.name,payment.id
                FROM pos_order AS payment,
                     res_partner AS method
                WHERE payment.pos_delivery_partner = method.id 
                    AND payment.id IN %s
                GROUP BY method.name,payment.id
            """, (tuple(delivery_partner_ids_lst),))
            delivery_partners = self.env.cr.dictfetchall()
        else:
            delivery_partners = []

        if delivery_partners:
            for record in delivery_partners:
                # id getting in record is pos order id
                record['delivery_partner_lines'] = []
                pos_order = self.env['pos.order'].search([('id','=',record['id'])])
                for payment_method in pos_order.payment_ids:
                    record['payment_method_name']=payment_method.payment_method_id.name
                    record['delivery_partner_lines'].append({'name':record['name'],'amount':payment_method.amount})
                    record.pop('name')
                    record.pop('id')
        
        final_delivery_partner_lst = []
        if delivery_partners:
            # final_delivery_partner_list = []
            # # filtering records in delivery_partners
            # for record in delivery_partners: 
            #     if not final_delivery_partner_list:
            #         final_delivery_partner_list.append(record)  
            #     else:          

            #         for line in final_delivery_partner_list:
            #             if record['payment_method_name'] not in final_delivery_partner_list:
            #                 final_delivery_partner_list.append(record)

            #             elif record['payment_method_name'] == line['payment_method_name']:
            #                 line['delivery_partner_lines'].append(record['delivery_partner_lines'])
            lst = []
            lst1 = []
            for i in delivery_partners:
                partner_obj = list(i.items())[1][1]
                if partner_obj not in lst:
                    lst.append(partner_obj)
                    obj = i.copy()
                    obj['delivery_partner_lines'] = []
                    lst1.append(obj)
                else:
                    pass            
            

            for line in delivery_partners:
                partner_obj = list(line.items())[0][1]
                for record in lst1:
                    if line['payment_method_name'] == record['payment_method_name']:
                        record['delivery_partner_lines'].append(partner_obj[0])

            newlist = []
            final_delivery_partner_lst = []
            def addelement(demo):
                if len(newlist) == 0:
                    newlist.append({'amount':demo.get('amount'), 'name':demo.get('name')})
                else:
                    for k in range(len(newlist)):
                        if newlist[k].get('name') == demo.get('name'):
                            newlist[k]['amount'] = newlist[k].get('amount') + demo.get('amount')
                            break
                    else:
                        newlist.append({'amount':demo.get('amount'), 'name':demo.get('name')})
                                    

       
            for i in range(len(lst1)):
                temp = lst1[i].get('delivery_partner_lines')
                for j in temp:
                    addelement(j)
                obj={'delivery_partner_lines': newlist, 'payment_method_name': lst1[i].get('payment_method_name')}
                final_delivery_partner_lst.append(obj)
                newlist = []


        loyalty_products = sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items() if product.name == 'Loyalty Redeem Point'], key=lambda l: l['product_name'])

        loyalty_products_amount_list = []
        for line in loyalty_products:
            amount = (line['quantity'] * line['price_unit'])
            if amount <0:
                amount = -(amount)
            loyalty_products_amount_list.append(amount)
        loyalty = [{'name': 'Loyalty Redeem Point', 'total': sum(loyalty_products_amount_list)}]


        # employees_orders_list = []
        # for order in orders:
        #     employees_orders_list.append({order.employee_id.name or 'Undefined':order.amount_total})
        #     order_qty = 0
        #     for line in order.lines:
        #         order_qty += line.qty
        #     employees_orders_list.append({order.employee_id.name or 'Undefined':order.amount_tax})
        # print('employees_orders_list: ',employees_orders_list)
        # employees_orders_dict = collections.Counter()
        # for value in employees_orders_list:
        #     employees_orders_dict.update(value)
        # print('employees_orders_dict: ',employees_orders_dict)

        # employees_orders_data = []
        # for key,value in employees_orders_dict:
        #     employees_orders_data.append({'employee_name':key,'employee_total':value})

        categories_data = []
        for order in orders:
            for line in order.lines:
                categories_data.append(line.product_id.categ_id.name)
        categories_data_x = list(dict.fromkeys(categories_data))

        categories_orders_data = []
        for categ in categories_data_x:
            categ_total_qty = 0
            categ_total_amount = 0
            for order in orders:
                for line in order.lines:
                    if categ == line.product_id.categ_id.name:
                        categ_total_qty += line.qty
                        categ_total_amount += line.price_subtotal_incl
            categories_orders_data.append({'categ_name':categ,
                                           'categ_total_qty': categ_total_qty,
                                           'categ_total_amount': categ_total_amount})
        print('categories_orders_data:',categories_orders_data)

        employees_data = []
        for order in orders:
            if order.employee_id:
                employees_data.append(order.employee_id.name)
        employees_data_x = list(dict.fromkeys(employees_data))

        employees_orders_data = []
        for employee in employees_data_x:
            employee_total_qty = 0
            employee_total_amount = 0
            for order in orders:
                if employee == order.employee_id.name:
                    employee_total_amount += order.amount_total
                    for line in order.lines:
                        employee_total_qty += line.qty
            employees_orders_data.append({'employee_name':employee,
                                          'employee_total_qty': employee_total_qty,
                                          'employee_total_amount': employee_total_amount})
        print('emp_order_data:',employees_orders_data)
        print('products:',payments)
        print('loyalty:',loyalty)

        return {
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total + loyalty[0]['total']),
            'payments': payments,
            'categories_orders_data': categories_orders_data,
            'employees_orders_data': employees_orders_data,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name']),
            'loyaltys':loyalty,
            'delivery_partners':delivery_partners,
            'delivery_partners':final_delivery_partner_lst,

        }

