from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_remove_note_unique_per_video'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ['-updated_at']},
        ),
    ]
