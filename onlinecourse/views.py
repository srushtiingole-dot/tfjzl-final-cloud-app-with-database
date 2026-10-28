from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Course, Enrollment, Question, Choice, Submission

# Course list view
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-pub_date')[:10]


# Course detail view showing course details and exam questions
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        if not user.is_authenticated:
            return redirect('onlinecourse:login')
        
        # Create enrollment if it doesn't exist
        Enrollment.objects.get_or_create(user=user, course=course)
        return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if not user.is_authenticated:
        return redirect('onlinecourse:login')

    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    if request.method == 'POST':
        # Get selected choices from POST request
        selected_choice_ids = request.POST.getlist('choice')
        
        # Create submission and attach choices
        submission = Submission.objects.create(enrollment=enrollment)
        if selected_choice_ids:
            submission.choices.set(selected_choice_ids)
        submission.save()

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

    return redirect('onlinecourse:course_details', course_id=course.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # Extract selected choice IDs as a list of integers
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    questions = Question.objects.filter(course=course)
    
    total_score = 0
    total_possible = 0

    for question in questions:
        total_possible += question.grade
        # Pass list of choice IDs to is_get_score
        if question.is_get_score(selected_ids):
            total_score += question.grade

    context = {
        'course': course,
        'submission': submission,
        'selected_ids': selected_ids,
        'total_score': total_score,
        'total_possible': total_possible,
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
