from django.urls import path

from app.views.submits import upload
from app.views.general import *
from app.utils.dbapi import *

urlpatterns = [
    # general
    path('', view_root, name='root'),
    path('signin/', view_signin, name='signin'),
    path('signup/', view_signup, name='signup'),
    path('signout/', view_signout, name='signout'),
    path('myaccount/', view_myaccount, name='myaccount'),
    path('myaccount/delete_account_confirmed', view_delete_account_confirmed, name='delmyaccount'),

    # submitter
    path('upload/', upload, name='submit'),
    path('tsklist/', view_tsklist_submitter, name='tsklist'),
    path('tsklist/<taskname>', view_tskdetail_submitter, name='tskdetail'),
    # evaluator

    # admin
    path('tskstat/', view_tskstat, name='tskstat'),
    path('tskstat/<tblname>/', view_tskstat_per_task, name='tskstat_per_task'),
    path('tskcreate/', view_tskcreate, name='tskcreate'),
    path('tskmgmt/', view_tskmgmt, name='tskmgmt'),
    path('tskmgmt/<tblname>/', view_tskmgmt_per_task, name='tskmgmt_per_task'),
        #debug only
    path('tskmgmt/<tblname>/delete', view_tskmgmt_per_task_del, name='tskmgmt_per_task_del'),
    path('usrmgmt/', view_usrmgmt, name='usrmgmt'),
    path('usrmgmt/<usrid>/', view_usrmgmt_per_user, name='usrmgmt_per_user'),

    # api
    path('api/db/users/',api_get_users, name='api_db_users'),
    path('api/db/tasks/',api_get_tasks, name='api_db_tasks'),
    path('api/db/task/create',api_create_task, name='api_db_create_task'),
    path('api/db/task/update',api_update_task, name='api_db_update_task'),
    path('api/db/task/raw_create',api_create_raw_type, name='api_db_create_raw'),
    path('api/db/task/<taskname>/raws',api_get_raw_types, name='api_db_get_raws'),
    path('api/db/task/<taskname>/pending',api_get_pending_submitters, name='api_db_get_pendings'),
    path('api/db/task/<taskname>/approved',api_get_approved_submitters, name='api_db_get_approved'),
    path('api/db/task/<taskname>/update_pending',api_update_pending_submitters, name='api_db_update_pendings'),
    path('api/db/task/<taskname>/task_accepted',api_get_accepted_data),
    path('api/db/task/<taskname>/task_pending',api_get_pending_data),

    path('api/db/task/<taskname>/status/',api_submitter_pending_status, name='api_db_submitter_status'),
    path('api/db/task/<taskname>/request/',api_submitter_request_permission , name='api_db_submitter_request'),
]

app_name = 'app'