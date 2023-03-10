# Generated by Django 4.1.7 on 2023-03-05 13:13

from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):
    dependencies = [
        ("mentorizon", "0006_alter_ratingvote_rate"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="sphere",
            name="name_unique",
        ),
        migrations.AddConstraint(
            model_name="sphere",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                name="name_unique",
                violation_error_message="Sphere with this name already exists.",
            ),
        ),
    ]
