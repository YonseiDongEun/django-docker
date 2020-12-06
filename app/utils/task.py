from . import dbinterface
from app.models import TaskMetadata, RawFileMetadata
from django.db import connection


class TaskDescriptor:
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
    
    def update(self):
        if(not self.is_valid() or not self.table_exists()):
            return False
        try:
            to_update = TaskMetadata.objects.get(table_name=self.table_name)
            to_update.description = self.description
            to_update.min_upload_cycle = self.upload_cycle
            to_update.pass_criterion = self.pass_criterion
            to_update.activated = self.activated
            to_update.display_name = self.display_name

            to_update.save()
            return True
        except:
            return False

    def create(self):

        if(not self.is_valid()):
            return False
        
        if(self.table_name is None):
            self.table_name = self.display_name
        
        self.table_name = dbinterface.get_available_task_table_name(self.table_name)
        self.columns.append({'fieldname':'_submitter_id','fieldtype':'INT'})
        self.columns.append({'fieldname':'_submitter_name','fieldtype':'TEXT'})
        
        result = dbinterface.create_table(self.table_name, self.columns)
        if(not result):
            return False
        result = dbinterface.create_table(self.get_waiting_tablename(), self.columns)
        if(not result):
            return False
        try:
            new_task = TaskMetadata(table_name=self.table_name,display_name=self.display_name,description=self.description,min_upload_cycle=self.upload_cycle,activated=self.activated,pass_criterion=self.pass_criterion)
            new_task.save()
            return True
        except:
            return False

    # debugging only
    def delete(self):
        with connection.cursor() as cursor:
            to_del = TaskMetadata.objects.get(table_name=self.table_name)
            to_del_rs = RawFileMetadata.objects.filter(task_name=to_del)
            for to_del_r in to_del_rs:
                print(f"DEBUGGING: deleting {to_del_r.table_name}.")
                cursor.execute(f"drop table {to_del_r.table_name}")
                to_del_r.delete()

            to_del.delete()
            cursor.execute(f"drop table {self.table_name}")
            cursor.execute(f"drop table {self.get_waiting_tablename()}")
            print(f"DEBUGGING: deleted {self.table_name}.")

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
        self.columns = dbinterface.get_fields(self.table_name, True)
        return True
    
    def get_columns(self):
        if(self.fetch_meta()):
            return self.columns
        else:
            return None

    def get_context(self):

        context = {'display_name':self.display_name,
            'table_name':self.table_name,
            'description':self.description,
            'pass_criterion':self.pass_criterion,
            'upload_cycle':self.upload_cycle,
            'activated':self.activated==b'\x01' and 1 or 0,
            'columns':self.columns}
        return context

    def get_raws(self):

        tsk = TaskMetadata.objects.get(table_name=self.table_name)
        raws = RawFileMetadata.objects.filter(task_name=tsk)
        return [ {'table_name':x.table_name,'display_name':x.display_name,'size':dbinterface.get_count(x.table_name)} for x in raws]



class RawDescriptor:
    def __init__(self, data):
        self.display_name = data.get("display_name")
        self.table_name = data.get("table_name")
        self.task_name = data.get("task_name")
        self.columns = data.get("columns")
        self.mapping_select = data.get("mapping_select").replace('\n',' ')
        return
    
    def is_valid(self):
        return self.display_name is not None
    
    def table_exists(self):
        return dbinterface.table_exists(self.table_name)
    
    def create(self):
        if(not self.is_valid()):
            return False
        self.columns.append({'fieldname':'_submitter_id','fieldtype':'INT'})
        self.columns.append({'fieldname':'_submitter_name','fieldtype':'TEXT'})
           
        if(self.table_name is None):
            self.table_name = self.display_name
        self.table_name = dbinterface.get_available_table_name(self.table_name)
        
        dbinterface.create_table(self.table_name, self.columns)
        try:
            original_task = TaskMetadata.objects.get(table_name=self.task_name)
            new_raw = RawFileMetadata(table_name=self.table_name,display_name=self.display_name,mapping_sql_query=self.mapping_select,task_name=original_task)
            new_raw.save()
            return True
        except:
            return False

    def fetch_meta(self):
        if(not self.table_exists()):
            return False
        meta = RawFileMetadata.objects.get(table_name=self.table_name)
        self.display_name = meta.display_name
        self.mapping_select = meta.mapping_sql_query
        self.task_name = meta.task_name
        self.columns = dbinterface.get_fields(self.table_name)
        return True
    
    def get_columns(self):
        if(self.fetch_meta()):
            return self.columns
        else:
            return None

