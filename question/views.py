from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator

from online_exam.decorators import authorized_user
from .forms import QuestionBankCreationForm, QuestionCreationForm
from user.models import Course, Lecturer
from .models import Question, QuestionBank
from exam.models import Exam
from online_exam.views import encrypt_id, decrypt_id

import json

# Create your views here.
@authorized_user(authorized_groups=['lecturer'])
def question_bank_list(request):
    lecturer = Lecturer.objects.get(user=request.user)
    question_banks = QuestionBank.objects.filter(course__lecturer=lecturer)
    course_list = Course.objects.filter(lecturer=lecturer)        

    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')
    
    # Apply search filter if there is a search query
    if search_query:
        question_banks = question_banks.filter(title__icontains=search_query)

    # Apply question type filter if a filter is selected
    if filter_type:
        question_banks = question_banks.filter(course=filter_type)
        
    paginator = Paginator(question_banks, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    question_banks = paginator.get_page(page_number)  # Get current page
    
    for question_bank in question_banks:
        question_bank.id = encrypt_id(question_bank.id)
    
    context = {
        'question_banks': question_banks,
        
        'course_list': course_list,
        'search_query': search_query,
        'filter_type': filter_type,
    }
    
    return render(request, 'question/question_bank_list.html', context)

@authorized_user(authorized_groups=['lecturer'])
def question_list(request, encrypted_id): 
    fk = decrypt_id(encrypted_id)
    if fk is None:
        raise Http404("Invalid URL")
    
    question_bank = get_object_or_404(QuestionBank, id=fk)
    questions = Question.objects.filter(question_bank=fk)

    exams = Exam.objects.filter(question_bank_id=question_bank.id)
    
    question_list = list(questions.values_list('id', flat=True))
    used_questions = {}  # Initialize an empty dictionary
    used_questions_list = []
    difference = []
    
    for exam in exams:
        difference = list(set(question_list) - set(used_questions_list))

        if len(used_questions_list) == len(questions):
            break
        
        for ques in difference:
            if ques not in used_questions.keys() or used_questions[ques] == False:     
                if str(ques) in exam.question_list:
                    used_questions_list.append(ques)
                    used_questions[ques] = True  
                elif str(ques) not in exam.question_list:
                    used_questions[ques] = False          

    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')
    
    # Apply search filter if there is a search query
    if search_query:
        questions = questions.filter(question__icontains=search_query)

    # Apply question type filter if a filter is selected
    if filter_type:
        questions = questions.filter(question_type=filter_type)
    
    # Get unique question types for the filter dropdown
    question_types = Question.objects.values_list('question_type', flat=True).distinct()
    
    paginator = Paginator(questions, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)  # Get current page
    
        
    for question in questions:
        question.id = encrypt_id(question.id)
    
    context = {
        'questions': questions,
        'question_bank': question_bank,
        'question_types': question_types,
        'search_query': search_query,
        'filter_type': filter_type,
        'used_questions' : used_questions,
    }
    
    return render(request, 'question/question_list.html', context)

@authorized_user(authorized_groups=['lecturer'])
def create_question_bank(request):
    lecturer = Lecturer.objects.get(user=request.user)
    course_list = Course.objects.filter(lecturer=lecturer)
    if request.POST:
        question_bank_form = QuestionBankCreationForm(request.POST)
        if question_bank_form.is_valid():
            print("Form Valid")
            question_bank_form.save()
            return redirect('question_bank_list')
        else:
            print("Form Invalid")
            messages.error(request, question_bank_form.errors)
            print(question_bank_form.errors)
            
    else:    
        question_bank_form = QuestionBankCreationForm

    return render(request, 'question/create_question_bank.html', {'question_bank_form': question_bank_form, 'course_list':course_list,   })

@authorized_user(authorized_groups=['lecturer'])
def edit_question_bank(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    if pk is None:
        raise Http404("Invalid URL")
    
    lecturer = Lecturer.objects.get(user=request.user)
    question_bank = QuestionBank.objects.get(pk=pk)
    course_list = Course.objects.filter(lecturer=lecturer)

    if Exam.objects.filter(question_bank_id = pk):
        has_exam = True
    else:
        has_exam = False

    if request.POST:
        question_bank_form = QuestionBankCreationForm(request.POST, instance=question_bank)
        if question_bank_form.is_valid():
            print("Form Valid")
            question_bank_form.save()
            return redirect('question_bank_list')
        else:
            print("Form Invalid")
            messages.error(request, question_bank_form.errors)
            print(question_bank_form.errors)
            
    else:    
        question_bank_form = QuestionBankCreationForm(instance=question_bank)
        context =  {
            'question_bank_form': question_bank_form, 
            'question_bank':question_bank,
            'course_list':course_list, 
            'has_exam':has_exam   
        }
    return render(request, 'question/edit_question_bank.html', context)
    
def delete_question_bank(reqeust, encrypted_id):
    pk = decrypt_id(encrypted_id)
    if pk is None:
        raise Http404("Invalid URL")
    
    question_bank = QuestionBank.objects.get(pk=pk)
    question_bank.delete()
    
    return redirect('question_bank_list')
    
@authorized_user(authorized_groups=['lecturer'])
def create_question(request):
    question_bank_id = request.GET.get('id_question_bank')
    question_bank = None
    if question_bank_id:
        print(question_bank_id.title)
        question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
        print(question_bank)
        
    if request.POST:
        post_data = request.POST.copy()
        
        if post_data['question_type'] == 'mcq':
            print("is mcq")
            options = request.POST.getlist('options') # Get all options
            correct_answers = request.POST.getlist('mcq_answers')  # Get correct answers' indices
            
            print("X")
            print(options)
            
            paired_options = {}
            
            for index, option in enumerate(options):
                print(index)
                paired_options[option] = index
            
            post_data['options'] = json.dumps(paired_options)
            post_data['correct_answers'] = json.dumps(correct_answers)
        elif post_data['question_type'] == 'tf':
            print("is tf")
            correct_answers = request.POST.getlist('tf_answers')  # Get correct answers' indices
            print(correct_answers)
            post_data['correct_answers'] = json.dumps(correct_answers)                
        question_form = QuestionCreationForm(post_data) #modified data
        
        if question_form.is_valid():
            print("Form Valid")
            question_form.save()
            return redirect('question_list', encrypted_id=encrypt_id(question_form.cleaned_data['question_bank'].id))
        else:
            print("Form invalid")
            messages.error(request, question_form.errors)
            print(question_form.errors)

    else:
        question_form = QuestionCreationForm(initial={'question_bank':question_bank})
       
    return render(request, 'question/create_question.html', {'question_form': question_form, 'question_bank': question_bank})

@authorized_user(authorized_groups=['lecturer'])
def view_question(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    if pk is None:
        raise Http404("Invalid URL")
    
    question = Question.objects.get(pk=pk)
    q_options = question.options
    q_correct_ans = question.correct_answers

    context = {
        'question': question, 
        'q_options': q_options, 
        'q_correct_ans':q_correct_ans
    }
    return render(request, "question/view_question.html", context)

@authorized_user(authorized_groups=['lecturer'])
def edit_question(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    if pk is None:
        raise Http404("Invalid URL")
    
    question = Question.objects.get(pk=pk)
    q_options = question.options
    q_correct_ans = question.correct_answers
    
    if request.POST:
        post_data = request.POST.copy()
        
        if post_data['question_type'] == 'mcq':
            print("is mcq")
            new_options = request.POST.getlist('options') # Get all options
            new_correct_answers = request.POST.getlist('mcq_answers')  # Get correct answers' indices
            
            paired_options = {}
        
            for index, option in enumerate(new_options):
                paired_options[option] = index
            
            post_data['options'] = json.dumps(paired_options)
            post_data['correct_answers'] = json.dumps(new_correct_answers)
        
        elif post_data['question_type'] == 'tf':
            print("is tf")
            new_correct_answers = request.POST.getlist('tf_answers')  # Get correct answers' indices
            print(new_correct_answers)
            post_data['correct_answers'] = json.dumps(new_correct_answers)  
            
        
        question_form = QuestionCreationForm(post_data, instance=question)
        if question_form.is_valid():
                print("Form Valid")
                question_form.save()
                return redirect('question_list', encrypted_id=encrypt_id(question_form.cleaned_data['question_bank'].id))
        else:
            print("Form invalid")
            messages.error(request, question_form.errors)
            print(question_form.errors)
    else:
        question_form = QuestionCreationForm(instance=question)
    
        context = {
            'question': question, 
            'question_form': question_form, 
            'q_options': q_options, 
            'q_correct_ans':q_correct_ans,
        }
    
    return render(request, "question/edit_question.html", context)

@authorized_user(authorized_groups=['lecturer'])
def delete_question(request, encrypted_id):
    pk = decrypt_id(encrypted_id)
    if pk is None:
        raise Http404("Invalid URL")
    
    question = Question.objects.get(pk=pk)
    question.delete()
    return redirect('question_list', encrypt_id(question.question_bank.id))