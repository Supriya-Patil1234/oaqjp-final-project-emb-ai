from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from .models import Course, Lesson, Question, Choice, Submission, Enrollment

def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            choice = Choice.objects.get(pk=int(value))
            submission.choices.add(choice)
            
    submission.save()
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = list(submission.choices.values_list('id', flat=True))
    
    total_score = 0
    grade = 0
    
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_score += question.grade
            if question.is_get_score(selected_ids):
                grade += question.grade

    grade_percent = int((grade / total_score) * 100) if total_score > 0 else 0

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'grade': grade_percent,
        'selected_ids': selected_ids,
        'user': request.user
    })

def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password =  request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:course_details', course_id=1)
    return redirect('onlinecourse:course_details', course_id=1)

def logout_request(request):
    logout(request)
    return redirect('onlinecourse:course_details', course_id=1)