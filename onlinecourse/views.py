from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import (
    Course, Enrollment,
    Question, Choice, Submission
)

from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.all()


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return redirect('onlinecourse:course_details', pk=course.id)


def extract_answers(request):
    submitted = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted.append(int(request.POST[key]))
    return submitted


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=request.user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)

    choices = extract_answers(request)
    for cid in choices:
        submission.choices.add(Choice.objects.get(id=cid))

    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result',
                args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    selected_ids = list(submission.choices.values_list('id', flat=True))

    questions = Question.objects.filter(lesson__course=course)

    total_score = 0
    total_grade = 0

    for q in questions:
        total_grade += q.grade
        if q.is_get_score(selected_ids):
            total_score += q.grade

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'grade': total_score,
        'total_grade': total_grade,
        'questions': questions,
    })
