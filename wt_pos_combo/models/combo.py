# Part of Warlock Technolab
from odoo import fields, models, api, _
from itertools import groupby

class PosCombo(models.Model):
    _name = 'pos.combo'
    _description = 'name'
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    pos_combo_items_ids = fields.One2many('pos.combo.item', 'pos_combo_id', string="Products", required=True)

    
class PosComboItems(models.Model):
    _name = 'pos.combo.item'
    _description = 'product_id'

    pos_combo_id = fields.Many2one('pos.combo', string="Combo", ondelete='cascade')
    category_id = fields.Many2one('pos.category', string="Category", required=True)
    product_ids = fields.Many2many('product.product', string="Item", required=True)
    is_min_max_config = fields.Boolean(string="Is Set Min-Max Quantity")
    max_qty = fields.Integer(string="Max Qty")
    min_qty = fields.Integer(string="Min Qty")

class ProductsTemplate(models.Model):
    _inherit = 'product.template'

    is_combo_product = fields.Boolean(string="Is Combo")
    pos_combo_id = fields.Many2one('pos.combo', string="POS Combo")

    is_notes= fields.Char()
class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_combo = fields.Boolean("Is Combo")
    combo_items_ids = fields.One2many("pos.order.line.combo.items", 'orderline_id', "Combo Items")

    def open_combo_items(self):
        self.ensure_one()
        view_id = self.env.ref('wt_pos_combo.combo_email_compose_message_wizard_form').id
        return  {'type': 'ir.actions.act_window',
                'name': _('Extra Toppings'),
                'res_model': 'combo.items.wizard',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
            }

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res['combo_items_ids'] = [[0, 0, combo] for combo in orderline.combo_items_ids.export_for_ui()] if orderline.combo_items_ids else [],
        res['is_combo'] = orderline.is_combo
        return res


class pos_order_line_combo_items(models.Model):
    _name = "pos.order.line.combo.items"
    _description = 'name'
    _rec_name = 'name'

    name = fields.Char(string="Name", compute="_compute_combo_item")
    orderline_id = fields.Many2one('pos.order.line', 'POS Line')
    product_id = fields.Many2one('product.product', 'Product')
    category_id = fields.Many2one('pos.category', string="Category")
    price = fields.Float('Item Price', required=True)
    qty = fields.Float('Quantity', default='1', required=True)
    total_price = fields.Float(string="Total", compute="_compute_combo_item")

    def _export_for_ui(self, combo):
        return {
            'product_id': combo.product_id.id,
            'category_id': combo.category_id.id,
            'price': combo.price,
            'qty': combo.qty,
            'total_price': combo.total_price
        }

    def export_for_ui(self):
        return self.mapped(self._export_for_ui) if self else []

    def _compute_combo_item(self):
        for rec in self:
            if rec.product_id and rec.qty:
                rec.name = rec.product_id.display_name +' X '+ str(rec.qty)
            if rec.price and rec.qty:
                rec.total_price = rec.price * rec.qty

class pos_order_line_combo_items_wizard(models.TransientModel):
    _name = 'combo.items.wizard'
    _description = 'Extra Toppings'

    combo_ids = fields.Many2many('pos.order.line.combo.items', string="Combo")

    @api.model
    def default_get(self, fields):
        line = False
        if self.env.context and self.env.context.get('active_id'):
            line = self.env['pos.order.line'].sudo().browse(self.env.context.get('active_id'))
        result = super(pos_order_line_combo_items_wizard, self).default_get(fields)
        if line:
            result['combo_ids'] = line.combo_items_ids
        return result


class StockMoveInherit(models.Model):
    _inherit = "stock.picking"

    def _prepare_stock_move_combo_vals(self, data):
        product_id = self.env['product.product'].browse(int(data.get('product_id')))
        return {
            'name': product_id.name,
            'product_uom': product_id.uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': product_id.id,
            'product_uom_qty': float(data.get('quantity')),
            'state': 'draft',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
        }

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        move_vals = []
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))
        data_list = []
        for rec in lines:
            for line in rec.combo_items_ids:
                add_qty =  False
                for data in data_list:
                    if line.product_id.id == data.get('product_id'):
                        qty = data.get('quantity')
                        data['product_id'] = line.product_id.id
                        data['quantity'] = line.qty + qty
                        # 'product_id' : line.product_id.id,
                        # 'quantity' : line.qty + qty,
                        # }
                        add_qty = True
                if not add_qty:
                    dic = {
                        'product_id' : line.product_id.id,
                        'quantity' : line.qty,
                        }
                    data_list.append(dic)
        if data_list:
            for data in data_list:
                move_vals.append(self._prepare_stock_move_combo_vals(data))
        
        moves = self.env['stock.move'].create(move_vals)
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)