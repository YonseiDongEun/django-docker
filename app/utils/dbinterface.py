from app.models import User
from . import account,userinterface
from django.http import JsonResponse
from django.db import connection
import re
import json

class QueryResultSerializable:
    def __init__(self, fields=None, select_=None):
        self.serializable = {'success':False,'fields':[],'tuples':[]}
        self.select_ = select_ or "*"
        if(fields is not None):
            self.set_ordered_fields(fields)
        return

    def toJsonResponse(self):
        return JsonResponse(self.serializable, safe=False)

    def set_success(self,is_success):
        self.serializable['success']= is_success
    
    def is_success(self):
        return self.serializable['success']
    
    def set_ordered_fields(self,orderedFields):
        self.serializable['fields'] = orderedFields
    
    def get_ordered_fields(self, hide_internal=False):
        fields = self.serializable['fields']
        if(hide_internal):
            fields = [x for x in fields if not x['fieldname'].startswith('_')]

        return fields

    def select_fields(self, u):
        fields = self.get_ordered_fields()
        result = {}
        for field in fields:
            fieldname = field['fieldname']
            if(fieldname in u):
                result[fieldname] = u[fieldname]
            else:
                result[fieldname] = u[fieldname.upper()]
            if(type(result[fieldname])==bytes):
                result[fieldname] = int.from_bytes(result[fieldname], "big")
        return result
    
    def clear_tuples(self):
        self.serializable['tuples'] = []
    
    def get_tuples(self):
        return self.serializable['tuples']

    def do_select(self, from_, where_):
        self.clear_tuples()
        if(len(self.get_ordered_fields())==0):
            self.fetch_fieldnames(from_)
        sql_st = f"SELECT {self.select_} FROM {from_} WHERE {where_}"
        sql_st = to_safe_sql_select(sql_st)
        print(sql_st)
        try:
            query_result = None
            with connection.cursor() as cursor:
                cursor.execute(sql_st)
                query_result = dictfetchall(cursor)
            self.set_success(True)
            self.get_tuples().extend([self.select_fields(u) for u in query_result])
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
            fields = [{'fieldname':u['Field'], 'fieldtype':u['Type']} for u in query_result]
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

def to_safe_sql_create_table(sql_st):
    sql_st = sql_st+';'
    mat = re.match("^CREATE TABLE .{0,512}?;", sql_st)
    return mat.group()

def to_safe_sql_identifier(fieldname, prefix="dyn17_"):
    fieldname = fieldname.replace(" ","_")
    fieldname = fieldname.replace("\n","_")
    fieldname = prefix+fieldname
    mat = re.match("^[a-zA-Z_][a-zA-Z_0-9]{0,32}", fieldname)
    return mat.group()

def table_exists(tablename):
    if(tablename is None):
        return False
    tables = connection.introspection.table_names()
    return tablename.lower() in tables

def get_fields(tablename, hide_internal = False):
    if(not table_exists(tablename)):
        return None
    fields = QueryResultSerializable()
    fields.fetch_fieldnames(tablename)
    return fields.get_ordered_fields(hide_internal)

_allowed_fieldtype = ['text','int','real','date','time']

def get_available_table_name(tablename):
    basename = to_safe_sql_identifier(tablename)
    tablename = basename
    idx = 0
    while(table_exists(tablename)):
        tablename = f"{basename}_{idx}"
        idx = idx+1
    return tablename

def get_available_task_table_name(tablename):
    basename = to_safe_sql_identifier(tablename)
    tablename = basename
    idx = 0
    while(table_exists(tablename) or table_exists(tablename+"_wait")):
        tablename = f"{basename}_{idx}"
        idx = idx+1
    return tablename

def create_table(tablename, fields):
    if(table_exists(tablename)):
        return False
    sql_var_definition = "_id_auto_increment int auto_increment, primary key(_id_auto_increment)"

    for i in range(0,len(fields)):
        fields[i]['fieldname'] = to_safe_sql_identifier(fields[i]['fieldname'],"")
        fields[i]['fieldtype'] = fields[i]['fieldtype'].lower()
        if(fields[i]['fieldtype'] not in _allowed_fieldtype):
            fields[i]['fieldtype'] = _allowed_fieldtype[0]
        sql_var_definition = sql_var_definition + f", {fields[i]['fieldname']} {fields[i]['fieldtype']}"
    
    sql_create = to_safe_sql_create_table(f"CREATE TABLE {tablename}({sql_var_definition});")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_create)
            return True
    except:
        return False

def select_from_where(from_, where_="TRUE", fields=None, select_=None):
    tuples = QueryResultSerializable(fields,select_)
    if(fields is None):
        tuples.fetch_fieldnames(from_)
    
    tuples.do_select(from_,where_)
    return tuples

def to_fields(fieldnames):
    return [{'fieldname':x} for x in fieldnames]