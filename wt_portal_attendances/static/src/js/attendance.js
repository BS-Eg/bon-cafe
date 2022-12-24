odoo.define('wt_portal_attendances.portal_attendance', function (require) {
'use strict';
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var session = require('web.session');
	var QWeb = core.qweb;
	var _t = core._t;
	publicWidget.registry.PortalKioskConfirm = publicWidget.Widget.extend({
	    selector: '.attendace_employye_cl',
	    xmlDependencies: ['/wt_portal_attendances/static/src/xml/attendance.xml'],
	    events: {
	        'click .o_hr_attendance_sign_in_out_icon': '_onClickSignInOut',
	    },
	    init: function () {
	        this._super.apply(this, arguments);
	    },
	    start: async function () {
	    	var res = await this._rpc({
	    		route: '/portal/attendance/employee',

	    	});
	    	this.next_action = 'hr_attendance.hr_attendance_action_kiosk_mode';
		this.employee_id = res.employee_id;
		this.employee_name = res.employee_name;
		this.employee_state = res.employee_state;
		var result = this.convertNumToTime(res.employee_hours_today);
		this.employee_hours_today = result;
		var is_use_pin = await session.user_has_group('hr_attendance.group_hr_attendance_use_pin');
		this.use_pin = is_use_pin
		this.$el.html(QWeb.render("PortalHrAttendanceKioskConfirm", {widget: this}));
		this.start_clock();
	    },
	    start_clock: function () {
	        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));}, 500);
	        // First clock refresh before interval to avoid delay
	        this.$(".o_hr_attendance_clock").show().text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit', second:'2-digit'}));
	    },
	    _onClickSignInOut: async function(){
			this._rpc({
                    model: 'hr.employee',
                    method: 'change_attandance_by_user',
                    args: [[this.employee_id]],
                    context: session.user_context,
                }).then(function(result) {
                    window.location.reload();
                });
	    },
	    convertNumToTime: function(number) {
		    var sign = (number >= 0) ? 1 : -1;
		    number = number * sign;
		    var hour = Math.floor(number);
		    var decpart = number - hour;
		    var min = 1 / 60;
		    decpart = min * Math.round(decpart / min);
		    var minute = Math.floor(decpart * 60) + '';
		    if (minute.length < 2) {
		    minute = '0' + minute; 
		    }
		    sign = sign == 1 ? '' : '-';
		    var time = sign + hour + ':' + minute;

		    return time;
		}
	});

	publicWidget.registry.PortalLeaveTimeOff = publicWidget.Widget.extend({
	    selector: '.portal_time_off_main_cl',
	    events: {
	    },
	    init: function () {
	        this._super.apply(this, arguments);
	    },
	    start: function () {
	    	var self = this;
	    	this.$el.find("input[name='daterange']").daterangepicker({

	    	},function(start, end, label) {
	    		var diff_dayas = end.diff(start, 'days') + 1;
	    		self.$el.find("input[name='number_of_days']").val(diff_dayas);
	    	});
	    	this._super.apply(this, arguments);
	    }
	});
});