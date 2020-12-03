from .dbinterface import *

def _get_query_result(request, tablename, fields=None):
    where_="TRUE"
    if(request.body):
        json_data = json.loads(request.body)
        if('sql_st' in json_data)and(json_data['sql_st']!=""):
            where_ = json_data['sql_st']

    tuples = QueryResultSerializable(fields)
    if(fields is None):
        tuples.fetch_fieldnames(tablename)
    
    if(not tuples.do_select(tablename,where_)):
        tuples.do_select(tablename,"TRUE")
        tuples.set_success(False)

    return tuples.toJsonResponse()

def api_get_users(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    fields = ["user_id","name","role","gender","phone","birth","user_address"]
    tablename = "USER"
    return _get_query_result(request,tablename,fields)

def api_get_tasks(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "TASK_METADATA"
    return _get_query_result(request,tablename)