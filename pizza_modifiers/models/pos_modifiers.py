# -*- coding: utf-8 -*-

from odoo import fields, models, api


class POSmodifiers(models.Model):
    _name = 'pos.modifiers'
    _description = 'POS Modifiers'

    name = fields.Many2one('product.product', string='Name', required=True)
    desc = fields.Char(string='Description')
    price = fields.Float(string='Price')
    pos_categoryid = fields.Many2one('pos.category')


class Productmodifiers(models.Model):
    _name = 'product.modifiers'
    _description = 'Product Modifiers'

    name = fields.Many2one('product.product', string='Name', required=True)
    desc = fields.Char(string='Description')
    price = fields.Float(string='Price')
    product_id = fields.Many2one('product.template')


class ModifiersGroups(models.Model):
    _name = 'modifiers.groups'
    _description = 'Modifiers Groups'

    name = fields.Char(string='Toppings', required=True)
    modifier_ids = fields.Many2many(
        'product.template', 'group_id', 'tmpl_id', string="Modifiers",
        domain=[('use_as_modifier', '=', True)])


class PosCateory(models.Model):
    _inherit = 'pos.category'

    is_modifier = fields.Boolean('Is Modifier Category?')
    modifier_ids = fields.One2many('pos.modifiers', 'pos_categoryid', string='Modifiers')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_modifier = fields.Boolean('Is Modifier Product?')
    use_as_modifier = fields.Boolean('Use as a Modifiers?')
    modifier_ids = fields.One2many('product.modifiers', 'product_id', string='Modifiers')
    modifier_grp_ids = fields.Many2many('modifiers.groups', string="Modifiers Groups")
    allow_portion = fields.Boolean('Display Pieces?')
    min_selector = fields.Integer('Min Selector', default=0)
    max_selector = fields.Integer('Max Selector', default=3)
    apply_selector = fields.Boolean('Apply Selector')
    slice_product_ids = fields.Many2many(
        'product.template', 'product_template_slice_rel', 'tmpl_id', 'slice_tmpl_id',
        string="Sides Products")

    def get_modifier(self):
        ProductProduct = self.env['product.product']
        for template in self:
            template.modifier_ids.unlink()
            modifier_ids = []
            templates = template.modifier_grp_ids.mapped('modifier_ids')
            domain = [
                ('product_tmpl_id', 'in', templates.ids),
            ]
            for variant in ProductProduct.search(domain):
                modifier_ids.append(
                    (0, 0, {'name': variant.id, 'desc': variant.name, 'price': variant.lst_price}))
            template.modifier_ids = modifier_ids


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_modifier = fields.Boolean('Is Modifier Attribute')


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    parent_line_id = fields.Integer('Parent line id')

    # def _export_for_ui(self, orderline):
    #     res = super(POSOrderLine, self)._export_for_ui(orderline)
    #     res['parent_line_id'] = orderline.parent_line_id
    #     return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        res = super(PosOrder, self)._get_fields_for_order_line()
        res.append('parent_line_id')
        return res
