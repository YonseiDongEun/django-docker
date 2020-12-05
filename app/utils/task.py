from . import dbinterface
from app.models import TaskMetadata
from django.db import connection

class TaskDescriptor:
    _allowed_fieldtype = ['TEXT','INT','REAL','DATE','TIME']
    def __init__(self, data):
        self.display_name = data.get("display_name")
        self.table_name = data.get("table_name")
        self.columns = data.get("columns")
        self.description = data.get("description")
        self.pass_criterion = data.get("pass_criterion")
        self.upload_cycle = data.get("upload_cycle")
        self.activated = data.get("activated")
        return
    
    def is_valid(self):
        return self.display_name is not None \
            and 2<len(self.display_name)<15 \
            and len(self.description)<100
    
    def table_exists(self):
        return dbinterface.table_exists(self.table_name)
    
    def create(self):

        if(self.table_exists() or not self.is_valid()):
            return False
        
        basename = dbinterface.to_safe_sql_identifier(self.display_name)
        self.table_name = basename
        idx = 0
        while(self.table_exists()):
            self.table_name = f"{basename}_{idx}"
            idx = idx+1
        self.columns.append({'fieldname':'submitter_name','fieldtype':'TEXT'})
        sql_var_definition = "_id_auto_increment int auto_increment, primary key(_id_auto_increment)"

        for i in range(0,len(self.columns)):
            
            self.columns[i]['fieldname'] = dbinterface.to_safe_sql_identifier(self.columns[i]['fieldname'],"")
            if(self.columns[i]['fieldtype'] not in self._allowed_fieldtype):
                self.columns[i]['fieldtype'] = 'TEXT'
            sql_var_definition = sql_var_definition + f", {self.columns[i]['fieldname']} {self.columns[i]['fieldtype']}"
        
        sql_create = f"CREATE TABLE {self.table_name}({sql_var_definition});"
        sql_create_wait = f"CREATE TABLE {self.get_waiting_tablename()}({sql_var_definition});"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_create)
                cursor.execute(sql_create_wait)
                new_task = TaskMetadata(table_name=self.table_name,display_name=self.display_name,description=self.description,min_upload_cycle=self.upload_cycle,activated=self.activated,pass_criterion=self.pass_criterion)
                new_task.save()
                return True
        except:
            return False

    def get_waiting_tablename(self):
        return self.table_name+"_wait"
        
    def fetch_meta(self):
        if(not self.table_exists()):
            return False
        meta = TaskMetadata.objects.get(table_name=self.table_name)
        self.display_name = meta.display_name
        self.description = meta.description
        self.pass_criterion = meta.pass_criterion
        self.upload_cycle = meta.min_upload_cycle
        self.activated = meta.activated
        self.columns = dbinterface.get_fields(self.table_name)
        return True




        



    
    
def create():
    return False

# Warning: debugging only
def delete():
    pass

def get():
    pass