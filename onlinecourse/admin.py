from django.contrib import admin
from django.contrib.admin import display
# <HINT> Import any new Models here
from .models import Choice, Course, Lesson, Instructor, Learner, Question, Submission

# <HINT> Register QuestionInline and ChoiceInline classes here


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('course_name', 'lesson_title', 'question_text', 'question_grades')
    # list_filter = ['course__name', 'lesson__title']
    # search_fields = ['course_name', 'lesson_title', 'question_text']

    @display(ordering='course__name', description='Course Name')
    def course_name(self, obj):
        return obj.course.name

    @display( description='Lesson Title')
    def lesson_title(self, obj):
        return obj.lesson.title

# <HINT> Register Question and Choice models here

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
