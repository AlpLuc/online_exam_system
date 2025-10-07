import json
import os
import random
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.utils.timezone import now, localtime

from online_exam.decorators import authorized_user
from online_exam import settings 
from question.models import Question, QuestionBank
from user.models import Course, Lecturer, Student
from .models import Exam, TrackingSetting
from completed_exam.models import CompletedExam, ScreenCapture, BrowserActivity
from .forms import ExamForm, TrackingSettingForm
from notification.views import send_notification
from screeninfo import get_monitors
from online_exam.views import encrypt_id, decrypt_id

# Create your views here.
@authorized_user(authorized_groups=['lecturer'])
def exam_list(request):
    lecturer = Lecturer.objects.get(user=request.user)    
    course_list = Course.objects.filter(lecturer=lecturer) 
    exam_list = Exam.objects.filter(lecturer=request.user.lecturer).order_by('-exam_status', 'start_date_time')
    
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')    
    # Apply search filter if there is a search query
    if search_query:
        exam_list = exam_list.filter(title__icontains=search_query)

    # Apply question type filter if a filter is selected
    if filter_type:
        exam_list = exam_list.filter(question_bank__course=filter_type)
        
    paginator = Paginator(exam_list, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    exam_list = paginator.get_page(page_number)  # Get current page
    
    for exam in exam_list:
        exam.id = encrypt_id(exam.id)
    
    context = {
        'exam_list':exam_list,
        'course_list':course_list,
        'search_query': search_query,
        'filter_type': filter_type,
        'now': now,
    }
    
    return render(request, 'exam/exam_list.html', context)

@authorized_user(authorized_groups=['lecturer'])
def change_exam_status(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    exam  = Exam.objects.get(pk=pk)
    exam.exam_status = not exam.exam_status  # Toggle the status
    exam.save()

    return redirect('exam_list')

@authorized_user(authorized_groups=['lecturer'])
def get_questions(request, question_bank_id):
    questions = Question.objects.filter(question_bank_id=question_bank_id).values('id', 'question', 'question_type', 'marks').order_by('quesion_type')
    question_data = list(questions)
    
    return JsonResponse(question_data, safe=False)

@authorized_user(authorized_groups=['lecturer'])
def create_exam(request):
    question_list = []
    selected_question_bank = None
    time_now = now()
                
    if request.POST:
        post_data = request.POST.copy()
        
        if post_data.get('question_bank'):
            selected_question_bank = int(post_data.get('question_bank'))
           
        
        if selected_question_bank:
            # Fetch questions for the selected question bank
            question_list = Question.objects.filter(question_bank_id=selected_question_bank).values('id', 'question', 'question_type', 'marks').order_by('-question_type')
            lecturer = Lecturer.objects.get(user=request.user)
            filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
                    
            exam_form = ExamForm()
            exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
            tracking_form = TrackingSettingForm()
            question_list = list(question_list)  # Convert queryset to a list
            cohorts = Student.objects.values_list('cohort', flat=True).distinct()
        else:
            lecturer = Lecturer.objects.get(user=request.user)
            filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
                    
            exam_form = ExamForm()
            exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
            tracking_form = TrackingSettingForm()
            cohorts = Student.objects.values_list('cohort', flat=True).distinct()
            

        #If submit button is clicked
        if 'submitBtn' in request.POST:
            question_list = request.POST.getlist('selected_questions')
            total_question = len(question_list)
            
            post_data['total_question'] = total_question

            exam_form = ExamForm(post_data)
            tracking_form = TrackingSettingForm(request.POST)
            if exam_form.is_valid() and tracking_form.is_valid():
                print("Form Valid")            
                exam = exam_form.save(commit=False)
                exam.lecturer = request.user.lecturer  
                exam.question_list = question_list
                exam.cohort = request.POST.get('cohort')
                exam.save()
                
                tracking_setting = tracking_form.save(commit=False)
                tracking_setting.exam = exam
                tracking_setting.save()
                return redirect('exam_list')
            else:
                print("Form Invalid")
                messages.error(request, exam_form.errors)
                messages.error(request, tracking_form.errors)
                print(exam_form.errors)
                print(tracking_form.errors)
            
    else:
        #customized question bank query    
        lecturer = Lecturer.objects.get(user=request.user)
        filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
                
        exam_form = ExamForm()
        exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
        tracking_form = TrackingSettingForm()
        cohorts = Student.objects.values_list('cohort', flat=True).distinct()
    
    context = {
        'exam_form':exam_form, 
        'tracking_form':tracking_form, 
        'question_bank':filtered_question_banks,
        'selected_question_bank': selected_question_bank,
        'question_list': question_list,
        'cohorts' : cohorts,
        'time_now' : time_now,
    }
    return render(request, 'exam/create_exam.html', context)

@authorized_user(authorized_groups=['lecturer'])
def view_exam(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    exam = Exam.objects.get(pk=pk)
    tracking_setting = TrackingSetting.objects.get(exam_id=exam.id)
    question_list = Question.objects.filter(id__in=exam.question_list).order_by('-question_type')
    
    if CompletedExam.objects.filter(exam_id=exam.id):
        has_completed_exam = True
    else:
        has_completed_exam = False    
    
    exam.id = encrypt_id(exam.id)
    
    context = {
        'exam':exam, 
        'tracking_setting' : tracking_setting, 
        'question_list' : question_list,
        'has_completed_exam' : has_completed_exam,
    }
    
    return render(request, 'exam/view_exam.html', context)

@authorized_user(authorized_groups=['lecturer'])
def edit_exam(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    exam = Exam.objects.get(pk=pk)
    track_setting = TrackingSetting.objects.get(exam_id=exam.id)
    question_list = Question.objects.filter(question_bank_id=exam.question_bank.id).order_by('-question_type')
    selected_question_bank = exam.question_bank.id
    
    if request.POST:
        post_data = request.POST.copy()  
        
        if post_data.get('question_bank'):
            selected_question_bank = int(post_data.get('question_bank'))
        
        if selected_question_bank:
            # Fetch questions for the selected question bank
            question_list = Question.objects.filter(question_bank_id=selected_question_bank).values('id', 'question', 'question_type', 'marks').order_by('-question_type')
            lecturer = Lecturer.objects.get(user=request.user)  
            filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
            
            exam_form = ExamForm(instance=exam)
            exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
            tracking_form = TrackingSettingForm(instance=track_setting)
            cohorts = Student.objects.values_list('cohort', flat=True).distinct()
        else:
            lecturer = Lecturer.objects.get(user=request.user)
            filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
                    
            exam_form = ExamForm()
            exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
            tracking_form = TrackingSettingForm()
            cohorts = Student.objects.values_list('cohort', flat=True).distinct()
            
        if 'submitBtn' in request.POST:
            question_list = request.POST.getlist('selected_questions')
            total_question = len(question_list)
            
            post_data['total_question'] = total_question

            exam_form = ExamForm(post_data, instance=exam)
            tracking_form = TrackingSettingForm(request.POST, instance=track_setting)
            if exam_form.is_valid() and tracking_form.is_valid():
                print("Form Valid")            
                exam = exam_form.save(commit=False)                
                exam.lecturer = request.user.lecturer  
                exam.question_list = question_list
                exam.cohort = request.POST.get('cohort')
                exam.save()
                
                tracking_setting = tracking_form.save(commit=False)
                tracking_setting.exam = exam
                tracking_setting.save()            
                return redirect('exam_list')
            else:
                print("Form Invalid")
                messages.error(request, exam_form.errors)
                messages.error(request, tracking_form.errors)
                print(exam_form.errors)
                print(tracking_form.errors)
    else:
        lecturer = Lecturer.objects.get(user=request.user)  
        filtered_question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
        
        exam_form = ExamForm(instance=exam)
        exam_form.fields['question_bank'].queryset = filtered_question_banks #change query set
        tracking_form = TrackingSettingForm(instance=track_setting)
        cohorts = Student.objects.values_list('cohort', flat=True).distinct()
        
    context = {
        'exam_form':exam_form, 
        'tracking_form':tracking_form,
        'question_list':question_list,
        'selected_question_bank':selected_question_bank, 
        'exam':exam,
        'track_setting':track_setting,
        'cohorts' : cohorts,
    }
        
    return render(request, 'exam/edit_exam.html', context)

@authorized_user(authorized_groups=['lecturer'])
def delete_exam(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    exam  = Exam.objects.get(pk=pk)
    track_setting = TrackingSetting.objects.get(exam_id=exam.id)
    exam.delete()
    track_setting.delete()
    
    return redirect('exam_list')

@authorized_user(authorized_groups=['student'])
def student_view_exam(request):
    student = Student.objects.get(user_id = request.user.id)
    
    completed_attempts = CompletedExam.objects.filter(
        exam_id=OuterRef('pk'),  # Reference to the current exam in the outer query
        student_id=student.id  # Use the current student ID
    ).values('exam_id').annotate(attempt_count=Count('id')).values('attempt_count')

    current_time = now()
    if student.registered_courses is not None:
        started_exams = Exam.objects.annotate(
            attempt_count=Coalesce(Subquery(completed_attempts), Value(0))    
        ).filter(
            question_bank__course__id__in=student.registered_courses,
            start_date_time__lte=current_time,
            end_date_time__gte=current_time,
            cohort = student.cohort
        ).exclude(
            attempt_count__gte=F('total_attempt')    
        )        

        upcoming_exams = Exam.objects.filter(
            question_bank__course__id__in=student.registered_courses,
            start_date_time__gt=current_time,
            cohort = student.cohort
        )

        closed_exams = Exam.objects.annotate(
            attempt_count=Coalesce(Subquery(completed_attempts), Value(0))    
        ).filter(
            Q(question_bank__course__id__in=student.registered_courses,
            end_date_time__lt=current_time) |
            Q(attempt_count__gte=F('total_attempt')),
            cohort = student.cohort 
        )
        
        for exam in started_exams:
            exam.remaining_attempts = exam.total_attempt - exam.attempt_count
        for exam in closed_exams:
            exam.remaining_attempts = exam.total_attempt - exam.attempt_count

        for exam in started_exams:
            exam.id = encrypt_id(exam.id)
        
        exam_list_list = [started_exams, upcoming_exams, closed_exams]
    
    
    context = {
        'exam_list_list':exam_list_list,
        'now':now,
    }

    return render(request, 'exam/student_view_exam.html', context)

@authorized_user(authorized_groups=['student'])
def exam_agreement(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    
    exam = Exam.objects.get(pk=pk)
    tracking_setting = TrackingSetting.objects.get(exam_id=exam.id)
    session_exam_id = -1
    active_setting = []
    
    if 'tab_switch_counter' in request.session:
        del request.session['tab_switch_counter']
    
    # Atempting to initiate another exam while another is undergoing
    if 'exam_undergoing' in request.session:
        session_exam_id = request.session.get('exam_undergoing').get('exam_id')        
        if session_exam_id != exam.id:
            undergoing_exam_pk = session_exam_id
            undergoing_exam = Exam.objects.get(pk=undergoing_exam_pk)
            print("detected student attempting to take other exam")
            messages.warning(request, ("Finish " + undergoing_exam.title + " first before attempting another exam"))
            return redirect('student_view_exam') 
        elif session_exam_id == exam.id:
            exam.id = encrypt_id(exam.id)
            return redirect('examination', exam.id) 
        
    if exam.copy_paste_restrict:
        active_setting.append("Copy and Paste Restriction: Copying and pasting text are restricted during this exam.")
    if tracking_setting.capture_screen:
        active_setting.append("Screen Capture: Your screen activity will be monitored and recorded during the exam to detect unauthorized behavior.")
    if tracking_setting.browser_activity:
        active_setting.append("Browser Activity Monitoring: Your browser activity will be monitored to ensure compliance with exam rules.")
    if tracking_setting.tab_switch:
        active_setting.append("Tab Switching Restrictions: Monitoring tools will track tab switching. Exceeding " + str(tracking_setting.tab_switch_limit)+ " tab switches will result in exam termination. ")
    
    exam.id = encrypt_id(exam.id)
    
    context = {
        'exam' : exam,
        'session_exam_id': session_exam_id,
        'active_setting' : active_setting,
    }
    return render(request, 'exam/exam_agreement.html', context)

def save_flagged_questions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)                
            request.session['flagged_questions'] = data.get('flagged_question_dict', {})
            request.session.modified = True
            
            print(request.session['flagged_questions'])
            
            return JsonResponse({'status': 'Flagged questions saved successfully!'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def save_timer(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            remaining_time = data.get('remaining_time')

            if remaining_time is None:
                return JsonResponse({'status': 'error', 'message': 'remaining_time is required'}, status=400)

            # Convert remaining_time to integer (if needed)
            remaining_time = int(remaining_time)

            # Example: Save to session or database
            request.session['time_remaining'] = remaining_time
            request.session.modified = True
            
            return JsonResponse({'status': 'time save success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def session_save_selected_answer(request):
    if request.method == "POST":
        print("saving selected answer")
        try:
            data = json.loads(request.body)        
            request.session['answers'] = data
            print(data)
            
            # Ensure the sessions for MCQ and TF answers exist
            if 'mcq_selected_answers' not in request.session:
                request.session['mcq_selected_answers'] = {}
            if 'tf_selected_answers' not in request.session:
                request.session['tf_selected_answers'] = {}
            if 'essay_selected_answers' not in request.session:
                request.session['essay_selected_answers'] = {}
            
            # Update MCQ answers in session
            if 'mcq' in data:      
                request.session['mcq_selected_answers'] = data['mcq']
           
            # Update TF answers in session        
            if 'tf' in data:
                request.session['tf_selected_answers'] = data['tf']
             
            # Update Essay answers in session         
            if 'essay' in data:
                request.session['essay_selected_answers'] = data['essay']

            request.session.modified = True
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("Error saving selected answer from JSON" + str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def update_tab_switch_counter(request):
    print("Updating tab switch counter")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            tab_switch_counter = data.get("tab_switch_counter")
            request.session["tab_switch_counter"] = tab_switch_counter
            
            return JsonResponse({"message": "Tab switch counter updated successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

def upload_screen_chunk(request, exam_id):
    if request.method == "POST" and request.FILES.get("chunk"):
        if 'screen_recording' not in request.session:
            request.session['screen_recording'] = True
            request.session.modified = True
        
        print(request.session['screen_recording'])
        
        chunk = request.FILES["chunk"]        
        
        #naming folder with the following format {exam.id}_{student.id}_{attempt}_exam_screen_recordings for identification
        folder_name = f"{exam_id}_{request.user.id}_{request.session['attempt']}_exam_screen_recordings"

        print(folder_name)
        # Create directory for session chunks if not exists
        chunk_dir = os.path.join(settings.MEDIA_ROOT, "screen_recordings", folder_name)
        os.makedirs(chunk_dir, exist_ok=True)

        # Save the chunk
        chunk_file_path = os.path.join(chunk_dir, f"{len(os.listdir(chunk_dir))}.webm")
        with open(chunk_file_path, "wb") as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)

        return JsonResponse({"message": "Chunk uploaded successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)    

@authorized_user(authorized_groups=['student'])
def examination(request, encrypted_id):
    pk = decrypt_id(encrypted_id)  
    
    if request.POST:
        print("end exam")
        return redirect('end_exam')
    
    exam = Exam.objects.get(pk=pk)
    tracking_setting = TrackingSetting.objects.get(exam_id=exam.id)
    student = Student.objects.get(user=request.user)
    #Check if there is undergoing exam
    if 'exam_undergoing' not in request.session: # Initializing exam if no undergoing exam
        request.session['exam_undergoing'] = {'exam_id': exam.id }
        request.session['tab_switch_counter'] = tracking_setting.tab_switch_limit
        request.session['attempt'] = CompletedExam.objects.filter(exam_id=exam.id, student_id=student.id).count() + 1
        
        #clear browser activity log to ensure proper logging
        if 'browser_activity_log' in request.session:
            del request.session['browser_activity_log']
        
        # Initialize timer if not already in session
        if 'time_remaining' not in request.session:
            request.session['time_remaining'] = exam.duration * 60  # Convert minutes to seconds
            request.session['last_updated'] = now().timestamp()  # Save current time in seconds
            request.session.modified = True
        
        # Initialize flagged question list if not already in session
        if 'flagged_questions' not in request.session:
            request.session['flagged_questions'] = {}   
                    
        # Setting up questions
        #Multiple Choice Question
        if 'mcq_question_list' not in request.session:      
            mcq_question_list = None
            if exam.random_order:
                mcq_question_list = Question.objects.filter(id__in=exam.question_list, question_type='mcq')
                randomized_questions = []
                for question in mcq_question_list:
                    options = question.options
                    print(options)
                    if options:
                        randomized_options = list(options.items())
                        random.shuffle(randomized_options)
                        randomized_questions.append({
                            'id': question.id,
                            'question': question.question,
                            'options': randomized_options
                        })
                random.shuffle(randomized_questions)
                mcq_question_list = randomized_questions
                request.session['mcq_question_list'] = mcq_question_list
            else:
                mcq_question_list = Question.objects.filter(id__in=exam.question_list, question_type='mcq').values()                    
                request.session['mcq_question_list'] = list(mcq_question_list)     
            
            request.session.modified = True
        else:
            mcq_question_list = request.session['mcq_question_list']
        
        #True / False    
        if 'tf_question_list' not in request.session: 
            tf_question_list = None
            
            if exam.random_order:
                tf_question_list = Question.objects.filter(id__in=exam.question_list, question_type='tf')
                randomized_questions = []
                for question in tf_question_list:
                    randomized_questions.append({
                        'id': question.id,
                        'question': question.question,  
                    })
                random.shuffle(randomized_questions)
                tf_question_list = randomized_questions
                request.session['tf_question_list'] = tf_question_list
            else:
                tf_question_list = Question.objects.filter(id__in=exam.question_list, question_type='tf').values()
                request.session['tf_question_list'] = list(tf_question_list)      
            
            request.session.modified = True
        else:
            tf_question_list = request.session['tf_question_list']
        
        #Essay      
        if 'essay_question_list' not in request.session:
            essay_question_list = None            
            
            if exam.random_order:
                essay_question_list = Question.objects.filter(id__in=exam.question_list, question_type='essay')     
                #essay question
                randomized_questions = []
                for question in essay_question_list:
                    randomized_questions.append({
                        'id': question.id,
                        'question': question.question,  
                    })
                random.shuffle(randomized_questions)
                essay_question_list = randomized_questions
                request.session['essay_question_list'] = essay_question_list
            else:
                essay_question_list = Question.objects.filter(id__in=exam.question_list, question_type='essay').values()
                request.session['essay_question_list'] = list(essay_question_list)  
                    
            request.session.modified = True
        else:
            print("essay question list in session")
            essay_question_list = request.session['essay_question_list']                
    # Exam ongoing
    else: 
        print('exam undergoing')
        # Calculate remaining time based on the last update
        time_elapsed = now().timestamp() - request.session['last_updated']
        request.session['time_remaining'] -= int(time_elapsed)
        request.session['time_remaining'] = max(request.session['time_remaining'], 0)  # Ensure no negative time
        request.session['last_updated'] = now().timestamp()
        request.session.modified = True
        
        #Retrive question from session
        mcq_question_list = request.session['mcq_question_list']
        tf_question_list = request.session['tf_question_list']
        essay_question_list = request.session['essay_question_list']

    mcq_selected_answers = request.session.get('mcq_selected_answers', {})
    tf_selected_answers = request.session.get('tf_selected_answers', {})
    essay_selected_answers = request.session.get('essay_selected_answers', {})
    
    print(mcq_question_list)
    
    context = {
        'exam' : exam,
        'tracking_setting' : tracking_setting,
        'mcq_question_list' : mcq_question_list,
        'tf_question_list' : tf_question_list,
        'essay_question_list' : essay_question_list,
        'mcq_selected_answers' : mcq_selected_answers,
        'tf_selected_answers' : tf_selected_answers,
        'essay_selected_answers' : essay_selected_answers,
        'time_remaining': request.session['time_remaining'],
        'tab_switch_counter': request.session['tab_switch_counter'],
        'flagged_questions': request.session['flagged_questions'],
        'navoff': True,
    }
    return render(request, 'exam/examination.html', context)

def log_browser_activity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            activity = data.get('activity', '')
            status = data.get('status')
            
            if not status: #if status is null
                status = 0
            
            if 'browser_activity_log' not in request.session:
                request.session['browser_activity_log'] = []
                
            request.session['browser_activity_log'].append({
                'activity': activity,
                'status': status,
                'timestamp': localtime(now()).strftime('%Y-%m-%d %H:%M:%S')
            })  
            request.session.modified = True
            
            #print(request.session['browser_activity_log'])
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@authorized_user(authorized_groups=['student'])
def end_exam(request):
    exam_id = request.session['exam_undergoing'].get('exam_id')
    exam = Exam.objects.get(id=exam_id)
    question_list = exam.question_list
    
    student = Student.objects.get(user=request.user)
    graded_status = True
    exam_attempt =  request.session['attempt']
    total_marks = 0
    
    # Get exam full marks
    marks_list = Question.objects.filter(id__in=question_list).values_list('marks', flat=True)
    full_marks = sum(marks_list)
    
    
    if request.session['essay_selected_answers'] != {}:
        graded_status = False
    
    mcq_answer = request.session['mcq_selected_answers']
    tf_answer = request.session['tf_selected_answers']

    # Grade Exam        
    for question_id, answer in mcq_answer.items():
        try:
            question = Question.objects.get(id=question_id)
            correct_answers = set(question.correct_answers)
            selected_answers = set(answer)
            marks = question.marks
            if selected_answers == correct_answers:
                total_marks += marks
        except Question.DoesNotExist:
            print(f"Question with id {question_id} does not exist.")
    
    for question_id, answer in tf_answer.items():
        try:
            question = Question.objects.get(id=question_id)
            correct_answers = set(question.correct_answers)
            selected_answers = set([answer])
            marks = question.marks
            if selected_answers == correct_answers:
                total_marks += marks 
        except Question.DoesNotExist:
            print(f"Question with id {question_id} does not exist.")
    
    #set up essay_marks
    essay_question_list = request.session['essay_question_list']
    essay_mark = None
    if essay_question_list:
        essay_mark = {}
        for question in essay_question_list:
            essay_mark[question['id']] = 0
        dict(sorted(essay_mark.items()))

            
    # Saving exam
    completed_exam = CompletedExam(
        exam_id = exam_id,
        student_id = student.id,
        graded = graded_status,
        attempt = exam_attempt,
        total_mark = total_marks,
        full_mark = full_marks,
        time_taken = exam.duration * 60 - request.session['time_remaining'], # in seconds
        answers = request.session['answers'],
        essay_mark = essay_mark,
        comment = "",
    )
    
    #Set folder name
    folder_name = f"{exam_id}_{request.user.id}_{request.session['attempt']}_exam_screen_recordings"
    
    completed_exam.save()
    
    if 'screen_recording' in request.session:     
        screen_capture = ScreenCapture(
            completed_exam_id = completed_exam.id,
            location  = os.path.join(settings.MEDIA_ROOT, "screen_recordings", folder_name)
        )
        screen_capture.save()
        
        user = exam.question_bank.course.lecturer.user
        title = "Alert: Unusual Behavior Detected During Exam Completion"
        message = "This is to notify you that unusual behavior was detected during the recently completed exam titled "+ exam.title +" by "+ student.user.first_name + " " + student.user.last_name + " in attempt " + str(exam_attempt) + ". The behaviors have been captured via screen recording for your review." + "\n\nTo review the recordings:" + "\n\nNavigate to the Completed Exam section." + "\nSelect the relevant exam and view the logs." + "\nWe recommend reviewing the recordings promptly and taking any necessary actions in accordance with the institution's policies." + "\n\nIf you need further assistance, please contact the system administrator."

        send_notification(user, title, message, False, 2)
    
    if 'browser_activity_log' in request.session:
        browser_activity = BrowserActivity(
            completed_exam_id = completed_exam.id,
            activity_log = request.session['browser_activity_log']
        )
        browser_activity.save()
    
    
    # Clear all session data
    if 'exam_undergoing' in request.session:
        print("Delete exam_undergoing")
        del request.session['exam_undergoing']
    
    if 'screen_recording' in request.session:
        del request.session['screen_recording']
        print("screen_recording removed from session")
    
    if 'time_remaining' in request.session:
        del request.session['time_remaining']
        del request.session['last_updated']
        print("time_remaining & last updated removed from session")
    
    if 'mcq_question_list' in request.session:
        del request.session['mcq_question_list']
    if 'tf_question_list' in request.session:
        del request.session['tf_question_list']
    if 'essay_question_list' in request.session:
        del request.session['essay_question_list']
        print("mcq,tf,essay questions removed from session")
        
    if 'mcq_selected_answers' in request.session:
        del request.session['mcq_selected_answers']
    if 'tf_selected_answers' in request.session:
        del request.session['tf_selected_answers']
    if 'essay_selected_answers' in request.session:
        del request.session['essay_selected_answers']
    if 'answers' in request.session:
        del request.session['answers']
        print("selected answers removed from session")

    if 'browser_activity_log' in request.session:
        del request.session['browser_activity_log']
        print("activity log removed from session")
        
    if 'flagged_questions' in request.session:
        del request.session['flagged_questions']
        print("flagged questions removed from session")
    
    completed_exam.id = encrypt_id(completed_exam.id)
    
    return redirect('exam_ended', completed_exam.id)

@authorized_user(authorized_groups=['student'])
def exam_ended(request, encrypted_id):
    id = decrypt_id(encrypted_id)
    completed_exam = CompletedExam.objects.get(id=id)
    terminate = False
    completed_exam.id = encrypt_id(completed_exam.id)

    if 'tab_switch_counter' in request.session:
        if request.session['tab_switch_counter'] == 0:
            terminate = True
    
    context = {
        "completed_exam" : completed_exam,
        "terminate" : terminate
    }
    return render(request, 'exam/exam_ended.html', context)
