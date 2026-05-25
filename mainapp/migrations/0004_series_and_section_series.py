from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0003_normalize_instructor_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="Series",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="section",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sections",
                to="mainapp.series",
            ),
        ),
    ]
