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

    #TODO: verity these are safe and legal
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

    if(role_=='submitter'):
        role_ = User.UserType.SUBMITTER
    elif(role_=='evaluator'):
        role_ = User.UserType.EVALUATOR
    else:
        return False
    
    if(gender_=="male"):
        gender_ = User.Gender.MALE
    elif(gender_=="female"):
        gender_ = User.Gender.FEMALE
    else:
        return False
    
    birth_ = dateparse.parse_date(birth_)
    if(birth_ is None):
        pass

    r=User.objects.create(user_id=id_,name=name_,address=address_,gender=gender_,phone=phone_,birth=birth_,role=role_)
    r.set_password(pw_)
    r.save()

    return True

def signin(request):
    id = request.POST['id']
    pw = request.POST['pw']
    user = authenticate(request, username=id,password=pw)
    print(user)
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

def update_info(request):
    u = get_user(request)
    form = request.POST

    u.user_id=form['id']
    u.birth = dateparse.parse_date(form['birth'])
    u.phone = form['phone']
    # u.gender = form['gender']
    u.name = form['name']
    u.address = form['address']

    if(2<=len(str(form['pw']))<=15):
        u.set_password(form['pw'])
    u.save()
    request.session['user_id'] = str(u.user_id)
    return

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

def get_role_fullname(request):
    r = get_role(request)
    if(r=='G'):
        return "guest"
    elif(r=='S'):
        return "submitter"
    elif(r=='A'):
        return "administrator"
    elif(r=='E'):
        return "evaluator"
    else:
        raise Exception("invalid case")
    
def is_admin(request):
    return get_role(request) == 'A'
    # return get_role()=="admin"

