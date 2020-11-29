from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import TextChoices


class Evaluates(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID',
                               primary_key=True)
    pds = models.ForeignKey('ParsingDataSeq', models.DO_NOTHING, db_column='PDS_ID', related_name='evaluates')
    status = models.CharField(db_column='STATUS', max_length=1, blank=True, null=True)
    p_np = models.IntegerField(db_column='P_NP')  # This field type is a guess.
    rating = models.IntegerField(db_column='RATING')

    class Meta:
        managed = False
        db_table = 'EVALUATES'
        unique_together = (('uid', 'pds'),)


class IsAssignedTo(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID',
                               primary_key=True)
    pds = models.ForeignKey('ParsingDataSeq', models.DO_NOTHING, db_column='PDS_ID', related_name='is_assigned_tos')
    due = models.DateField(db_column='DUE')

    class Meta:
        managed = False
        db_table = 'IS_ASSIGNED_TO'
        unique_together = (('uid', 'pds'),)


class NullRatioPerColumn(models.Model):
    pds = models.OneToOneField('ParsingDataSeq', models.CASCADE, db_column='PDS_ID',
                               primary_key=True)
    null_ratio = models.FloatField(db_column='NULL_RATIO')

    class Meta:
        managed = False
        db_table = 'NULL_RATIO_PER_COLUMN'
        unique_together = (('pds', 'null_ratio'),)


class ParsingDataSeq(models.Model):
    pds_id = models.BigAutoField(db_column='PDS_ID', primary_key=True)
    total_tuple_count = models.IntegerField(db_column='TOTAL_TUPLE_COUNT')
    duplicated_tuple_count = models.IntegerField(db_column='DUPLICATED_TUPLE_COUNT')

    class Meta:
        managed = False
        db_table = 'PARSING_DATA_SEQ'

    @property
    def table_name(self):
        return self.requests_new.table_name

    @property
    def rating(self):
        return getattr(self.evaluates.first(), 'rating', None)


class ParticipatesIn(models.Model):
    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID',
                               primary_key=True)
    table_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING,
                                   db_column='TABLE_NAME')
    status = models.CharField(db_column='STATUS', max_length=1)

    class Meta:
        managed = False
        db_table = 'PARTICIPATES_IN'
        unique_together = (('uid', 'table_name'),)


class PrevEvaluators(models.Model):
    uid = models.OneToOneField('UserEvaluator', models.CASCADE, db_column='UID',
                               primary_key=True)
    pds = models.ForeignKey(ParsingDataSeq, models.DO_NOTHING, db_column='PDS_ID')
    prev_evaluator = models.CharField(db_column='PREV_EVALUATOR', max_length=15)

    class Meta:
        managed = False
        db_table = 'PREV_EVALUATORS'
        unique_together = (('uid', 'pds'),)


class RawDataSeq(models.Model):
    rds_id = models.BigAutoField(db_column='RDS_ID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'RAW_DATA_SEQ'


class RawDataTemplate(models.Model):
    rdt_id = models.BigAutoField(db_column='RDT_ID', primary_key=True)
    raw_data = models.TextField(db_column='RAW_DATA')

    class Meta:
        managed = False
        db_table = 'RAW_DATA_TEMPLATE'

    @staticmethod
    def convert_csv_to_text(file):
        rows = [','.join([str(x) for x in row]) for row in file.get_sheet().array]
        return '\n'.join(rows)


class RawFileMetadata(models.Model):
    table_name = models.CharField(db_column='TABLE_NAME', primary_key=True, max_length=50)
    display_name = models.CharField(db_column='DISPLAY_NAME', max_length=15)
    mapping_sql_query = models.CharField(db_column='MAPPING_SQL_QUERY', max_length=1000)
    task_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING,
                                  db_column='TASK_NAME')

    class Meta:
        managed = False
        db_table = 'RAW_FILE_METADATA'


class RequestsNew(models.Model):
    class Status(TextChoices):
        PASS = 'P', 'pass'
        NON_PASS = 'N', 'non_pass'

    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID',
                               primary_key=True)
    table_name = models.ForeignKey('TaskMetadata', models.DO_NOTHING,
                                   db_column='TABLE_NAME')
    rdt = models.ForeignKey(RawDataTemplate, models.DO_NOTHING, db_column='RDT_ID')
    status = models.CharField(db_column='STATUS', max_length=1, choices=Status.choices)
    pds = models.OneToOneField('ParsingDataSeq', db_column='PDS_ID', on_delete=models.CASCADE,
                               related_name='requests_new')

    class Meta:
        managed = False
        db_table = 'REQUESTS_NEW'
        unique_together = (('uid', 'table_name', 'rdt'),)


class Submission(models.Model):
    subm_id = models.BigAutoField(db_column='SUBM_ID', primary_key=True)
    submit_count = models.IntegerField(db_column='SUBMIT_COUNT')
    duration_info = models.TimeField(db_column='DURATION_INFO')
    parsed = models.TextField(db_column='PARSED')  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'SUBMISSION'


