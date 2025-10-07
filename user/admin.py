from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from .models import Course, Faculty, Lecturer, Programme, Student

# Register your models here.
class CourseFilter(SimpleListFilter):
    title = 'course'  # Label for the filter
    parameter_name = 'course'  # URL parameter

    def lookups(self, request, model_admin):
        # Get the list of all courses
        courses = Course.objects.all()
        return [(course.id, course.name) for course in courses]

    def queryset(self, request, queryset):
        # Filter lecturers based on the selected course
        if self.value():
            return queryset.filter(course__id=self.value())
        return queryset
    
class FacultyFilter(SimpleListFilter):
    title = 'Faculty'  # Title for the filter
    parameter_name = 'faculty'  # URL parameter for the filter

    def lookups(self, request, model_admin):
        # Get all faculty instances
        faculties = Faculty.objects.all()
        return [(faculty.id, faculty.name) for faculty in faculties]

    def queryset(self, request, queryset):
        # Filter programmes based on the selected faculty
        if self.value():
            return queryset.filter(faculty__id=self.value())
        return queryset


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):    
    list_display = ('__str__', 'programme','cohort','registered_courses_list','phone_num')  
    search_fields = ('user__first_name', 'user__last_name', 'programme__name', 'cohort', 'phone_num')  
    list_filter = ('programme', 'cohort')  
    ordering = ('cohort', 'id')  
    
    
    def registered_courses_list(self, obj):
        course_ids = obj.registered_courses
        if not course_ids:
            course_ids = []
        # Fetch all courses corresponding to the course IDs
        courses = Course.objects.filter(id__in=course_ids)
        # Return a comma-separated string of course names
        return ", ".join([course.name for course in courses])

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):      
    list_display = ('__str__', 'faculty','courses', 'phone_num')  
    search_fields = ('user__first_name', 'user__last_name', 'faculty')  
    list_filter = ('faculty', CourseFilter)  
    ordering = ('user__first_name', 'user__last_name')  
    
    def courses(self, obj):
        # Fetch all the courses related to the current lecturer
        courses = Course.objects.filter(lecturer=obj)
        # Return a comma-separated string of course names
        return ", ".join([course.name for course in courses])
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'programme__name','lecturer')  
    search_fields = ('name', 'code', 'programme__name')  
    list_filter = ('lecturer', 'programme')  
    ordering = ('code', 'name')  
      
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)  
    list_filter = ('name',)  
    ordering = ('name',)  

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty__name')  
    search_fields = ('name', 'faculty__name')  
    list_filter = ('name', FacultyFilter)  
    ordering = ('name',)  