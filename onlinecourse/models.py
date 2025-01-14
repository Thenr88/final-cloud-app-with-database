import sys
from django.utils.timezone import now
from django.db.models import Sum
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description

    
    def get_total_marks(self):
        return Question.objects.filter(course=self).aggregate(marks=Sum('question_grades'))["marks"]


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.id} -- {self.title}"


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def submission( self ):
        submission = Submission.objects.filter( enrollment=self ).first()
        return submission


# <HINT> Create a Question Model with:
    # Used to persist question content for a course
    # Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
    # Has a grade point for each question
    # Has question content
    # Other fields and methods you would like to design
class Question(models.Model):
    # Foreign key to lesson
    # question text
    # question grade/mark
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    question_grades = models.IntegerField()

    def __str__(self):
        return f"{self.id} -- {self.question_text}"

    # <HINT> A sample model method to calculate if learner get the score of the question
    def is_get_score(self, selected_ids):
       all_answers = self.choice_set.filter(is_correct=True).count()
       selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
       if all_answers == selected_correct:
           return True
       else:
           return False




#  <HINT> Create a Choice Model with:
    # Used to persist choice content for a question
    # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    # Choice content
    # Indicate if this choice of the question is a correct one or not
    # Other fields and methods you would like to design
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_content = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} -- {self.question.question_text} -- {self.choice_content}"

# <HINT> The submission model
# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    #  Other fields and methods you would like to design

    def get_grade(self):
        grade = 0
        submitted_choices = self.choices.all()

        if submitted_choices.count():
            for submitted_choice in submitted_choices:
                if self.is_correct( submitted_choice ):
                    grade = grade+self.get_question_grade(submitted_choice)

        return grade

    def get_percentage(self):
        grade = self.get_grade()
        # get all the questions 
        total_marks = self.get_total_available_marks_for_course()
        # calculate total marks
        percentage = 0
        if total_marks > 0:
            percentage = (grade/total_marks)*100 if grade > 0 else 0
            
        return int(percentage)

    def get_total_available_marks_for_course(self):
        choices = self.choices.all()
        # get course
        course = choices[0].question.course if choices.count() > 0 else None

        # calculate total marks
        return course.get_total_marks() if course else 0

    def is_correct(self, submitted_choice ):
        choice = Choice.objects.get(pk=submitted_choice.id)
        return choice.is_correct

    def get_question_grade(self, submitted_choice ):
        choice = Choice.objects.get(pk=submitted_choice.id)
        return int(choice.question.question_grades)
