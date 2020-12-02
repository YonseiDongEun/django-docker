from django.urls import path

from app.views.submits import upload
from app.views.general import *
from app.utils.dbinterface import api_get_users

urlpatterns = [
    # general
    path('', view_root, name='root'),
    path('signin/', view_signin, name='signin'),
    path('signup/', view_signup, name='signup'),
    path('signout/', view_signout, name='signout'),
    path('myaccount/', view_myaccount, name='myaccount'),
    
    # submitter
    path('upload/', upload, name='submit'),
    # evaluator

    # admin
    path('tskstat/', view_tskstat, name='tskstat'),
    path('tskcreate/', view_tskcreate, name='tskcreate'),
    path('tskmgmt/', view_tskmgmt, name='tskmgmt'),
    path('usrmgmt/', view_usrmgmt, name='usrmgmt'),

    # api
    path('api/db/users/',api_get_users, name='api_db_users'),
]

app_name = 'app'