from datetime import datetime, time
from itertools import islice
import json
from math import ceil
from collections import defaultdict
import os
from django.shortcuts import redirect, render
from django.core.paginator import Paginator

from online_exam.decorators import authorized_user
from exam.models import Exam
from online_exam.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL
from question.models import Question
from user.models import Lecturer, Student, Course
from .models import CompletedExam, BrowserActivity, ScreenCapture
from notification.views import send_notification
from online_exam.views import encrypt_id, decrypt_id


# Create your views here.
@authorized_user(authorized_groups=['lecturer'])
def lecture_view_completed_exam(request):    
    lecturer = Lecturer.objects.get(user_id = request.user.id)
    exam_list = Exam.objects.filter(lecturer__id = lecturer.id).order_by('question_bank__course__id')
    completed_exams = ""
    years_list = []
    exist_graded_exam = False
    
    exam_dict = defaultdict(list)
    
    for exam in exam_list:
        exam.id = encrypt_id(exam.id)

    for exam in exam_list:
        course = Course.objects.get(id = exam.question_bank.course.id)
        course_title = course.code + " " + course.name 
        exam_dict[course_title].append(exam)
        
    exam_dict = dict(exam_dict)
    
    #Get completed exams
    exam_id = request.GET.get('exam_id')
    if exam_id:
        exam_id = decrypt_id(exam_id)
        selected_exam = Exam.objects.get(id=exam_id) 
        selected_exam.id = encrypt_id(selected_exam.id)        
    else:
        selected_exam = ''
        
    if exam_id:
        completed_exams = CompletedExam.objects.filter(exam_id=exam_id).order_by('graded')
        if completed_exams.exists():
            exist_graded_exam = completed_exams.filter(graded=1).exists()
            years = {str(exam.completed_at.year) for exam in completed_exams}
            years_list = sorted(years)
    
    #Get oldest and latest Completed Exam Date of selected Exam
    if completed_exams:
        oldest_exam = completed_exams.order_by('completed_at').first()
        latest_exam = completed_exams.order_by('-completed_at').first()
        
    else:
        oldest_exam = None
        latest_exam = None    
    
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')    
    # Apply search filter if there is a search query
    if search_query:
        completed_exams = completed_exams.filter(
            student__user__first_name__icontains=search_query
        ) | completed_exams.filter(
            student__user__last_name__icontains=search_query
        ) | completed_exams.filter(
            student__user__first_name__icontains=search_query.split(' ')[0],
            student__user__last_name__icontains=search_query.split(' ')[-1],
        )
    # Apply question type filter if a filter is selected
    if filter_type:
        completed_exams = completed_exams.filter(completed_at__year=filter_type)    
        
    paginator = Paginator(completed_exams, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    completed_exams = paginator.get_page(page_number)  # Get current page
    
    for completed_exam in completed_exams:
        completed_exam.id = encrypt_id(completed_exam.id)

    context = {
        'exam_dict' : exam_dict,
        'search_query' : search_query,
        'filter_type' : filter_type,
        'completed_exams' : completed_exams,
        'years_list' : years_list,
        'selected_exam': selected_exam,
        'oldest_exam': oldest_exam,
        'latest_exam': latest_exam,
        'exist_graded_exam': exist_graded_exam,
    }
    return render(request, 'completed_exam/lecture_view_completed_exam.html', context)

@authorized_user(authorized_groups=['lecturer'])
def grade_completed_exam(request, encrypted_id):
    id = decrypt_id(encrypted_id)
     
    completed_exam = CompletedExam.objects.get(id=id)
    mcq_answer = completed_exam.answers["mcq"]
    tf_answer = completed_exam.answers["tf"]
    essay_answer = completed_exam.answers["essay"]
    essay_mark = completed_exam.essay_mark
    mcq_question = []
    tf_question = []
    essay_question = []
    
    if request.POST:
        action = request.POST.get('submit')
             
        if essay_mark:
            if completed_exam.graded:
                total = sum(int(value) for value in essay_mark.values())
                completed_exam.total_mark -= total
            for essay in essay_mark:
                mark = request.POST.get(essay)
                essay_mark[essay] = mark

            #New mark
            total = sum(int(value) for value in essay_mark.values())
            completed_exam.total_mark += total  
              
            completed_exam.essay_mark = essay_mark        
        
        if action == 'fail_exam':
            completed_exam.exam_passed = False
        else:
            completed_exam.exam_passed = True  
        
        completed_exam.comment = request.POST.get("comment")
        completed_exam.graded = True
        #Save graded exam
        completed_exam.save()
        
        message = "Dear " + completed_exam.student.user.first_name + " " + completed_exam.student.user.last_name + "\n\nWe are pleased to inform you that your exam for " + completed_exam.exam.title + " has been graded. You can now view your results by logging into your student portal.\n\n" + "If you have any questions or concerns about your grades, feel free to reach out to your lecturer.\n\n" + "Access your results by navigating to the Completed Exam section."
      
        send_notification(completed_exam.student.user, 
                          completed_exam.exam.title + " Results Are Now Available", 
                          message, 
                          False, 1)
        
        return redirect('lecture_view_completed_exam')   
    
    for question in mcq_answer:
        curr_question = Question.objects.get(id=int(question))
        correct_ans = False
        if curr_question.correct_answers == mcq_answer[question]:
            correct_ans = True
        mcq_question.append([question, curr_question.question, mcq_answer[question], correct_ans, curr_question.marks, curr_question.options, curr_question.correct_answers])
        
    for question in tf_answer:
        curr_question = Question.objects.get(id=int(question))
        correct_ans = False
        if curr_question.correct_answers[0] == tf_answer[question]:
            correct_ans = True
        tf_question.append([question, curr_question.question, tf_answer[question], correct_ans, curr_question.marks, curr_question.correct_answers])
    
    for question in essay_answer:
        curr_question = Question.objects.get(id=int(question))
        essay_question.append([question, curr_question.question, essay_answer[question], essay_mark[question],  curr_question.marks]) #[id, question, answer, graded_mark, total_mark]

    if mcq_question:
        first_ques_type = "mcq"
    elif tf_question:
        first_ques_type = "tf"
    elif essay_question:
        first_ques_type = "essay"
    else:
        first_ques_type = "" 
    
    context = {
        'completed_exam' : completed_exam,
        'mcq_question' : mcq_question,
        'tf_question' : tf_question,
        'essay_question' : essay_question,
        'first_ques_type' : first_ques_type,
    }
    return render(request, 'completed_exam/grade_completed_exam.html', context)

@authorized_user(authorized_groups=['lecturer'])
def view_exam_report(request, encrypted_id):
    id= decrypt_id(encrypted_id)
    
    if request.POST:
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d') 
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
        end_date = datetime.combine(end_date, time(23, 59, 59))
               
        completed_exams = CompletedExam.objects.filter(exam_id=id, completed_at__gte=start_date, completed_at__lte=end_date, graded=True).order_by('student__user__first_name')
      
        
        student_grp40 = None
        if len(completed_exams) > 40:
            student_grp40 = [list(islice(completed_exams, i, i + 40)) for i in range(0, len(completed_exams), 40)]
           
        pages = ceil(len(completed_exams) / 40)
        
        #Marks
        total_marks = completed_exams.values_list('total_mark', flat=True)
        average_marks = f"{sum(total_marks) / len(total_marks):.2f}"
        
        highest_mark = max(total_marks)
        lowest_mark = min(total_marks)
    
        
        mark_report = {'average_marks' : average_marks, 'highest_mark' : highest_mark, 'lowest_mark' : lowest_mark}
        
        #Time taken
        time_taken = completed_exams.values_list('time_taken', flat=True)
        average_time = sum(time_taken) / len(time_taken)
        
        #Question
        answers_list = [exam.answers for exam in completed_exams]
        mcq = []
        tf = []
        mcq_corrects = {}
        tf_corrects = {}
        essay_marks = {}
        average_essay_mark = None
        
        for dict in answers_list:
            for key in dict['mcq']:
                if key not in mcq:
                    mcq.append(key)
                    mcq_corrects[key] = 0
            for key in dict['tf']:
                if key not in tf:
                    tf.append(key)
                    tf_corrects[key] = 0          
                    
        print(mcq_corrects)
        print(tf_corrects)
        
        
        for completed_exam in completed_exams: #Calculate total amounts of corrects
            if mcq_corrects != {}: #Run when not empty        
                mcq_answer = completed_exam.answers["mcq"]
                
                for question in mcq_answer:
                    curr_question = Question.objects.get(id=int(question))
                    if curr_question.correct_answers == mcq_answer[question]:
                        mcq_corrects[question] += 1
            
            
            if tf_corrects != {}: #Run when not empty
                tf_answer = completed_exam.answers["tf"]
                
                for question in tf_answer:
                    curr_question = Question.objects.get(id=int(question))
                    if curr_question.correct_answers[0] == tf_answer[question]:
                        tf_corrects[question] += 1
                
        
        essay_marks = completed_exams.values_list('essay_mark', flat=True)
        grouped_values = defaultdict(list)
        if essay_marks != {} and essay_marks.filter(essay_mark__isnull=False).exists(): #Run when not empty    
            for essay in essay_marks:
                if essay:
                    for key, value in essay.items():
                        grouped_values[key].append(int(value))
            
            average_essay_mark = {key: sum(values) / len(values) for key, values in grouped_values.items()}
        
        #Diagram
        #MCQ
        if mcq_corrects != {}:
            keys = list(map(int, mcq_corrects.keys()))
            values = list(mcq_corrects.values())
            
            question_list = Question.objects.filter(id__in=keys).values('question', 'marks')
            mcq_corrects = {'keys' : question_list, 'values' : values}
        
        #TF
        if tf_corrects != {}:
            keys = list(map(int, tf_corrects.keys()))
            values = list(tf_corrects.values())
            
            question_list = Question.objects.filter(id__in=keys).values('question', 'marks')
            tf_corrects = {'keys' : question_list, 'values' : values}
        
        #Essay
        if essay_marks != {} and essay_marks.filter(essay_mark__isnull=False).exists():
            keys = list(map(int, average_essay_mark.keys()))
            values = list(average_essay_mark.values())
            
            question_list = Question.objects.filter(id__in=keys).values('question', 'marks')
            average_essay_mark = {'keys' : question_list, 'values' : values}

        context = {
            'start_date' : start_date,
            'end_date' : end_date,
            'full_mark' : completed_exams[0].full_mark,
            'pages' : pages,
            'completed_exams' : completed_exams,
            'mark_report' : mark_report,
            'average_time' : average_time,
            'mcq_corrects' : mcq_corrects,
            'tf_corrects' : tf_corrects,
            'average_essay_mark' : average_essay_mark,
            'student_grp40' : student_grp40,
        }         
    
    return render(request, 'completed_exam/view_exam_report.html', context)

@authorized_user(authorized_groups=['student'])
def student_view_completed_exam(request):
    student = Student.objects.get(user_id = request.user.id)
    completed_exams = CompletedExam.objects.filter(student_id = student.id, graded=True).order_by('graded', 'exam__title', '-completed_at')
    course_list = Course.objects.filter(id__in = student.registered_courses)
    
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')    
    # Apply search filter if there is a search query
    if search_query:
        completed_exams = completed_exams.filter(
            exam__title__icontains=search_query
        )
    # Apply question type filter if a filter is selected
    if filter_type:
        completed_exams = completed_exams.filter(exam__question_bank__course__id=filter_type)  
    
    paginator = Paginator(completed_exams, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    completed_exams = paginator.get_page(page_number)  # Get current page
    
    for completed_exam in completed_exams:
        completed_exam.id = encrypt_id(completed_exam.id)
    
    context = {
        'completed_exams' : completed_exams,
        'course_list' : course_list,
        'search_query' : search_query,
        'filter_type' : filter_type,
    }
    return render(request, 'completed_exam/student_view_completed_exam.html', context)

@authorized_user(authorized_groups=['student'])
def student_view_completed_exam_detail(request, encrypted_id):
    id = decrypt_id(encrypted_id)
    
    completed_exam = CompletedExam.objects.get(id=id)
    mcq_answer = completed_exam.answers["mcq"]
    tf_answer = completed_exam.answers["tf"]
    essay_answer = completed_exam.answers["essay"]
    essay_mark = completed_exam.essay_mark
    mcq_question = []
    tf_question = []
    essay_question = []
    
    for question in mcq_answer:
        curr_question = Question.objects.get(id=int(question))
        correct_ans = False
        if curr_question.correct_answers == mcq_answer[question]:
            correct_ans = True
        mcq_question.append([question, curr_question.question, mcq_answer[question], correct_ans, curr_question.marks, curr_question.options, curr_question.correct_answers, curr_question.explanation])
        #[id, question, answer, answered correct or not, mark, options, correct answer, explanation]
            
    for question in tf_answer:
        curr_question = Question.objects.get(id=int(question))
        correct_ans = False
        if curr_question.correct_answers[0] == tf_answer[question]:
            correct_ans = True
        tf_question.append([question, curr_question.question, tf_answer[question], correct_ans, curr_question.marks, curr_question.correct_answers, curr_question.explanation])
        #[id, question, answer, answered correct or not, mark, correct answer, explanation]
    
    print(tf_question)
    
    for question in essay_answer:
        curr_question = Question.objects.get(id=int(question))
        essay_question.append([question, curr_question.question, essay_answer[question], essay_mark[question],  curr_question.marks, curr_question.explanation]) 
        #[id, question, answer, graded_mark, total_mark, explanation]

    if mcq_question:
        first_ques_type = "mcq"
    elif tf_question:
        first_ques_type = "tf"
    elif essay_question:
        first_ques_type = "essay"
    else:
        first_ques_type = "" 
    
    
    context = {
        'completed_exam' : completed_exam,
        'mcq_question' : mcq_question,
        'tf_question' : tf_question,
        'essay_question' : essay_question,
        'first_ques_type' : first_ques_type,
    }
    return render(request, 'completed_exam/student_view_completed_exam_detail.html', context)

@authorized_user(authorized_groups=['lecturer'])
def view_exam_log(request, encrypted_id):
    id = decrypt_id(encrypted_id)
    completed_exam = CompletedExam.objects.get(id=id)
    browser_activity = BrowserActivity.objects.filter(completed_exam_id = completed_exam.id).first()
    screen_capture = ScreenCapture.objects.filter(completed_exam_id = completed_exam.id).first()
    curr_view = None
    log_page_number = 0
    screen_page_number = 0
    video_num = 0
    curr_video_url = None
    
    if request.GET:
        curr_view=request.GET.get('view')        
    
    #Browser Activity
    if browser_activity:
        browser_activity.activity_log = sorted(browser_activity.activity_log, key=lambda x: x['status'], reverse=True)
        
        log_paginator = Paginator(browser_activity.activity_log, 10)  # Show 10 log per page
        log_page_number = request.GET.get('log-page', 1)
        browser_activity.activity_log = log_paginator.get_page(log_page_number)  # Get current page
    
    #Screen Capture
    if screen_capture:
        #Screen Capture Video
        video_directory = str(screen_capture.location)
        absolute_path = os.path.abspath(video_directory)
        
        # Get all .webm files in the directory
        videos = [
            f for f in os.listdir(absolute_path) 
            if os.path.isfile(os.path.join(absolute_path, f)) and f.endswith('.webm')
        ]

        # Generate full paths for video URLs if serving through static/media
        video_urls = [os.path.join(video_directory, video).replace(str(BASE_DIR), "") for video in videos]
        
        print(video_urls)
        
        screen_paginator = Paginator(video_urls, 1)  # Show 1 video per page
        screen_page_number = request.GET.get('screen-page', 1)
        #Get chosen video url
        if screen_page_number:
            video_num = int(screen_page_number) - 1
            curr_video_url = video_urls[video_num]
            
            
        video_urls = screen_paginator.get_page(screen_page_number)  # Get current page
            
    else:
        video_urls = None
    
    context = {
        'completed_exam' : completed_exam,
        'browser_activity' : browser_activity,
        'video_urls' : video_urls,
        'curr_view' : curr_view,
        'curr_video_url' : curr_video_url,
        'log_page_number' : log_page_number,
        'screen_page_number' : screen_page_number,
    }
    return render(request, 'completed_exam/view_exam_log.html', context)