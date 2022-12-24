/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_custom_discounts.pos_custom_discounts', function (require) {
"use strict";
	const NumpadWidget = require('point_of_sale.NumpadWidget');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
	var pos_model = require('point_of_sale.models');
	var SuperOrderline = pos_model.Orderline;
	var core = require('web.core');
	var _t = core._t;
	const { Gui } = require('point_of_sale.Gui');
	
	pos_model.load_models([{
		model:'pos.custom.discount',
		field: [],
		domain:function(self){
			return [['id','in',self.config.discount_ids]];
		},
		loaded: function(self,result) {
			self.all_discounts = result;
		}

	}]);

	pos_model.Orderline = pos_model.Orderline.extend({			
		initialize: function(attr,options){
			this.custom_discount_reason='';
			SuperOrderline.prototype.initialize.call(this,attr,options);
		},
		export_for_printing: function(){
			var dict = SuperOrderline.prototype.export_for_printing.call(this);
			dict.custom_discount_reason = this.custom_discount_reason;
			return dict;
		},
		get_custom_discount_reason: function(){
			var self = this;		
			return self.custom_discount_reason;
		},
		export_as_JSON: function() {
			var self = this;
			var loaded=SuperOrderline.prototype.export_as_JSON.call(this);
			loaded.custom_discount_reason=self.get_custom_discount_reason();  
			return loaded;
		}
	});

	// Popup WkCustomDiscountPopup
    class WkCustomDiscountPopup extends AbstractAwaitablePopup {
		click_discount(event){
			$('#error_div').hide();
		}
		click_current_product(event){
			if (($('#discount').val())>100 || $('#discount').val()<0){
				$('#error_div').show();
				$('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
			}
			else{
				var wk_customize_discount = parseFloat($('#discount').val())
				var reason =($("#reason").val());
				var order = this.env.pos.get_order();
				order.get_selected_orderline().set_discount(wk_customize_discount);	
				order.get_selected_orderline().custom_discount_reason=reason;
				$('ul.orderlines li.selected div#custom_discount_reason').text(reason);
				this.cancel();
			}
		}
		click_whole_order(event){
			var order = this.env.pos.get_order();
			var orderline_ids = order.get_orderlines();
			if (($('#discount').val())>100 || $('#discount').val()<0){
				$('#error_div').show();
				$('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
			}
			else{
				var wk_customize_discount = parseFloat($('#discount').val());
				var reason =($("#reason").val());
				for(var i=0; i< orderline_ids.length; i++){
						orderline_ids[i].set_discount(wk_customize_discount);
						orderline_ids[i].custom_discount_reason=reason;
					}
				$('ul.orderlines li div#custom_discount_reason').text(reason);
				this.cancel();
			}			
		}
    }
    WkCustomDiscountPopup.template = 'WkCustomDiscountPopup';
    WkCustomDiscountPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WkCustomDiscountPopup);

	// Popup WkDiscountPopup
    class WkDiscountPopup extends AbstractAwaitablePopup {
		constructor() {
			super(...arguments);
			var discount_id = null;
			var wk_discount_list = this.env.pos.all_discounts;
			this.wk_discount_percentage=0;
			var discount_price=0;
			var wk_discount = null;
			setTimeout(function(){
				$(".button.apply").show();
				$(".button.apply_complete_order").show();
				$("#discount_error").hide();
				if(!wk_discount_list.length){
					$(".button.apply_complete_order").hide();
					$(".button.apply").hide();
				}
			},100);
			// this.render();
		}
		async wk_ask_password(password){
			var self = this;
			var ret = new $.Deferred();
			if (password) {
				const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
					isPassword: true,
					title: this.env._t('Password ?'),
					startingValue: null,
				});
				if (Sha1.hash(inputPin) !== password) {
					Gui.showPopup('WebkulErrorPopup',{
						'title':_t('Password Incorrect !!!'),
						'body':_('Entered Password Is Incorrect ')
					});
				} else {
					ret.resolve();
				}
			} else {
				ret.resolve();
			}
			return ret;
		}
		click_wk_product_discount(event){
			$("#discount_error").hide();
			$(".wk_product_discount").css('background','white');
			var discount_id=parseInt($(event.currentTarget).attr('id'));
			$(event.currentTarget).css('background','#6EC89B');
			var wk_discount_list = this.env.pos.all_discounts;
			for(var i=0; i<wk_discount_list.length; i++ ){
				if( wk_discount_list[i].id == discount_id){
					var wk_discount = wk_discount_list[i] ;
					this.wk_discount_percentage = this.env.pos.format_currency_no_symbol(wk_discount.discount_percent);
				}
			}
		}
		click_customize(event){
			var self = this;
			var employee = _.filter(self.env.pos.employees, function(employee){
				return employee.id == self.env.pos.get_cashier().id;
			});
			if(self.env.pos.config.allow_security_pin && employee && employee[0].pin){
				self.wk_ask_password(employee[0].pin).then(function(data){
					Gui.showPopup('WkCustomDiscountPopup', {
						'title': self.env._t("Customize Discount"),
					});
				});
			}
			else{
				self.showPopup('WkCustomDiscountPopup', {
					'title': self.env._t("Customize Discount")
				});
			}
		}
		click_apply_complete_order(event){
			var order = this.env.pos.get_order();
			if(this.wk_discount_percentage != 0){
				var orderline_ids = order.get_orderlines();
				for(var i=0; i< orderline_ids.length; i++){
						orderline_ids[i].set_discount(this.wk_discount_percentage);
						orderline_ids.custom_discount_reason='';
					}
				$('ul.orderlines li div#custom_discount_reason').text('');
				this.cancel();	
			}
			else{	
				$(".wk_product_discount").css("background-color","burlywood");
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},100);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","burlywood");
				},200);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},300);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","burlywood");
				},400);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},500);
				return;
			}
		}
		click_apply(event){
			var order = this.env.pos.get_order();
			if(this.wk_discount_percentage != 0){
				order.get_selected_orderline().set_discount(this.wk_discount_percentage);
				order.get_selected_orderline().custom_discount_reason='';
				$('ul.orderlines li.selected div#custom_discount_reason').text('');
				this.cancel();
			}
			else{			
				$(".wk_product_discount").css("background-color","burlywood");
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},100);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","burlywood");
				},200);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},300);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","burlywood");
				},400);
				setTimeout(function(){
					$(".wk_product_discount").css("background-color","");
				},500);
				return;
			}
		}
    }
    WkDiscountPopup.template = 'WkDiscountPopup';
    WkDiscountPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WkDiscountPopup);
	
	// Popup WebkulErrorPopup
    class WebkulErrorPopup extends AbstractAwaitablePopup {
		click_password_ok_button(event){
			this.cancel();
		}
    }
    WebkulErrorPopup.template = 'WebkulErrorPopup';
    WebkulErrorPopup.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(WebkulErrorPopup);

	// Inherit NumpadWidget----------------
    const PosResNumpadWidget = (NumpadWidget) =>
		class extends NumpadWidget {
			changeMode(mode) {
				var self = this;
				if(mode == 'discount' && self.env.pos.get_order().get_selected_orderline()){
					if(self.env.pos.config.discount_ids.length ||self.env.pos.config.allow_custom_discount){
						self.showPopup('WkDiscountPopup', {
							'title': self.env._t("Discount List"),
						});
						return;
					}
					else{
						self.showPopup('WebkulErrorPopup',{
							'title':self.env._t('No Discount Is Available'),
							'body':self.env._t('No discount is available for current POS. Please add discount from configuration')
						});
						return;
					}	
				}
				else if(mode == 'discount'){
					self.showPopup('WebkulErrorPopup',{
						'title':self.env._t('No Selected Orderline'),
						'body':self.env._t('No order line is Selected. Please add or select an Orderline')
					});
					return;
				}
				super.changeMode(mode);
			}
		};
    Registries.Component.extend(NumpadWidget, PosResNumpadWidget);
});
