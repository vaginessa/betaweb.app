# Generated by Django 4.0.5 on 2022-06-05 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0014_alter_post_shortcode_carouselmedia_image_cm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='biography',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
