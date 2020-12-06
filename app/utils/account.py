from django import forms
from django.contrib.auth import authenticate, login, logout
from django.utils import dateparse
from app.models import User
from app.utils import validation

class SignupForm(forms.Form):
    user_id = forms.CharField(min_length=2, max_length=15)
    name = forms.CharField(max_length=15)
    address = forms.CharField(max_length=64)
    birth = forms.DateField()
    phone = forms.CharField(max_length=11)
    gender = forms.CharField(max_length=1)
    role = forms.CharField(max_length=1)


def create_account(request,data,errs):
        
    data['birth'] = dateparse.parse_date(data['birth'])
    validation.validate(validation.user_id,data['user_id'],errs)
    validation.validate(validation.birth,data['birth'],errs)
    validation.validate(validation.phone,data['phone'],errs)
    validation.validate(validation.name,data['name'],errs)
    validation.validate(validation.address,data['address'],errs)
    validation.validate(validation.password_init,data['pw'],errs)

    if(len(errs)>0):
        return False

    data['role'] = get_role_constant(data['role'])
    if(data['role'] is None):
        return False
    
    data['gender'] = get_gender_const(data['gender'])
    if(data['gender'] is None):
        return False
    
    try:
        r=User.objects.create(user_id=data['user_id'],name=data['name'],address=data['address'],gender=data['gender'],phone=data['phone'],birth=data['birth'],role=data['role'])
        r.set_password(data['pw'])
        r.save()
        return True
    except:
        return False

def signin(request,data):
    id = data['user_id']
    pw = data['pw']
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
    
def update_info(request, data, errs):
    u = get_user(request)
    
    data['birth'] = dateparse.parse_date(data['birth'])
    validation.validate(validation.user_id,data['user_id'],errs)
    validation.validate(validation.birth,data['birth'],errs)
    validation.validate(validation.phone,data['phone'],errs)
    validation.validate(validation.name,data['name'],errs)
    validation.validate(validation.address,data['address'],errs)
    validation.validate(validation.password,data['pw'],errs)
    if(len(errs)>0):
        return False
    try:
        u.user_id=data['user_id']
        u.birth = data['birth']
        u.phone = data['phone']
        u.gender = get_gender_const(data['gender']) or User.Gender.MALE
        u.name = data['name']
        u.address = data['address']

        if(data['pw']!=''):
            u.set_password(data['pw'])
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