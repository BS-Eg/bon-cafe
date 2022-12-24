odoo.define('wt_pos_combo.models', function (require) {
"use strict";
	var models = require('point_of_sale.models');

	models.load_models({
		model: 'pos.combo.item',
	    fields: ['pos_combo_id','category_id','product_ids','is_min_max_config', 'max_qty', 'min_qty'],
	    loaded: function(self,pos_combo_items){
	    	self.db.add_pos_combo_items(pos_combo_items);
	    },
	});

	models.load_models({
		model: 'pos.combo',
		fields: ['name','pos_combo_items_ids'],
		loaded: function(self,pos_combo_ids){
			self.db.add_pos_combo(pos_combo_ids);
	    },
	})
	models.load_fields('product.template', ['is_combo_product', 'pos_combo_id']);
	models.load_fields('product.product', ['is_combo_product', 'pos_combo_id']);

	var _super_orderline = models.Orderline.prototype

	models.Orderline = models.Orderline.extend({
		initialize: function(attr,options) {
			_super_orderline.initialize.apply(this,arguments);
			if(options && options.json && options.json.combo_lines){
				this.combo_lines = options.json.combo_lines;
			}else{
				this.combo_lines = this.combo_lines || {};			
			}
			this.combo_customer_data = [];
			this.set_combo_customer_data();
		},
		set_combo_customer_data: function(){
			var self = this;
	    	var combo = [];
	    	var combo_lines = this.get_combo_lines() || [];
	    	if(combo_lines != undefined){
	    		_.each(combo_lines, function(val, key){
	    			var products = [];
	    			_.each(val, function(item){
	    				products.push({
	    					'item_name': item.product_name,
	    					'item_qty': item.qty,
	    					'item_price': item.price,
	    					'item_total_price': item.total_price
	    				});
	    			});
	    			var value = {
	    				'category': self.pos.db.get_category_by_id(key).name,
	    				'items': products
	    			}
	    			combo.push(value);
	    		});
	    	}
	    	this.combo_customer_data = combo;
		},
		get_combo_customer_data: function(){
			return this.combo_customer_data;
		},
		set_combo_lines: function(combo_lines){
			this.combo_lines = combo_lines;
			this.update_unit_price();
			this.set_combo_customer_data();
			this.trigger('change', this);
			if (this.pos.config.iface_customer_facing_display) this.pos.send_current_order_to_customer_facing_display();
		},
		update_unit_price: function(){
			var self = this;
			var total = 0;
			_.each(this.combo_lines, function(val, key){
				var tlist = _.map(val, 'decimal_total_price');
				var sum = tlist.reduce((a, b) => a + b, 0);
				total = total + sum;
			});
			var cprice = total;
			this.set_price_extra(cprice);
			this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
            this.order.fix_tax_included_price(this);
		},
		get_combo_lines: function(){
			return this.combo_lines;
		},
		init_from_JSON: function(json) {
	        _super_orderline.init_from_JSON.apply(this,arguments);
	        var self = this;
	        this.combo_lines = json.combo_lines;
	        if(this.combo_lines == undefined && json.combo_items_ids && json.combo_items_ids.length){
	        	var com_products = [];
	        	_.each(json.combo_items_ids[0], function(cline){
	        		var co_line = cline[2];
	        		var pricelist = self.order.pricelist;
	        		var product = self.pos.db.get_product_by_id(co_line.product_id);
	        		var category = self.pos.db.get_category_by_id(co_line.category_id);
	        		com_products.push({
	        			'category_id': co_line.category_id,
	                    'product_id': co_line.product_id,
	                    'product': product,
	                    'product_name': product.display_name,
	                    'category': category,
	                    'qty': co_line.qty,
	                    'price': self.pos.format_currency(co_line.price),
	                    'total_price': self.pos.format_currency(co_line.total_price),
	                    'unit_price': co_line.price,
	                    'decimal_total_price': co_line.total_price
	        		});
	        	});
	        	if(com_products.length){
	        		this.set_combo_lines(_.groupBy(com_products, 'category_id'));
	        	}
	        }
	    },
	    get_line_export_com_paid_order: function(options){

	    },
	    export_as_JSON: function() {
	        var json = _super_orderline.export_as_JSON.apply(this,arguments);
	        json['combo_lines'] = this.combo_lines;
	        json['combo_items_ids'] = this.product.is_combo_product ? this.export_combo_items_lines() : [];
	        json['is_combo'] = this.product.is_combo_product && this.combo_lines ? true : false;
	        return json;
	    },
	    export_combo_items_lines: function(){
	    	var lines = [];
	    	var combo_lines = this.get_combo_lines() || [];
	    	if(combo_lines != undefined){
	    		_.each(combo_lines, function(val, key){
	    			_.each(val, function(item){
	    				lines.push([0, 0, {
	    					'product_id': item.product_id,
	    					'category_id': item.category_id,
	    					'price': item.unit_price,
	    					'qty': parseInt(item.qty)
	    				}]);
	    			});
	    		});
	    	}
	    	return lines;
	    },
	    export_combo_lines: function(){
	    	var self = this;
	    	var combo = [];
	    	var combo_lines = this.get_combo_lines() || [];
	    	if(combo_lines != undefined){
	    		_.each(combo_lines, function(val, key){
	    			var products = [];
	    			_.each(val, function(item){
	    				products.push({
	    					'item_name': item.product_name,
	    					'item_qty': item.qty,
	    					'item_price': item.price,
	    					'item_total_price': item.total_price
	    				});
	    			});
	    			var value = {
	    				'category': self.pos.db.get_category_by_id(key).name,
	    				'items': products
	    			}
	    			combo.push(value);
	    		});
	    	}
	    	return combo;
	    },
	    export_for_printing: function(){
	    	var receipt = _super_orderline.export_for_printing.apply(this,arguments);
	    	receipt['combo_lines'] = this.export_combo_lines();
	    	return receipt;
	    }
	});

});