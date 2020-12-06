from .dbinterface import *
from . import task
from app import models

def _get_query_result(request, tablename, pwhere_="TRUE", fields=None, select_=None):
    where_ = pwhere_
    if(request.body):
        json_data = json.loads(request.body)
        if('sql_st' in json_data)and(json_data['sql_st']!=""):
            where_ = f"{where_} and {json_data['sql_st']}"
    tuples = select_from_where(tablename,where_,fields,select_)
    if(not tuples.is_success()):
        print("success:false")
        tuples = select_from_where(tablename,pwhere_,fields,select_)
        tuples.set_success(False)

    return tuples.toJsonResponse()

def api_get_users(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    fields = to_fields(["user_id","name","role","gender","phone","birth","user_address","age",'status','task_name'])
    tablename = "USER left join participates_in as pin on id=pin.uid left join task_metadata as tmd on pin.table_name=tmd.table_name"
    select_="*,cast(datediff(now(),birth)/365 as signed) as age, tmd.display_name as task_name"
    return _get_query_result(request,tablename,fields=fields,select_=select_)

def api_get_tasks(request):
    if account.is_admin(request):
        tablename = "TASK_METADATA"
        return _get_query_result(request,tablename)
    elif account.is_submitter(request):
        tablename = "TASK_METADATA"
        return _get_query_result(request,tablename,"activated=1")
    else:
        return userinterface.render_template_error_UI(request,403)

def api_create_task(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    json_data=None
    result = False
    if(request.body):
        json_data = json.loads(request.body)
    new_task = task.TaskDescriptor(json_data)
    if(not new_task.is_valid() or new_task.table_exists()):
        result= False
    else:
        result = new_task.create()
    return JsonResponse({'success':result, 'table_name':new_task.table_name},safe=False)

def api_update_task(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    json_data=None
    result = False
    if(request.body):
        json_data = json.loads(request.body)
    to_update = task.TaskDescriptor(json_data)
    result = to_update.update()
    return JsonResponse({'success':result},safe=False)

def api_get_raw_types(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "RAW_FILE_METADATA"
    return _get_query_result(request,tablename,f"task_name='{taskname}'")

def api_get_accepted_data(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    models.TaskMetadata.objects.get(table_name=taskname)
    return _get_query_result(request,taskname)

def api_get_pending_data(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    models.TaskMetadata.objects.get(table_name=taskname)
    return _get_query_result(request,taskname+"_wait")

def api_get_pending_submitters(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "participates_in, user"
    where_="uid=id and status='p'"
    fields = to_fields(['user_id','name','birth','phone','gender','user_address'])
    return _get_query_result(request,tablename,where_,fields)

def api_get_approved_submitters(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "participates_in, user"
    where_="uid=id and status='a'"
    fields = to_fields(['user_id','name','birth','phone','gender','user_address'])
    return _get_query_result(request,tablename,where_,fields)

def api_update_pending_submitters(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)
    data = None
    if(request.body):
        data = json.loads(request.body)
    
    tsk = models.TaskMetadata.objects.get(table_name=taskname)
    usr = models.User.objects.get(user_id=data['user_id'])
    result = models.ParticipatesIn.objects.get(uid=usr.id,table_name=taskname)

    result.status = data['status']
    result.save()
    return JsonResponse({'success':True},safe=False)

def api_create_raw_type(request):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    json_data=None
    result = False
    if(request.body):
        json_data = json.loads(request.body)
    new_raw = task.RawDescriptor(json_data)
    
    if(not new_raw.is_valid() or new_raw.table_exists()):
        result= False
    else:
        result = new_raw.create()

    return JsonResponse({'success':result, 'table_name':new_raw.table_name},safe=False)

def api_submitter_pending_status(request, taskname):
    if not account.is_submitter(request):
        return userinterface.render_template_error_UI(request,403)
    
    status = "N"
    try:
        result = models.ParticipatesIn.objects.get(uid=request.user.id,table_name=taskname)
        status =  result.status
    except:
        pass

    status = status.lower()
    if(status=='p'):
        status = "pending"
    elif(status=='r'):
        status = "rejected"
    elif(status=='a'):
        status = 'approved'
    elif(status=='n'):
        status = "none"
    else:
        status = None
    return JsonResponse({'success':True, 'status':status},safe=False)


def api_submitter_request_permission(request, taskname):
    print("TEST")
    if not account.is_submitter(request):
        return userinterface.render_template_error_UI(request,403)
    
    status = "N"
    tsk = models.TaskMetadata.objects.get(table_name=taskname)
    usr = models.UserSubmitter.objects.get(user=request.user)
    try:
        result = models.ParticipatesIn.objects.get(uid=usr,table_name=tsk)
        status =  result.status
    except:
        pass

    status = status.lower()
    if(status!='n'):
        return userinterface.render_template_error_UI(request,403)
    
    success=False
    try:
        new_status = models.ParticipatesIn(uid=usr,table_name=tsk,status='p')
        new_status.save()
        success=True
    except:
        pass

    return JsonResponse({'success':success},safe=False)