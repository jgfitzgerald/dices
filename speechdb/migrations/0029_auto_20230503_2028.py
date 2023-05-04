# Generated by Django 3.1.8 on 2023-05-03 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speechdb', '0028_auto_20221207_1140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characterinstance',
            name='disg',
        ),
        migrations.AddField(
            model_name='characterinstance',
            name='disguise',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='work',
            name='tlg',
            field=models.CharField(blank=True, max_length=12),
        ),
        migrations.AlterField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='author',
            name='urn',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='character',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='characterinstance',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='speechtag',
            name='notes',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='title',
            field=models.CharField(max_length=128),
        ),
    ]
