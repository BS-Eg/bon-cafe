odoo.define('employee_timeoff_portal.timeoff_portal', function (require) { 
    "use strict";
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var time = require('web.time');

    var _t = core._t;
    var Dialog = require('web.Dialog');
    
    publicWidget.registry.time0ff_portal = publicWidget.Widget.extend({
        selector: '#wrapwrap:has(.create_new_timeoff_form, .edit_timeoff_form)',
        events: {
            'change select.holiday_status_id' : function (e) {
                e.preventDefault();
                var self = this;
                self.$("#request_unit_half").prop("checked", false);
                self.$("#request_unit_hours").prop("checked", false);
                self.$('.request_hour_div').hide();
                self.$('.request_date_from_period_div').hide();
                self._onChangeHolidayStatus(this.$('select.holiday_status_id').val());
                self.$('#request_date_to_div').show();
            },
            'change input.request_unit_half' : function(e){
                e.preventDefault();
                var self = this;
                self.$("#request_unit_hours").prop("checked", false);
                self.$('.request_hour_div').hide();
                self.$('.select_request_hour').removeAttr('required');
                self.$('.select_request_hour').val('');
                self.check_request_date_from_period(this.$('input.request_unit_half'));
            },
            'change input.request_unit_hours' : function(e){
                e.preventDefault();
                var self = this;
                self.$("#request_unit_half").prop("checked", false);
                self.$('#request_date_from_period_div').hide();
                self.$('#request_date_from_period').removeAttr('required');
                self.$('#request_date_from_period').val('');
                self.check_request_custom_hours(this.$('input.request_unit_hours'));
            },
            'click .create_new_timeoff_form .create_new_timeoff_confirm': '_onCreateNewTimeoffRequest',
            'click .edit_timeoff_form .edit_timeoff_confirm': '_onEditTimeOffRequest',
            'click .o_delete_action_button' : '_onDeleteTimeoffRequest',
        },
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {jQuery} $btn
         * @param {function} callback
         * @returns {Promise} 
         */
        _buttonExec: function ($btn, callback) {
            // TODO remove once the automatic system which does this lands in master
            $btn.prop('disabled', true);
            return callback.call(this).guardedCatch(function () {
                $btn.prop('disabled', false);
            });
        },
        /**
         * @private
         * @returns {Promise} 
         */

        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            return Promise.all([
                this._super(),
                this.$('.holiday_status_id').each(function () {
                    self._onChangeHolidayStatus($(this).val());
                }),
                this.$('#request_unit_half').each(function(){
                    self.check_request_date_from_period($(this));
                }),
                this.$('#request_unit_hours').each(function(){
                    self.check_request_custom_hours($(this));
                }),
            ])
        },
        _onChangeHolidayStatus: function(val){
            var self = this;
            this._rpc({
                model : 'hr.leave.type',
                method: 'search_read',
                args: [[['id', '=', val]], ['id', 'request_unit']],
            }).then(function(rec){
                if (rec && rec[0]){
                    if (rec[0].request_unit == 'hour'){
                        $('.request_unit_half_div').show();
                        $('.request_unit_hours_div').show();
                    }
                    else if (rec[0].request_unit == 'half_day'){
                        $('.request_unit_half_div').show();
                        $('.request_unit_hours_div').hide();                     
                    }
                    else{
                        $('.request_unit_half_div').hide();
                        $('.request_unit_hours_div').hide();
                        $('.request_date_from_div').show();
                    }
                }
            });            
        },
        check_request_date_from_period: function($this){
            var self = this;
            var $request_date_from_period_div = $('#request_date_from_period_div');
            var $request_date_to_div = $('#request_date_to_div');
            var $request_date_from_period = $request_date_from_period_div.find('#request_date_from_period');
            if ($this.prop('checked'))
            {
                $request_date_from_period_div.show();                
                $request_date_from_period.attr('required','required');
                setTimeout(function() {
                    $request_date_to_div.hide();
                    $request_date_to_div.find('.request_date_to').val('');
                }, 10);               
            }
            else
            {   
            	$request_date_from_period_div.hide();
            	$request_date_from_period.removeAttr('required');
                $request_date_from_period.val('');
                $request_date_to_div.show();
            }
        },
        check_request_custom_hours: function($this){
            var $request_hour_div = $('.request_hour_div');
            var $request_date_to_div = $('#request_date_to_div');
            var $select_request_hour = $request_hour_div.find('.select_request_hour');
            if ($this.prop('checked'))
            {
            	$request_hour_div.show();
                $select_request_hour.attr('required','required');
                setTimeout(function() {
                    $request_date_to_div.hide();
                    $request_date_to_div.find('.request_date_to').val('');
                }, 10);
            }
            else
            {
            	$request_hour_div.hide();
            	$select_request_hour.removeAttr('required');
                $select_request_hour.val('');
                $request_date_to_div.show();
            }
        },
        _onCreateNewTimeoffRequest: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var name = $('.create_new_timeoff_form .name').val();
            if (!name) {    
                this.do_notify(false, _t("Please Enter Description"));
                return;
            }
            var request_date_from = $('.create_new_timeoff_form .request_date_from').val();
            if (!request_date_from) {
                this.do_notify(false, _t("Please Enter From Date"));
                return;
            }            
            
            var request_unit_half = $('.create_new_timeoff_form .request_unit_half').prop("checked");
            var request_date_from_period = $('.create_new_timeoff_form .request_date_from_period').val();
            if (request_unit_half && !request_date_from_period) {
                this.do_notify(false, _t("Please Enter From Period"));
                return;
            }

            var request_unit_hours = $('.create_new_timeoff_form .request_unit_hours').prop("checked");
            var request_hour_from = $('.create_new_timeoff_form .request_hour_from').val();
            var request_hour_to =$('.create_new_timeoff_form .request_hour_to').val();

            if (request_unit_hours && (!request_hour_from || !request_hour_to)) {
                this.do_notify(false, _t("Please Enter From Period"));
                return;
            }

            var request_date_to = $('.create_new_timeoff_form .request_date_to').val();
            if (!request_date_to && !request_unit_half && !request_unit_hours) {
                this.do_notify(false, _t("Please Enter To Date"));
                return;
            }

            this._buttonExec($(ev.currentTarget), this._createNewTimeOff);
        },
        _createNewTimeOff: function(){            
            return this._rpc({
                model: 'hr.leave',
                method: 'create_timeoff_portal',
                args: [{
                    name: $('.create_new_timeoff_form .name').val(),
                    holiday_status_id: $('.create_new_timeoff_form .holiday_status_id').val(),

                    request_date_from: this._parse_date($('.create_new_timeoff_form .request_date_from').val()),
                    request_date_to: this._parse_date($('.create_new_timeoff_form .request_date_to').val()),
                    
                    request_unit_half: $('.create_new_timeoff_form .request_unit_half').prop("checked"),
                    request_date_from_period: $('.create_new_timeoff_form .request_date_from_period').val(),

                    request_unit_hours: $('.create_new_timeoff_form .request_unit_hours').prop("checked"),
                    request_hour_from: $('.create_new_timeoff_form .request_hour_from').val(),
                    request_hour_to: $('.create_new_timeoff_form .request_hour_to').val(),                    
                }],
            })
            .then(function (response) {
                if (response.errors) {
                    $('#new-timeoff-dialog .alert').remove();
                    $('#new-timeoff-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                    return Promise.reject(response);
                } else {
                    window.location = '/my/leave/' + response.id + '?access_token=' + response.access_token;
                }
            });
        },
        _onEditTimeOffRequest: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            var name = $('.edit_timeoff_form .name').val();
            if (!name) {    
                this.do_notify(false, _t("Please Enter Description"));
                return;
            }
            var request_date_from = $('.edit_timeoff_form .request_date_from').val();
            if (!request_date_from) {
                this.do_notify(false, _t("Please Enter From Date"));
                return;
            }            
            
            var request_unit_half = $('.edit_timeoff_form .request_unit_half').prop("checked");
            var request_date_from_period = $('.edit_timeoff_form .request_date_from_period').val();
            if (request_unit_half && !request_date_from_period) {
                this.do_notify(false, _t("Please Enter From Period"));
                return;
            }

            var request_unit_hours = $('.edit_timeoff_form .request_unit_hours').prop("checked");
            var request_hour_from = $('.edit_timeoff_form .request_hour_from').val();
            var request_hour_to =$('.edit_timeoff_form .request_hour_to').val();

            if (request_unit_hours && (!request_hour_from || !request_hour_to)) {
                this.do_notify(false, _t("Please Enter From Period"));
                return;
            }

            var request_date_to = $('.edit_timeoff_form .request_date_to').val();
            if (!request_date_to && !request_unit_half && !request_unit_hours) {
                this.do_notify(false, _t("Please Enter To Date"));
                return;
            }
            this._buttonExec($(ev.currentTarget), this._onEditTimeOff);
        },
        _onEditTimeOff: function(){
            return this._rpc({
                model: 'hr.leave',
                method: 'update_timeoff_portal',
                args: [{
                    leave_id: parseInt($('.edit_timeoff_form .leave_id').val()),

                    name: $('.edit_timeoff_form .name').val(),
                    holiday_status_id: $('.edit_timeoff_form .holiday_status_id').val(),

                    request_date_from: this._parse_date($('.edit_timeoff_form .request_date_from').val()),
                    request_date_to: this._parse_date($('.edit_timeoff_form .request_date_to').val()),
                    
                    request_unit_half: $('.edit_timeoff_form .request_unit_half').prop("checked"),
                    request_date_from_period: $('.edit_timeoff_form .request_date_from_period').val(),

                    request_unit_hours: $('.edit_timeoff_form .request_unit_hours').prop("checked"),
                    request_hour_from: $('.edit_timeoff_form .request_hour_from').val(),
                    request_hour_to: $('.edit_timeoff_form .request_hour_to').val(),              
                }],
            }).then(function (response) {
                if (response){
                    window.location.reload();
                }else{
                    this.do_notify(false, _t("Something went wrong during your Time off updation."));
                }                
            });
        },
        _onDeleteTimeoffRequest: function(ev){
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();
            var leave_id = parseInt(ev.currentTarget.value);
            if(leave_id){
                Dialog.alert(self, _t("This will delete the Time Off. Do you still want to proceed ?"), {
                    confirm_callback: function() {
                        self._onDeleteTimeOff(leave_id);
                    },
                    title: _t('Delete Time Off'),
                });
            }            
        },
        _onDeleteTimeOff: function (leave_id) {  
            var self = this;          
            return this._rpc({
                    model:  'hr.leave',
                    method: 'unlink_portal',
                    args: [{
                        leave_id :  leave_id
                    }],                   
                }).then(function(result){
                    if (result === true) {
                        window.location = '/my/leaves/';
                    }else{
                        self.do_notify(false, _t("Something went wrong during your Time off deletion."));
                    }
                });
        },
        _parse_date: function (value) {            
            var date = moment(value, "YYYY-MM-DD", true);
            if (date.isValid()) {
                return time.date_to_str(date.toDate());
            }
            else {
                return false;
            }
        },
    });
});