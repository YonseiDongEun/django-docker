from django.contrib import admin

from app.models import SideDishesReview, MealReview, StyleReview, User, TaskMetadata, RawFileMetadata


@admin.register(MealReview)
class MealReviewAdmin(admin.ModelAdmin):
    pass


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
