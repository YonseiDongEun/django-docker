from django import forms
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect

from app.models import MealReview, SideDishesReview, StyleReview, Submits, UserSubmitter, RawFileMetadata, \
    RawDataTemplate, RequestsNew, TaskMetadata, ParsingDataSeq

from app.utils.userinterface import render_template_UI

from app.utils import account
from app.utils import dbinterface
from app.utils import task
# general ui
def view_signin(request):
    if(request.method == "POST"):
        if(account.signin(request)):
            return redirect("/")
    else:
        if(request.user.is_authenticated):
            return redirect("/")
        
    return render_template_UI(request,'app/general/signin.html')

def view_signup(request):
    if(request.user.is_authenticated):
        return redirect("/")

    if(request.method=="POST"):
        if(account.create_account(request)):
            account.signin(request)
            return redirect("/")

    return render_template_UI(request,'app/general/signup.html')

def view_signout(request):
    if(request.user.is_authenticated):
        account.signout(request)
        pass
    else:
        pass

    return redirect("/")

def view_myaccount(request):
    if(not request.user.is_authenticated):
        return redirect("/")

    if(request.method=="POST"):
        account.update_info(request)
        return redirect("/")

    return render_template_UI(request,'app/general/myaccount.html')

def view_delete_account_confirmed(request):
    account.delete_account(request)
    return redirect("/")

def view_root(request):
    if(not request.user.is_authenticated):
        return redirect('/signin')
    return render_template_UI(request,'app/general/main.html')

# admin ui
def view_tskstat(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/tskstat.html')

def view_tskstat_per_task(request, tblname):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/todo.html')

def view_tskcreate(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/tskcreate.html')

def view_tskmgmt(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/tskmgmt.html')

def view_tskmgmt_per_task(request, tblname):
    if(not account.is_admin(request)):
        return redirect("/")
    
    cur_task = task.TaskDescriptor({"table_name":tblname})
    if(not cur_task.table_exists()):
        return redirect("/")
    cur_task.fetch_meta()
    context = {'display_name':cur_task.display_name,
        'table_name':cur_task.table_name,
        'description':cur_task.description,
        'pass_criterion':cur_task.pass_criterion,
        'upload_cycle':cur_task.upload_cycle,
        'activated':cur_task.activated,
        'columns':cur_task.columns}
    return render_template_UI(request,'app/general/tskmgmt_per_task.html',context)

def view_usrmgmt(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/usrmgmt.html')

def view_usrmgmt_per_user(request, usrid):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/todo.html')