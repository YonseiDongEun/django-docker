from django import forms
from django.contrib.auth import authenticate, login, logout
from django.utils import dateparse
from app.models import User

class SignupForm(forms.Form):
    user_id = forms.CharField(min_length=2, max_length=15)
    name = forms.CharField(max_length=15)
    address = forms.CharField(max_length=64)
    birth = forms.DateField()
    phone = forms.CharField(max_length=11)
    gender = forms.CharField(max_length=1)
    role = forms.CharField(max_length=1)


def create_account(request):
    id_ = request.POST['id']
    pw_ = request.POST['pw']
    role_=request.POST['role']
    birth_ = request.POST['birth']
    phone_ = request.POST['phone']
    gender_ = request.POST['gender']
    name_ = request.POST['name']
    address_ = request.POST['address']

    if(not(2<=len(str(id_))<=15)):
        return False
    if(not(2<=len(str(pw_))<=15)):
        return False

    role_ = get_role_constant(role_)
    if(role_ is None):
        return False
    
    gender_ = get_gender_const(gender_)
    if(gender_ is None):
        return False
    
    birth_ = dateparse.parse_date(birth_)
    if(birth_ is None):
        pass

    try:
        r=User.objects.create(user_id=id_,name=name_,address=address_,gender=gender_,phone=phone_,birth=birth_,role=role_)
        r.set_password(pw_)
        r.save()
        return True
    except:
        return False

def signin(request):
    id = request.POST['id']
    pw = request.POST['pw']
    user = authenticate(request, username=id,password=pw)
    if( user is None):
        return False
    else:
        login(request, user)
        u = User.objects.get(user_id=id)
        request.session['user_id'] = id
        request.session['role'] = u.role
        return True

def signout(request):
    logout(request)
    return

def delete_account(request):
    if(not request.user.is_authenticated) or (is_admin(request)):
        return False
    u = request.user
    signout(request)
    u.delete()
    return True
    
def update_info(request):
    u = get_user(request)
    form = request.POST

    try:
        u.user_id=form['id']
        u.birth = dateparse.parse_date(form['birth'])
        u.phone = form['phone']
        u.gender = get_gender_const(form['gender']) or User.Gender.MALE
        u.name = form['name']
        u.address = form['address']

        if(2<=len(str(form['pw']))<=15):
            u.set_password(form['pw'])
        u.save()
        request.session['user_id'] = str(u.user_id)
        return True
    except:
        return False

def get_user(request):
    user_id = get_id(request)
    if( user_id is None):
        return None
    else:
        return User.objects.get(user_id=get_id(request))

def get_id(request):
    if('user_id' in request.session):
        return request.session['user_id']
    else:
        return None

def get_role(request):
    if('role' in request.session):
        return request.session['role']
    else:
        return 'G'

_dict_role_fullname={
    'G':"Guest",
    'S':"Submitter",
    'A':"Administrator",
    'E':"Evaluator"
}

def get_role_fullname(request):
    r = get_role(request)
    return _dict_role_fullname[r]
def get_role_constant(str, allow_admin=False):
    i = str[0].lower()
    if(i=='s'):
        return User.UserType.SUBMITTER
    elif(i=='e'):
        return User.UserType.EVALUATOR
    elif(i=='a' and allow_admin):
        return User.UserType.ADMIN
    else:
        return None

def get_role_initial(str):
    return str[0]

def is_admin(request):
    return get_role(request) == 'A'

def is_guest(request):
    return get_role(request) == 'G'

def is_submitter(request):
    return get_role(request) == 'S'

def is_evaluator(request):
    return get_role(request) == 'E'

_dict_gender_fullname={
    'M':"Male",
    'F':"Female",
    'U':"Unknown"
}

def get_gender(request):
    if(is_guest(request)):
        return 'U'
    g = request.user.gender
    if(g not in _dict_gender_fullname):
        g = 'U'
    return g

def get_gender_fullname(request):
    g = get_gender(request)
    return _dict_gender_fullname[g]
def get_gender_const(str):
    i = str[0].lower()
    if(i=='m'):
        return User.Gender.MALE
    elif(i=='f'):
        return User.Gender.FEMALE
    else:
        return None