class Submits(models.Model):
    uid = models.OneToOneField('UserSubmitter', models.CASCADE, db_column='UID',
                               primary_key=True)
    table_name = models.ForeignKey(RawFileMetadata, models.DO_NOTHING,
                                   db_column='TABLE_NAME')
    subm = models.ForeignKey(Submission, models.DO_NOTHING, db_column='SUBM_ID', null=True,
                             blank=True)  # 해당 연결관계의 필요성을 느끼지 못해 추가하지 않음

    class Meta:
        managed = False
        db_table = 'SUBMITS'
        unique_together = (('uid', 'table_name',),)


class TaskMetadata(models.Model):
    table_name = models.CharField(db_column='TABLE_NAME', primary_key=True, max_length=50)
    display_name = models.CharField(db_column='DISPLAY_NAME', max_length=15)
    description = models.CharField(db_column='DESCRIPTION', max_length=100, blank=True,
                                   null=True)
    min_upload_cycle = models.IntegerField(db_column='MIN_UPLOAD_CYCLE')
    activated = models.IntegerField(db_column='ACTIVATED')  # This field type is a guess.
    pass_criterion = models.IntegerField(db_column='PASS_CRITERION')

    # schema = models.TextField(verbose_name='생성 스키마')  # create table ~~~~
    # fields = models.TextField(verbose_name='필드 (순서대로)')  # ID, NAME, ....

    class Meta:
        managed = False
        db_table = 'TASK_METADATA'


class User(AbstractUser):
    class Gender(TextChoices):
        MALE = 'M', '남성'
        FEMALE = 'F', '여성'

    class UserType(TextChoices):
        ADMIN = 'A', '관리자'
        EVALUATOR = 'E', '평가자'
        SUBMITTER = 'S', '제출자'

    id = models.BigAutoField(db_column='ID', primary_key=True)
    name = models.CharField(db_column='NAME', max_length=15, blank=True, null=True, unique=True)
    birth = models.DateField(db_column='BIRTH', blank=True, null=True)
    phone = models.CharField(db_column='PHONE', max_length=11, blank=True, null=True)
    gender = models.CharField(db_column='GENDER', max_length=1, blank=True, null=True, choices=Gender.choices)
    role = models.CharField(db_column='ROLE', max_length=1, choices=UserType.choices)

    email = None
    EMAIL_FIELD = None
    REQUIRED_FIELDS = []
    first_name = None
    last_name = None
    username = None
    date_joined = None

    USERNAME_FIELD = 'name'

    class Meta:
        managed = True
        db_table = 'USER'

    @property
    def is_evaluator(self) -> bool:
        return self.role == self.UserType.EVALUATOR

    @property
    def is_admin(self) -> bool:
        return self.role == self.UserType.ADMIN

    @property
    def is_submitter(self) -> bool:
        return self.role == self.UserType.SUBMITTER

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.name

    def get_short_name(self):
        """Return the short name for the user."""
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role == self.UserType.ADMIN:
            UserAdmin.objects.get_or_create(user=self)
        if self.role == self.UserType.EVALUATOR:
            UserEvaluator.objects.get_or_create(user=self)
        if self.role == self.UserType.SUBMITTER:
            UserSubmitter.objects.get_or_create(user=self)

    def __str__(self):
        return self.name


class UserAdmin(models.Model):
    user = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'USER_ADMIN'

    def __str__(self):
        return self.user.name


class UserEvaluator(models.Model):
    user = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'USER_EVALUATOR'

    def __str__(self):
        return self.user.name


class UserSubmitter(models.Model):
    user = models.OneToOneField(User, models.CASCADE, db_column='ID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'USER_SUBMITTER'

    def __str__(self):
        return self.user.name


class MealReview(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='meal_reviews')
    name = models.TextField(verbose_name='음식 메뉴 이름', blank=True, null=True)
    price = models.IntegerField(verbose_name='가격', blank=True, null=True)
    portion = models.TextField(verbose_name='양', blank=True, null=True)
    taste = models.IntegerField(verbose_name='맛', blank=True, null=True)

    class Meta:
        db_table = 'MEAL_REVIEW'


class SideDishesReview(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='side_dishes_reviews')
    name = models.TextField(verbose_name='사이드 메뉴 이름', blank=True, null=True)
    price = models.IntegerField(verbose_name='가격', blank=True, null=True)
    portion = models.TextField(verbose_name='양', blank=True, null=True)
    taste = models.IntegerField(verbose_name='맛', blank=True, null=True)

    class Meta:
        db_table = 'SIDE_DISHES_REVIEW'


class StyleReview(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='style_reviews')
    name = models.TextField(verbose_name='식당 이름', blank=True, null=True)
    atmosphere = models.IntegerField(verbose_name='분위기', blank=True, null=True)
    sanitation = models.IntegerField(verbose_name='청결', blank=True, null=True)
    toilet = models.IntegerField(verbose_name='화장실 여부', blank=True, null=True)
    parking = models.IntegerField(verbose_name='주차장 여부', blank=True, null=True)

    class Meta:
        db_table = 'STYLE_REVIEW'
