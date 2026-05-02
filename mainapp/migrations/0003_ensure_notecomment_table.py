from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0002_notelike"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS mainapp_notecomment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                note_id BIGINT NOT NULL REFERENCES mainapp_note(id) DEFERRABLE INITIALLY DEFERRED,
                user_id INTEGER NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
            );
            CREATE INDEX IF NOT EXISTS mainapp_notecomment_note_id_idx ON mainapp_notecomment (note_id);
            CREATE INDEX IF NOT EXISTS mainapp_notecomment_user_id_idx ON mainapp_notecomment (user_id);
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
