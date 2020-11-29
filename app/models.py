from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Evaluates(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID', primary_key=True)
    pds = models.ForeignKey('ParsingDataSeq', models.DO_NOTHING, db_column='PDS_ID')
    status = models.CharField(db_column='STATUS', max_length=1)
    p_np = models.TextField(db_column='P_NP')
    rating = models.IntegerField(db_column='RATING')

    class Meta:
        managed = False
        db_table = 'EVALUATES'
        unique_together = (('uid', 'pds'),)


class IsAssignedTo(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID', primary_key=True)
    pds = models.ForeignKey('ParsingDataSeq', models.DO_NOTHING, db_column='PDS_ID')
    due = models.DateField(db_column='DUE')

    class Meta:
        managed = False
        db_table = 'IS_ASSIGNED_TO'
        unique_together = (('uid', 'pds'),)


class NullRatioPerColumn(models.Model):
    pds = models.OneToOneField('ParsingDataSeq', models.DO_NOTHING, db_column='PDS_ID', primary_key=True)
    null_ratio = models.FloatField(db_column='NULL_RATIO')

    class Meta:
        managed = False
        db_table = 'NULL_RATIO_PER_COLUMN'
        unique_together = (('pds', 'null_ratio'),)


class ParsingDataSeq(models.Model):
    pds_id = models.CharField(db_column='PDS_ID', primary_key=True, max_length=15)
    total_tuple_count = models.IntegerField(db_column='TOTAL_TUPLE_COUNT')
    duplicated_tuple_count = models.IntegerField(db_column='DUPLICATED_TUPLE_COUNT')

    class Meta:
        managed = False
        db_table = 'PARSING_DATA_SEQ'


class ParticipatesIn(models.Model):
    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID', primary_key=True)
    table_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING, db_column='TABLE_NAME')
    status = models.CharField(db_column='STATUS', max_length=1)

    class Meta:
        managed = False
        db_table = 'PARTICIPATES_IN'
        unique_together = (('uid', 'table_name'),)


class PrevEvaluators(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID', primary_key=True)
    pds = models.ForeignKey(ParsingDataSeq, models.DO_NOTHING, db_column='PDS_ID')
    prev_evaluator = models.CharField(db_column='PREV_EVALUATOR', max_length=15)

    class Meta:
        managed = False
        db_table = 'PREV_EVALUATORS'
        unique_together = (('uid', 'pds'),)


class RawDataSeq(models.Model):
    rds_id = models.CharField(db_column='RDS_ID', primary_key=True, max_length=15)

    class Meta:
        managed = False
        db_table = 'RAW_DATA_SEQ'


class RawDataTemplate(models.Model):
    rdt_id = models.CharField(db_column='RDT_ID', primary_key=True, max_length=15)
    raw_data = models.TextField(db_column='RAW_DATA')

    class Meta:
        managed = False
        db_table = 'RAW_DATA_TEMPLATE'


class RawFileMetadata(models.Model):
    table_name = models.CharField(db_column='TABLE_NAME', primary_key=True, max_length=15)
    display_name = models.CharField(db_column='DISPLAY_NAME', max_length=15)
    mapping_sql_query = models.CharField(db_column='MAPPING_SQL_QUERY', max_length=1000)
    task_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING, db_column='TASK_NAME')

    class Meta:
        managed = False
        db_table = 'RAW_FILE_METADATA'


class RequestsNew(models.Model):
    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID', primary_key=True)
    table_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING, db_column='TABLE_NAME')
    rdt = models.ForeignKey(RawDataTemplate, models.DO_NOTHING, db_column='RDT_ID')
    status = models.CharField(db_column='STATUS', max_length=1)

    class Meta:
        managed = False
        db_table = 'REQUESTS_NEW'
        unique_together = (('uid', 'table_name', 'rdt'),)


class Submission(models.Model):
    subm_id = models.CharField(db_column='SUBM_ID', primary_key=True, max_length=15)
    submit_count = models.IntegerField(db_column='SUBMIT_COUNT')
    duration_info = models.TimeField(db_column='DURATION_INFO')
    parsed = models.TextField(db_column='PARSED')

    class Meta:
        managed = False
        db_table = 'SUBMISSION'


class Submits(models.Model):
    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID', primary_key=True)
    table_name = models.ForeignKey(RawFileMetadata, models.DO_NOTHING, db_column='TABLE_NAME')
    subm = models.ForeignKey(Submission, models.DO_NOTHING, db_column='SUBM_ID')

    class Meta:
        managed = False
        db_table = 'SUBMITS'
        unique_together = (('uid', 'table_name', 'subm'),)


class TaskMetadata(models.Model):
    table_name = models.CharField(db_column='TABLE_NAME', primary_key=True, max_length=15)
    display_name = models.CharField(db_column='DISPLAY_NAME', max_length=15)
    description = models.CharField(db_column='DESCRIPTION', max_length=100, blank=True, null=True)
    min_upload_cycle = models.IntegerField(db_column='MIN_UPLOAD_CYCLE')
    activated = models.TextField(db_column='ACTIVATED')
    pass_criterion = models.IntegerField(db_column='PASS_CRITERION')

    class Meta:
        managed = False
        db_table = 'TASK_METADATA'


class User(AbstractBaseUser):
    id = models.CharField(db_column='ID', primary_key=True, max_length=15)
    password = models.CharField(db_column='PW', max_length=128)
    name = models.CharField(db_column='NAME', max_length=15, blank=True, null=True)
    birth = models.DateField(db_column='BIRTH', blank=True, null=True)
    phone = models.CharField(db_column='PHONE', max_length=11, blank=True, null=True)
    gender = models.CharField(db_column='GENDER', max_length=1, blank=True, null=True)
    role = models.CharField(db_column='ROLE', max_length=1)
    last_login = None

    class Meta:
        managed = False
        db_table = 'USER'

    @property
    def is_staff(self) -> bool:
        return self.is_evaluator

    @property
    def is_superuser(self) -> bool:
        return self.is_admin

    @property
    def is_evaluator(self) -> bool:
        try:
            return bool(self.user_evaluator)
        except ObjectDoesNotExist:
            return False

    @property
    def is_admin(self) -> bool:
        try:
            return bool(self.user_admin)
        except ObjectDoesNotExist:
            return False

    @property
    def is_submitter(self) -> bool:
        try:
            return bool(self.user_submitter)
        except ObjectDoesNotExist:
            return False


class UserAdmin(models.Model):
    id = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True, related_name='user_admin')

    class Meta:
        managed = False
        db_table = 'USER_ADMIN'


class UserEvaluator(models.Model):
    id = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True, related_name='user_evaluator')

    class Meta:
        managed = False
        db_table = 'USER_EVALUATOR'


class UserSubmitter(models.Model):
    id = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True, related_name='user_submitter')

    class Meta:
        managed = False
        db_table = 'USER_SUBMITTER'
