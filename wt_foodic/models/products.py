# -*- coding: utf-8 -*-

from odoo import fields, models, _
import base64
import requests

class ProductProduct(models.Model):
    _inherit = 'product.product'

    name_localized = fields.Char('Name Localized')
    foodic_product_id = fields.Char('Foodic product Id')
    is_modifier = fields.Boolean()
    
    def set_products_to_odoo(self, res):

        i = 0
        ProductProduct = self.env['product.product']
        for product in res.get('data'):
            i += 1
            image = False
            try:
                if product.get('image'):
                    image = base64.b64encode(requests.get(product.get('image').strip()).content).replace(b'\n', b'')
            except:
                pass

            barcode = product.get('barcode')
            if barcode:
                self._cr.execute('''SELECT id from product_product where barcode='{}' '''.format(barcode))
                res = self._cr.fetchone()
                if res:
                    barcode = ''

            vals = {
                'foodic_product_id': product.get('id'),
                'default_code': product.get('sku'),
                'barcode': barcode if barcode else None,
                'name': product.get('name'),
                'name_localized': product.get('name_localized'),
                'description': product.get('description'),
                'image_1920': image,
                'type': 'product' if product.get('is_stock_product') else 'consu', 
                'lst_price': product.get('price'),
                'standard_price': product.get('cost'), 
                'available_in_pos': True,
                'sale_ok': True, 
                'active': product.get('is_active'),
            }

            if product.get('deleted_at'):
                vals['active'] = False

            if product.get('status') == 5:
                vals['active'] = False

            if self.env.context.get('is_modifier'):
                vals['is_modifier'] = True
            
            product_id = ProductProduct.search([('name', '=', product.get('name')), ('active', 'in', [True, False])], limit=1)
            if product_id and product_id.foodic_product_id == product.get('id'):
                product_id.write(vals)
                
            if not product_id:
                product_id = ProductProduct.create(vals)
            
            if i%100 == 0:
                self._cr.commit()
        self._cr.commit()
