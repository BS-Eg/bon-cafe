odoo.define('pizza_modifiers.models', function(require) {
    "use strict";

    var models = require('point_of_sale.models');

    // Add field
    models.load_fields('product.attribute', 'value_ids');
    models.load_fields('product.template.attribute.value', 'name');
    models.load_fields(
        'product.product',
        ['valid_product_template_attribute_line_ids', 'product_template_attribute_value_ids',
            'is_modifier', 'allow_portion', 'apply_selector',
        ]);
    //Add new models
    models.PosModel.prototype.models.push({
        model: 'product.template',
        fields: [
            'name',
            'display_name',
            'product_variant_ids',
            'product_variant_count',
            'modifier_ids',
            'is_modifier',
            'allow_portion',
            'apply_selector', 'min_selector', 'max_selector',
            'slice_product_ids',
        ],
        domain: function(self) {
            return [
                ['sale_ok', '=', true],
                ['available_in_pos', '=', true],
            ];
        },
        context: function(self) {
            return {
                display_default_code: false
            };
        },
        loaded: function(self, templates) {
            self.db.add_templates(templates);
        },
    }, {
        model: 'product.modifiers',
        fields: [
            'name', 'desc', 'price', 'product_id'
        ],
        loaded: function(self, modifiers) {
            self.db.add_modifiers(modifiers);
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            if(product && product.is_modifier)
            {
                options = _.extend({merge: false}, options);
            }
            _super_order.add_product.call(this, product, options);
         },
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this, attr, options);
            this.parent_line_id = this.parent_line_id || false;
            this.portion = this.portion || false;
        },
        set_parent_line_id: function(line_id) {
            this.parent_line_id = line_id;
            this.trigger('change', this);
        },
        get_parent_line_id: function() {
            return this.parent_line_id;
        },
        set_portion: function(portion){
            this.portion = portion;
            this.trigger('change',this);
        },
        get_portion: function(){
            return this.portion;
        },
        clone: function() {
            var orderline = _super_orderline.clone.call(this);
            orderline.parent_line_id = this.parent_line_id;
            orderline.portion = this.portion;
            return orderline;
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.call(this);
            json.parent_line_id = this.parent_line_id;
            json.portion = this.portion;
            return json;
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.parent_line_id = json.parent_line_id;
            this.portion = json.portion;
        },
        export_for_printing: function() {
            var result = _super_orderline.export_for_printing.apply(this,arguments);
            result.parent_line_id = this.parent_line_id;
            result.portion = this.portion;
            return result;
        },
    });
});
