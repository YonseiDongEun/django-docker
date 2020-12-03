from app.models import User
from . import account,userinterface
from django.http import JsonResponse
from django.db import connection
import re
import json

class QueryResultSerializable:
    def __init__(self, fields=None):
        self.serializable = [False,[]]
        if(fields is not None):
            self.set_ordered_fields(fields)
        return

    def toJsonResponse(self):
        return JsonResponse(self.serializable, safe=False)

    def set_success(self,is_success):
        self.serializable[0]= is_success
    
    def is_success(self):
        return self.serializable[0]
    
    def set_ordered_fields(self,orderedFields):
        self.serializable[1] = orderedFields
    
    def get_ordered_fields(self):
        return self.serializable[1]

    def select_fields(self, u):
        fields = self.get_ordered_fields()
        result = {}
        for field in fields:
            result[field] = u[field.upper()]
        return result
    
    def clear_tuples(self):
        self.serializable = self.serializable[:2]
    
    def get_tuples(self):
        return self.serializable[2:]

    def do_select(self, from_, where_):
        self.clear_tuples()
        sql_st = f"SELECT * FROM {from_} WHERE {where_}"
        sql_st = to_safe_sql_select(sql_st)
        try:
            query_result = None
            with connection.cursor() as cursor:
                cursor.execute(sql_st)
                query_result = dictfetchall(cursor)
            self.set_success(True)
            self.serializable = self.serializable + [self.select_fields(u) for u in query_result]
            return True
        except:
            self.set_success(False)
            return False
    
    def fetch_fieldnames(self, from_):
        sql_st = f"SHOW COLUMNS FROM {from_};"
        sql_st = to_safe_sql_show(sql_st)
        try:
            query_result = None
            with connection.cursor() as cursor:
                cursor.execute(sql_st)
                query_result = dictfetchall(cursor)
            fields =  [u['Field'] for u in query_result]
            self.set_ordered_fields(fields)
            return True
        except:
            return False
    

def create_account(id_,pw_,role_):
    new_user = User(id=id_,role=role_)
    new_user.set_password(pw_)
    new_user.save()

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def to_safe_sql_select(sql_st):
    sql_st = sql_st+';'
    mat = re.match("^SELECT .{0,512}?;", sql_st)
    return mat.group()

def to_safe_sql_show(sql_st):
    sql_st = sql_st+';'
    mat = re.match("^SHOW .{0,512}?;", sql_st)
    return mat.group()

def to_safe_sql_identifier(fieldname):
    fieldname = "dyn17_"+fieldname
    mat = re.match("^[a-zA-Z_][a-zA-Z_0-9]{0,32}", fieldname)
    return mat.group()

def table_exists(tablename):
    tables = connection.introspection.table_names()
    return tablename in tables

def get_fields(tablename):
    if(not table_exists(tablename)):
        return None
    fields = QueryResultSerializable()
    fields.fetch_fieldnames(tablename)
    return fields.get_ordered_fields()
