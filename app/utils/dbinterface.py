from app.models import User
from . import account,userinterface
from django.core import serializers
from django.http import JsonResponse, HttpResponse
def create_account(id_,pw_,role_):
    new_user = User(id=id_,role=role_)
    new_user.set_password(pw_)
    new_user.save()

def api_get_users(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)
    
    users = User.objects.only("user_id")#,"name","role","gender","phone","birth")

    # cur.execute("select ID,Role from users")
    res = serializers.serialize('json',users)
    return HttpResponse(res,content_type="application/json")
