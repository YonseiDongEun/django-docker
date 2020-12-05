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
    # evaluator

    # admin
    path('tskstat/', view_tskstat, name='tskstat'),
    path('tskstat/<tblname>/', view_tskstat_per_task, name='tskstat_per_task'),
    path('tskcreate/', view_tskcreate, name='tskcreate'),
    path('tskmgmt/', view_tskmgmt, name='tskmgmt'),
    path('tskmgmt/<tblname>/', view_tskmgmt_per_task, name='tskmgmt_per_task'),
    path('usrmgmt/', view_usrmgmt, name='usrmgmt'),
    path('usrmgmt/<usrid>/', view_usrmgmt_per_user, name='usrmgmt_per_user'),

    # api
    path('api/db/users/',api_get_users, name='api_db_users'),
    path('api/db/tasks/',api_get_tasks, name='api_db_tasks'),
    path('api/db/task/create',api_create_task, name='api_db_create_task'),
]

app_name = 'app'