from . import account
from django.shortcuts import render, get_object_or_404, redirect


def render_template_UI(request, template, context):
    # context['user'] = account.get_session()
    context['nav_items_'] = get_navitems(request)
    context['user_'] = {'id':account.get_id(request)
                        ,'role':account.get_role_fullname(request)}
    return render(request, template, context)

def render_template_error_UI(request, status_code):
    return render(request, "app/general/error.html",{'status_code':status_code})

_navitems={
    "guest":[("Sign Up","signup"),("Sign In","signin")],
    "member":[("My Account","myaccount"),("Sign Out","signout")],

    "administrator":[("Overview","tskstat"),
        ("Create Task","tskcreate"),
        ("Manage Task","tskmgmt"),
        ("Manage Users","usrmgmt")],

    "evaluator":[],
    
    "submitter":[("Upload","upload")],
}
def get_navitems(request):
    if(not request.user.is_authenticated):
        return _navitems["guest"]
    else:
        return _navitems[account.get_role_fullname(request)]+_navitems["member"]