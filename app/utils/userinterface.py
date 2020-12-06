from . import account
from django.shortcuts import render, get_object_or_404, redirect
from app.utils.help_text import get_help_text

def render_template_UI(request, template, context={}):
    context['nav_items_'] = get_navitems(request)
    birth = request.user.is_authenticated and str(request.user.birth) or None
    context['user_'] = {'id':account.get_id(request)
                        ,'role':account.get_role_fullname(request)
                        ,'gender':account.get_gender_fullname(request)
                        ,'birth':birth}
    context['help_text_'] = get_help_text(template)
    return render(request, template, context)

def render_template_error_UI(request, status_code):
    return render(request, "app/general/error.html",{'status_code':status_code})

_navitems={
    "Guest":[("Sign Up","signup"),("Sign In","signin")],
    "Member":[("My Account","myaccount"),("Sign Out","signout")],

    "Administrator":[("Overview","tskstat"),
        ("Create Task","tskcreate"),
        ("Manage Task","tskmgmt"),
        ("Manage Users","usrmgmt")],

    "Evaluator":[],
    
    "Submitter":[("Upload","upload"),
        ("Task List", "tsklist")],
}
def get_navitems(request):
    if(not request.user.is_authenticated):
        return _navitems["Guest"]
    else:
        return _navitems[account.get_role_fullname(request)]+_navitems["Member"]