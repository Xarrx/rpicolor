# Generated by Django 2.1.3 on 2018-12-04 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ColorApp', '0002_auto_20181204_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedcolor',
            name='blue',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='savedcolor',
            name='brightness',
            field=models.PositiveSmallIntegerField(default=255),
        ),
        migrations.AlterField(
            model_name='savedcolor',
            name='green',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='savedcolor',
            name='name',
            field=models.CharField(default='unnamed', max_length=256),
        ),
        migrations.AlterField(
            model_name='savedcolor',
            name='red',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]