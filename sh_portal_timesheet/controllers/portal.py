# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
import json
import datetime
from datetime import datetime

class ShTimesheetCustomerPortal(TimesheetCustomerPortal):
    
    @http.route([
        '/get-login-employee',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def login_employee(self, **post):
        dic={}
        if request.env.user.employee_id:
            dic.update ({'employee_id':request.env.user.employee_id.id})
            
        return json.dumps(dic)
    
    @http.route([
        '/create-timesheet',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def create_timesheet(self, **post):
        dic={}
        timesheet_dic={}
        if post.get('name'):
            timesheet_dic.update({'name':post.get('name')})
        if post.get('date'):
            date = post.get('date')
            date_str = datetime.strptime(date,"%Y-%m-%d").date()
            timesheet_dic.update({'date':date_str})
        if post.get('project_id'):
            timesheet_dic.update({'project_id':int(post.get('project_id'))})
        if post.get('employee_id'):
            timesheet_dic.update({'employee_id':int(post.get('employee_id'))})
        if post.get('task_id'):
            timesheet_dic.update({'task_id':int(post.get('task_id'))})
        if post.get('duration'):
            str_value = str(post.get('duration'))
            split_str=str_value.split(':')
            float_hour = float(split_str[0])
            float_minute = float(float(float(split_str[1])*100)/60)/100
            float_value = float_hour + float_minute
            timesheet_dic.update({'unit_amount':float_value})
        account_id = request.env['project.project'].sudo().search([('id','=',int(post.get('project_id')))])
        user_id = request.env['hr.employee'].sudo().search([('id','=',int(post.get('employee_id')))])
        timesheet_dic.update({
            'account_id':account_id.analytic_account_id.id,
            'user_id':request.env.user.id,
            'partner_id':account_id.partner_id.id,
            'department_id':user_id.department_id.id,
            })
        if timesheet_dic.get('name') and timesheet_dic.get('date') and timesheet_dic.get('project_id') and timesheet_dic.get('employee_id'):
            timesheet_id = request.env['account.analytic.line'].sudo().create(timesheet_dic)
            if timesheet_id:
                dic.update({
                    'success_msg':'Timesheet is Created Successfully.'
                    })
        else:
            if not timesheet_dic.get('name'):
                dic.update({
                    'msg':'Description Field is Blank'
                    })
            if not timesheet_dic.get('date'):
                dic.update({
                    'msg':'Date Field is Blank'
                    })
            if not timesheet_dic.get('project_id'):
                dic.update({
                    'msg':'Project Field is Blank'
                    })
            if not timesheet_dic.get('employee_id'):
                dic.update({
                    'msg':'Employee Field is Blank'
                    })
        return json.dumps(dic)
    
    @http.route([
        '/get-timesheet-data',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def get_data_timesheet(self, **post):
        dic={}
        timesheet_id = request.env['account.analytic.line'].sudo().search([('id','=',int(post.get('timesheet_id')))],limit=1)
        date_obj = timesheet_id.date 
        date_str = date_obj.strftime("%Y-%m-%d")
        dic.update({
            'edit_description':timesheet_id.name,
            'edit_date':date_str,
            'edit_project_id':timesheet_id.project_id.id,
            'edit_employee_id':timesheet_id.employee_id.id,
            })
        if timesheet_id.task_id:
            dic.update({
                'edit_task_id':timesheet_id.task_id.id,
                })
        if timesheet_id.unit_amount:
            duration = str(timesheet_id.unit_amount)
            dic.update({
                'edit_duration':duration,
                })
        return json.dumps(dic)
    
    @http.route([
        '/edit-timesheet',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def edit_timesheet(self, **post):
        dic={}
        timesheet_id = request.env['account.analytic.line'].sudo().search([('id','=',int(post.get('edit_timesheet_id')))],limit=1)
        
        if post.get('edit_description') and timesheet_id:
            timesheet_id.sudo().write({
                'name':post.get('edit_description'),
                })
        if post.get('edit_date') and timesheet_id:
            date = post.get('edit_date')
            date_str = datetime.strptime(date,"%Y-%m-%d").date()
            timesheet_id.sudo().write({
                'date':date_str,
                })
        if post.get('edit_project_id') and timesheet_id:
            timesheet_id.sudo().write({
                'project_id':int(post.get('edit_project_id')),
                })
        if post.get('edit_employee_id') and timesheet_id:
            timesheet_id.sudo().write({
                'employee_id':int(post.get('edit_employee_id'))
                })
        if post.get('edit_task_id')!='' and timesheet_id:
            timesheet_id.sudo().write({
                'task_id':int(post.get('edit_task_id'))
                })
        elif post.get('edit_task_id')=='' and timesheet_id:
            timesheet_id.sudo().write({
                'task_id':False
                })
        if post.get('edit_duration') and timesheet_id:
            str_value = str(post.get('edit_duration'))
            split_str=str_value.split(':')
            float_hour = float(split_str[0])
            float_minute = float(float(float(split_str[1])*100)/60)/100
            float_value = float_hour + float_minute
            timesheet_id.sudo().write({
                'unit_amount':float_value
                })
        if post.get('edit_description') and post.get('edit_date') and post.get('edit_project_id') and post.get('edit_employee_id'):
            dic.update({
                'success_msg':'Timesheet is Edited Successfully.'
                })
        return json.dumps(dic)
    
    @http.route([
        '/task-data',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def get_task_list(self,**post):
        dic={}
        task_list=[]
        if post.get('project_id'):
            project_ids = request.env['project.task'].sudo().search([('project_id','=',int(post.get('project_id')))])
            for task in project_ids:
                task_dic={
                    "id":task.id,
                    "name":task.name,
                    }
                task_list.append(task_dic)
        dic.update({
            'task_list':task_list,
            })
        return json.dumps(dic)
    
    @http.route([
        '/edit-get-task-data',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def edit_get_task_list(self,**post):
        dic={}
        task_list=[]
        if post.get('project_id'):
            project_ids = request.env['project.task'].sudo().search([('project_id','=',int(post.get('project_id')))])
            for task in project_ids:
                task_dic={
                    "id":task.id,
                    "name":task.name,
                    }
                task_list.append(task_dic)
        dic.update({
            'task_list':task_list,
            })
        return json.dumps(dic)
        
    @http.route([
        '/delete-timesheet-data',
    ], type='http', auth="public",method="post" ,website=True,csrf=False)
    def delete_timesheet(self, **post):
        dic={}
        if post.get('timesheet_id'):
            timesheet_id = request.env['account.analytic.line'].sudo().search([('id','=',int(post.get('timesheet_id')))],limit=1)
            if timesheet_id:
                timesheet_id.sudo().unlink()
                dic.update({
                    'success_msg':'Timesheet is Deleted Successfully.'
                    })
        return json.dumps(dic)
    