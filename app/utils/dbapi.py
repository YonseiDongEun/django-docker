from .dbinterface import *
from . import task
from app import models
from app.utils import validation

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
    tablename = "USER left join PARTICIPATES_IN as pin on id=pin.uid left join TASK_METADATA as tmd on pin.table_name=tmd.table_name"
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
    errs = []
    res = {'errs':errs}
    validation.validate(validation.display_name,json_data['display_name'],errs)
    validation.validate(validation.description,json_data['description'],errs)
    new_task=None
    if(len(errs)==0):
        new_task = task.TaskDescriptor(json_data)
        if(new_task.table_exists()):
            result= False
        else:
            result = new_task.create()
            res['table_name'] = new_task.table_name
    
    res['success']=result
    return JsonResponse(res, safe=False)

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

def api_get_raw_data(request,taskname,rawname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    print("_"*32)
    print(rawname)
    models.RawFileMetadata.objects.get(table_name=rawname)
    return _get_query_result(request,rawname)

def api_get_pending_submitters(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "PARTICIPATES_IN, USER"
    where_=f"uid=id and status='p' and table_name='{taskname}'"
    fields = to_fields(['user_id','name','birth','phone','gender','user_address'])
    return _get_query_result(request,tablename,where_,fields)

def api_get_approved_submitters(request,taskname):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    tablename = "PARTICIPATES_IN, USER"
    where_=f"uid=id and status='a' and table_name='{taskname}'"
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

    errs = []
    res = {'errs':errs}
    json_data=None
    result = False
    if(request.body):
        json_data = json.loads(request.body)
    

    validation.validate(validation.display_name,json_data['display_name'],errs)
    new_raw = task.RawDescriptor(json_data)
    if(len(errs)==0):
        if(not new_raw.is_valid() or new_raw.table_exists()):
            result= False
        else:
            result = new_raw.create()
            res['table_name']=new_raw.table_name

    res['success']= result
    return JsonResponse(res,safe=False)

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

def api_update_account(request):
    errs = []
    res = {'success':False, 'errs':errs}
    if(request.body):
        json_data = json.loads(request.body)
        res['success'] = account.update_info(request, json_data, errs)
    return JsonResponse(res,safe=False)

def api_create_account(request):
    errs = []
    res = {'success':False, 'errs':errs}
    if(request.body):
        json_data = json.loads(request.body)
        print(json_data)
        res['success'] = account.create_account(request, json_data, errs)
    if(res['success']):
        account.signin(request,json_data)
    return JsonResponse(res,safe=False)

def api_signin(request):
    errs = []
    res = {'success':False, 'errs':errs}
    if(request.body):
        json_data = json.loads(request.body)
        res['success'] = account.signin(request, json_data)
    if(res['success']):
        account.signin(request,json_data)
    else:
        res['errs'] = ["sign in failed"]
    return JsonResponse(res,safe=False)

def api_get_user_detail(request,usr_id):
    if not account.is_admin(request):
        return userinterface.render_template_error_UI(request,403)

    usr = models.User.objects.get(user_id=usr_id)
    fields = None
    select_ = None
    tablename = None
    where_=f"user_id='{usr_id}'"
    if(usr.role==models.User.UserType.ADMIN):
        fields = to_fields(["user_id","name","role","gender","phone","birth","user_address","age"])
        tablename = "USER"
        select_="*,cast(datediff(now(),birth)/365 as signed) as age"
    elif(usr.role==models.User.UserType.EVALUATOR):
        fields = to_fields(["user_id","name","role","gender","phone","birth","user_address","age",'submission_id'])
        tablename = "USER left join IS_ASSIGNED_TO as iat on id=iat.uid"
        select_="*,cast(datediff(now(),birth)/365 as signed) as age, iat.pds_id as submission_id"
    elif(usr.role==models.User.UserType.SUBMITTER):
        fields = to_fields(["user_id","name","role","gender","phone","birth","user_address","age","task_name","status"])
        tablename = "USER left join PARTICIPATES_IN as pin on id=pin.uid left join TASK_METADATA as tmd on pin.table_name=tmd.table_name"
        select_="*,cast(datediff(now(),birth)/365 as signed) as age, tmd.display_name as task_name"

    return _get_query_result(request,tablename,pwhere_=where_, fields=fields,select_=select_)
