from app.models import User
from . import account,userinterface
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.db import connection
import re
from urllib.parse import parse_qs
import json

def create_account(id_,pw_,role_):
    new_user = User(id=id_,role=role_)
    new_user.set_password(pw_)
    new_user.save()

def select_fields(fields, u):
    result = {}
    for field in fields:
        result[field] = u[field.upper()]
    return result

def do_select(fields, from_, where_):
    sql_st = f"SELECT * FROM {from_} WHERE {where_}"
    sql_st = to_safe_sql_statement(sql_st)
    print(sql_st)
    try:
        query_result = None
        with connection.cursor() as cursor:
            cursor.execute(sql_st)
            query_result = dictfetchall(cursor)
        return [fields]+ [select_fields(fields, u) for u in query_result]
    except:
        return None

def api_get_users(request):
    fields = ["user_id","name","role","gender","phone","birth"]
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)
    
    where_="TRUE"
    if(request.body):
        json_data = json.loads(request.body)
        if('sql_st' in json_data)and(json_data['sql_st']!=""):
            where_ = json_data['sql_st']

    users = do_select(fields, "USER", where_)
    if(users is not None):
        users = [True] + users
    else:
        users = [False] + do_select(fields, "USER","TRUE")

    return JsonResponse(users,safe=False)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def to_safe_sql_statement(sql_st):
    sql_st = sql_st.lower()+';'
    mat = re.match("^select .{0,64}?;", sql_st)
    return mat.group()