from django import forms
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect

from app.models import MealReview, SideDishesReview, StyleReview, Submits, UserSubmitter, RawFileMetadata, \
    RawDataTemplate, RequestsNew, TaskMetadata, ParsingDataSeq


class UploadFileForm(forms.Form):
    task = forms.CharField()
    file = forms.FileField()


@transaction.atomic
def upload(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'app/submit/upload_form.html', {'title': '업로드'})
        try:
            result = import_data(request, form)
            messages.success(request, f'{result}개가 업데이트 되었습니다')
        except IntegrityError:
            messages.error(request, '이미 제출 되었습니다.')
            return render(request, 'app/submit/upload_form.html', {'title': '업로드'})

    return render(request, 'app/submit/upload_form.html', {'form': form, 'title': '업로드'})


def import_data(request, form):
    task = form.cleaned_data.get('task')
    sheet = request.FILES['file']
    array = sheet.get_sheet().array
    header = {idx: field for idx, field in enumerate(array[0])}

    if task == 'MealReview':
        model_class = MealReview
    elif task == 'SideDishesReview':
        model_class = SideDishesReview
    elif task == 'StyleReview':
        model_class = StyleReview

    instances = []
    for row in array[1:]:
        instance = create_model_instance(row, header, model_class)
        if instance is not None:
            instance.__setattr__('user', request.user)
            instances.append(instance)

    if instances:
        model_class.objects.bulk_create(instances)
        create_related_instances(model_class, request, array[1:])
    return len(instances)


def create_related_instances(model_class, request, rows):
    table_name = model_class._meta.db_table
    raw_file_metadata = get_object_or_404(RawFileMetadata, table_name=table_name)
    task_metadata = get_object_or_404(TaskMetadata, table_name=table_name)
    user_submitter = get_object_or_404(UserSubmitter, user=request.user)

    Submits.objects.create(uid=user_submitter, table_name=raw_file_metadata)
    text = RawDataTemplate.convert_csv_to_text(request.FILES['file'])
    rdt = RawDataTemplate.objects.create(raw_data=text)
    parsing_data_seq = ParsingDataSeq.objects.create(total_tuple_count=len(rows),
                                                     duplicated_tuple_count=len(rows) - len(remove_duplicates(rows)))
    RequestsNew.objects.create(table_name=task_metadata, rdt=rdt, status=RequestsNew.Status.NON_PASS,
                               uid=user_submitter, pds=parsing_data_seq)


def create_model_instance(row, header, model_class):
    data_dict = {header[idx]: data for idx, data in enumerate(row)}
    if len(data_dict.values()) == len(header):
        return model_class(**data_dict)
    return None


def remove_duplicates(rows):
    return set(tuple(row) for row in rows)

