# Generated by Django 2.2.7 on 2020-03-09 09:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_v1', '0007_delete_responsesequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentresponse',
            name='skill',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tutor_v1.Skill'),
            preserve_default=False,
        ),
    ]