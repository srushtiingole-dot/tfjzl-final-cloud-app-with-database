from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Submission, Question

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if request.method == "POST":
        selected_choices = request.POST.getlist("choice")
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_choices)
        submission.save()

        return redirect("onlinecourse:show_exam_result", course.id, submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    questions = Question.objects.filter(course=course)
    total_score = 0

    for question in questions:
        total_score += question.grade if question.is_get_score(submission) else 0

    context = {
        "course": course,
        "submission": submission,
        "questions": questions,
        "total_score": total_score,
    }

    return render(request, "onlinecourse/exam_result.html", context)


