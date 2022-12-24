$( document ).ready(function(e) {
	$(document).on('click','#create_timesheet',function(e){
		$.ajax({url: "/get-login-employee",
		 	data: {},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 			var datas = JSON.parse(result);
		 			$('#employee_id').val(datas.employee_id);
		 	},
		});
		var tdate = new Date();
		var dd = tdate.getDate();
		var MM = tdate.getMonth();
		var yyyy = tdate.getFullYear();
		var currentDate= yyyy + "-" +(MM+1) + "-" + dd;
		var today_date = new Date(yyyy,MM,dd);
		var FormattedDate= moment(today_date).format('YYYY-MM-DD');
		console.log($('#Modal'));
		$('#date').val(FormattedDate);
		$('#Modal').modal('show');
		
	});
	$(document).on('click','#edit_timesheet',function(e){
		$('#edit_success_msg_div').addClass('o_hidden');
		var self = this;
	    var $el = $(e.target).parents('tr').find("#timesheet_id").attr("value")
	    var timesheet_id = parseInt($el)
	    
		$.ajax({url: "/get-timesheet-data",
		 	data: {'timesheet_id':timesheet_id},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 		var datas = JSON.parse(result);
		 		var tdate = new Date(datas.edit_date);
				var dd = tdate.getDate();
				var MM = tdate.getMonth();
				var yyyy = tdate.getFullYear();
				var currentDate= yyyy + "-" +(MM+1) + "-" + dd;
				var today_date = new Date(yyyy,MM,dd);
				var FormattedDate= moment(today_date).format('YYYY-MM-DD');
				$('#edit_timesheet_id').val(timesheet_id);
				$('#edit_date').val(FormattedDate);
		 		$('#edit_description').val(datas.edit_description);
		 		$('#edit_project_id').val(datas.edit_project_id);
		 		$('#edit_employee_id').val(datas.edit_employee_id);
		 		if(datas.edit_task_id){
		 			$('#edit_task_id').val(datas.edit_task_id);
		 		}
		 		if(datas.edit_duration){
		 			var decimalTimeString = datas.edit_duration;
			 		var decimalTime = parseFloat(decimalTimeString);
			 		decimalTime = decimalTime * 60 * 60;
			 		var hours = Math.floor((decimalTime / (60 * 60)));
			 		decimalTime = decimalTime - (hours * 60 * 60);
			 		var minutes = Math.floor((decimalTime / 60));
			 		decimalTime = decimalTime - (minutes * 60);
			 		if(hours < 10)
			 		{
			 			hours = "0" + hours;
			 		}
			 		if(minutes < 10)
			 		{
			 			minutes = "0" + minutes;
			 		}
			 		var act_value = "" + hours + ":" + minutes;
		 			$('#edit_duration').val(act_value);
		 		}
		 	},
		});
	$('#ModalEdit').modal('show');
	});
	$(document).on('click','#add_timesheet',function(e){
		$('#success_msg_div').addClass('o_hidden');
		$.ajax({url: "/create-timesheet",
		 	data: {'name':$('#name').val(),'date':$('#date').val(),'project_id':$('#project_id').val(),
		 		'task_id':$('#task_id').val(),'employee_id':$('#employee_id').val(),'duration':$('#duration').val(),
		 	},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 			var datas = JSON.parse(result);
		 			if(datas.msg){
		 				
		 				$('#error_msg_div').removeClass('o_hidden');
		 				$('#success_msg_div').addClass('o_hidden');
		 				$('#error_msg').html(datas.msg);
		 			}
		 			if(datas.success_msg){
		 				$('#error_msg_div').addClass('o_hidden');
		 				$('#success_msg_div').removeClass('o_hidden');
		 				$('#success_msg').html(datas.success_msg);
		 				$('#name').val("");
		 				$('#duration').val("");
		 			}
		 	},
		});
	});
	$(document).on('click','#save_timesheet',function(e){
		$.ajax({url: "/edit-timesheet",
		 	data: {'edit_timesheet_id':$('#edit_timesheet_id').val(),'edit_description':$('#edit_description').val(),'edit_date':$('#edit_date').val(),'edit_project_id':$('#edit_project_id').val(),
		 		'edit_task_id':$('#edit_task_id').val(),'edit_employee_id':$('#edit_employee_id').val(),'edit_duration':$('#edit_duration').val(),
		 	},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 			var datas = JSON.parse(result);
		 			if(datas.success_msg){
		 				$('#edit_success_msg_div').removeClass('o_hidden');
		 				$('#edit_success_msg').html(datas.success_msg);
		 			}
		 	},
		});
	});
	$(document).on('click','#delete_timesheet_from_list',function(e){
		var self = this;
	    var $el = $(e.target).parents('tr').find("#timesheet_id").attr("value")
	    var timesheet_id = parseInt($el)
	    $('#delete_timesheet_id').val(timesheet_id);
		$('#delete_msg_div').addClass('o_hidden');
		$('#deleteModal').modal('show');
	});
	$(document).on('change','#project_id',function(e){
		$.ajax({url: "/task-data",
		 	data: {'project_id':$('#project_id').val()},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 		var datas = JSON.parse(result);
		 		$('#task_id > option').remove();
                      _.each(datas.task_list, function (data) {
				            	$('#task_id').append(
				      					  '<option value="' + data.id + '">' + data.name + '</option>'
				                        );		
                      });
		 	},
		});
	});
	$(document).on('change','#edit_project_id',function(e){
		$.ajax({url: "/edit-get-task-data",
		 	data: {'project_id':$('#edit_project_id').val()},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 		var datas = JSON.parse(result);
		 		$('#edit_task_id > option').remove();
                      _.each(datas.task_list, function (data) {
				            	$('#edit_task_id').append(
				      					  '<option value="' + data.id + '">' + data.name + '</option>'
				                        );		
                      });
		 	},
		});
	});
	$(document).on('click','#delete_timesheet',function(e){
		$.ajax({url: "/delete-timesheet-data",
		 	data: {'timesheet_id':$('#delete_timesheet_id').val()},
		 	type: "post",
		 	cache: false,
		 	success: function(result){
		 		var datas = JSON.parse(result);
		 		if(datas.success_msg){
		 			location.reload(true);
		 		}
		 	},
		});
	});
});