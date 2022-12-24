odoo.define('gs_pos_loyalty.PointsCounter', function(require) {
'use strict';

    const Registries = require('point_of_sale.Registries');
    const utils = require('web.utils');
    const PointsCounter = require('pos_loyalty.PointsCounter')

    const round_pr = utils.round_precision;

    const GSPointsCounter = PointsCounter =>
        class  extends PointsCounter {
        get_points_won() {

            this.env.pos.get_order().get_new_loyalty();
            return round_pr(this.env.pos.get_order().get_won_points(), this.env.pos.loyalty.rounding);
        }
        get_points_spent() {

            this.env.pos.get_order().get_new_loyalty();
            return round_pr(this.env.pos.get_order().get_spent_points(), this.env.pos.loyalty.rounding);
        }
        get_points_total() {
            this.env.pos.get_order().get_new_loyalty();
            return round_pr(this.env.pos.get_order().get_new_total_points(), this.env.pos.loyalty.rounding);
        }
    }

    Registries.Component.extend(PointsCounter, GSPointsCounter);
    return GSPointsCounter;
});
