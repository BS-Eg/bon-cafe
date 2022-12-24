from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    custom_iface_discount = fields.Boolean(string='Order Discounts', help='Allow the cashier to give discounts on the whole order.')
    custom_discount_pc = fields.Float(string='Discount Percentage', help='The default discount percentage', default=10.0)
    custom_discount_product_id = fields.Many2one('product.product', string='Discount Product',
        domain="[('sale_ok', '=', True)]", help='The product used to model the discount.')
    custom_module_pos_discount = fields.Boolean("custom Global Discounts")


    def _get_forbidden_change_fields(self):
        forbidden_keys = ['module_pos_hr', 'cash_control', 'module_pos_restaurant', 'available_pricelist_ids',
                          'limit_categories', 'iface_available_categ_ids', 'use_pricelist', 'module_pos_discount','custom_module_pos_discount',
                          'payment_method_ids', 'iface_tipproduc']
        return forbidden_keys


    @api.onchange('company_id','custom_module_pos_discount')
    def custom_default_discount_product_id(self):
        product = self.env.ref("point_of_sale.product_product_consumable", raise_if_not_found=False)
        self.custom_discount_product_id = product if self.custom_discount_product_id and product and (not product.company_id or product.company_id == self.company_id) else False

    @api.model
    def custom_default_discount_value_on_module_install(self):
        configs = self.env['pos.config'].search([])
        open_configs = (
            self.env['pos.session']
            .search(['|', ('state', '!=', 'closed'), ('rescue', '=', True)])
            .mapped('config_id')
        )
        # Do not modify configs where an opened session exists.
        for conf in (configs - open_configs):
            conf.custom_default_discount_product_id()
