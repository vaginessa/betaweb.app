# Generated by Django 4.0.5 on 2022-06-08 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0018_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
