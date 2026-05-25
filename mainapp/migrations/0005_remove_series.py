from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0004_series_and_section_series"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="section",
            name="series",
        ),
        migrations.DeleteModel(
            name="Series",
        ),
    ]
