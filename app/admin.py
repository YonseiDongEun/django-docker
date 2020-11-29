import csv

from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django_object_actions import DjangoObjectActions

from app.models import SideDishesReview, MealReview, StyleReview, User, TaskMetadata, RawFileMetadata, Evaluates, \
    ParsingDataSeq, IsAssignedTo


@admin.register(MealReview)
class MealReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'price', 'portion', 'taste']


@admin.register(SideDishesReview)
class SideDishesReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(StyleReview)
class StyleReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskMetadata)
class TaskMetadataAdmin(admin.ModelAdmin):
    list_display = ['table_name', 'display_name', 'description', 'min_upload_cycle', 'activated', 'pass_criterion']


@admin.register(RawFileMetadata)
class RawFileMetadataAdmin(admin.ModelAdmin):
    list_display = ['table_name', 'display_name', 'mapping_sql_query', 'task_name']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Evaluates)
class EvaluatesAdmin(admin.ModelAdmin):
    list_display = ['uid', 'pds_id', 'p_np', 'rating']


@admin.register(IsAssignedTo)
class IsAssignedToAdmin(admin.ModelAdmin):
    list_display = ['uid', 'pds', 'due']


class EvaluatesInline(admin.TabularInline):
    model = Evaluates
    extra = 1


@admin.register(ParsingDataSeq)
class ParsingDataSeqAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['pds_id', 'table_name', 'total_tuple_count', 'duplicated_tuple_count', 'rating']
    inlines = [EvaluatesInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        try:
            return queryset.filter(is_assigned_tos__uid=request.user.userevaluator)
        except ObjectDoesNotExist:
            return queryset.none()

    def download_excel(self, request, obj):
        FILE_NAME = 'parsing_request_seq.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{FILE_NAME}"'

        writer = csv.writer(response)
        try:
            lines = obj.requests_new.rdt.raw_data.split('\n')
        except TypeError:
            lines = obj.requests_new.rdt.raw_data.decode().split('\n')
        for row in lines:
            writer.writerow(row.split(','))

        return response

    download_excel.label = "다운로드"
    download_excel.short_description = "이 제출을 다운로드합니다"

    change_actions = ('download_excel',)


