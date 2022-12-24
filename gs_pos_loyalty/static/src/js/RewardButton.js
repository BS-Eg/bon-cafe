odoo.define('gs_pos_loyalty.RewardButton', function(require) {
'use strict';

    const RewardButton = require('pos_loyalty.RewardButton');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const ajax = require('web.ajax');
    const core = require('web.core');
    var _t = core._t;
    const GSRewardButton = RewardButton =>
        class  extends RewardButton {
        constructor() {
            super(...arguments);
        }
        async onClick() {
            let order = this.env.pos.get_order();
            let client = this.env.pos.get('client') || this.env.pos.get_client();
            var self = this

            if (!client) {
                const {
                    confirmed,
                    payload: newClient,
                } = await this.showTempScreen('ClientListScreen', { client });
                if (confirmed) {
                    order.set_client(newClient);
                    order.updatePricelist(newClient);
                }
                return;
            }
            if (client && client.loyalty_id && client.loyalty_id.length > 0) {
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'loyalty.reward',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: [['loyalty_program_id', '=', client.loyalty_id[0]]],
                    fields: ['name','reward_type','minimum_points','gift_product_id','point_cost','discount_product_id',
                'discount_percentage', 'discount_fixed_amount', 'discount_apply_on', 'discount_type', 'discount_apply_on',
                'discount_specific_product_ids', 'discount_max_amount', 'minimum_amount', 'loyalty_program_id']
                }
            }).then(function (res) {
                self.env.pos.loyalty.rewards = res;
            })
            this.env.pos.loyalty.rewards = self.env.pos.loyalty.rewards;
        }
            var rewards = this.env.pos.loyalty.rewards;
            var rules = order.get_rules();
            var max_amount = 0.00;
            var min_amount = 0.00;
            var min_amount_float = 0.00;
            var points_currency = 0.00;
            var points_quantity = 0;
            var max_amount = 0.00;
            var max_amount_float = 0.00;

            if (!rewards) {
                await this.showPopup('ErrorPopup', {
                    title: this.env._t('No Rewards Available'),
                    body: this.env._t('There are no rewards available for this customer as part of the loyalty program'),
                });
                return;
            }
            else if (this.env.pos.loyalty.rewards.length === 1) {
                var selectedReward = rewards[0];

            }
            else {
                const rewardsList = rewards.map(reward => ({
                    id: reward.id,
                    label: reward.name,
                    item: reward,
                }));

                const { confirmed, payload: selectedReward } = await this.showPopup('SelectionPopup',
                    {
                        title: this.env._t('Please select a reward'),
                        list: rewardsList,
                    }
                );
            }
            if (rules && rules[0]) {
                max_amount_float = rules[0].max_amount
                min_amount_float = rules[0].min_amount
                max_amount = this.env.pos.format_currency(rules[0].max_amount, 2)
                min_amount = this.env.pos.format_currency(rules[0].min_amount, 2)
                points_currency = this.env.pos.format_currency(client.loyalty_points * selectedReward.point_cost, 2)
                points_quantity = client.loyalty_points
            }
            const body_desc = "Total points:" + points_quantity + "\nAmount:" + points_currency + "\nMin amount: " + min_amount + "\nMax amount: " + max_amount;
            const { confirmed, payload } = await this.showPopup('NumberPopup', {
                title: this.env._t('Reward'),
                body: body_desc,
                startingValue: 0,
            });
            const val = Math.round(parseFloat(payload));
            var order_total = order.get_total_with_tax();
            if (val >= order_total){
                await this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be less than Total amount.'),
                });
                return;
            }

            else if (val > max_amount_float){
                await this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be less than or equal to the Max amount.'),
                });
                return;
            }
            else if (val < min_amount_float){
                await this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The reward amount should be greater than or equal to the Min amount.'),
                });
                return;
            }
            else if (rules && rules[0] && rules[0].points_currency * val > this.env.pos.get_client().loyalty_points){
                await this.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('The equivalent points of the amount you have entered is greater than the total points of this customer.'),
                });
                return ;
            }
            if (confirmed) {

                order.apply_reward(selectedReward, val, max_amount, min_amount);
            }


        }
    }

    Registries.Component.extend(RewardButton, GSRewardButton);
    return GSRewardButton;
})