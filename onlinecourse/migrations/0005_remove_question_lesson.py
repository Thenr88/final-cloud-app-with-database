# Generated by Django 3.2.7 on 2022-03-12 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0004_alter_question_question_grades'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='lesson',
        ),
    ]
