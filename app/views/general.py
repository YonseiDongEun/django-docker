from django import forms
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect

from app.models import MealReview, SideDishesReview, StyleReview, Submits, UserSubmitter, RawFileMetadata, \
    RawDataTemplate, RequestsNew, TaskMetadata, ParsingDataSeq

from app.utils.userinterface import render_template_UI

from app.utils import account

def view_signin(request):
    if(request.method == "POST"):
        if(account.signin(request)):
            return redirect("/")
    else:
        if(request.user.is_authenticated):
            return redirect("/")
        
    return render_template_UI(request,'app/general/signin.html',{})


def view_signup(request):
    if(request.user.is_authenticated):
        return redirect("/")

    if(request.method=="POST"):
        if(account.create_account(request)):
            account.signin(request)
            return redirect("/")

    return render_template_UI(request,'app/general/signup.html',{})


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

    return render_template_UI(request,'app/general/myaccount.html',{})
    

def view_root(request):
    if(not request.user.is_authenticated):
        return redirect('/signin')
    return render_template_UI(request,'app/general/main.html',{})

def view_tskstat(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/todo.html',{})

def view_tskcreate(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/tskcreate.html',{})

def view_tskmgmt(request):
    if(not account.is_admin(request)):
        return redirect("/")
    return render_template_UI(request,'app/general/todo.html',{})

def view_usrmgmt(request):
    if(not account.is_admin(request)):
        return redirect("/")
    context={}
    return render_template_UI(request,'app/general/usrmgmt.html',context)
