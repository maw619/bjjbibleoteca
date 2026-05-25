from django.db import migrations, models
import django.db.models.deletion


def copy_section_instructors(apps, schema_editor):
    Section = apps.get_model("mainapp", "Section")
    Instructor = apps.get_model("mainapp", "Instructor")

    for section in Section.objects.exclude(instructor="").exclude(instructor__isnull=True):
        instructor_name = section.instructor.strip()
        if not instructor_name:
            continue
        instructor_obj, _ = Instructor.objects.get_or_create(name=instructor_name)
        section.instructor_ref = instructor_obj
        section.save(update_fields=["instructor_ref"])


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0002_section_instructor"),
    ]

    operations = [
        migrations.CreateModel(
            name="Instructor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="section",
            name="instructor_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sections",
                to="mainapp.instructor",
            ),
        ),
        migrations.RunPython(copy_section_instructors, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="section",
            name="instructor",
        ),
        migrations.RenameField(
            model_name="section",
            old_name="instructor_ref",
            new_name="instructor",
        ),
    ]
