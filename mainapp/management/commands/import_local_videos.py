from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mainapp.models import Category, Section, Video


class Command(BaseCommand):
    help = "Import local video files into Category, Section, and Video rows."

    VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}

    def add_arguments(self, parser):
        parser.add_argument(
            "--root",
            default=getattr(settings, "LOCAL_VIDEO_ROOT", "/mnt/BJJ_STORAGE"),
            help="Mounted folder containing the video library. Default: settings.LOCAL_VIDEO_ROOT.",
        )
        parser.add_argument(
            "--url-prefix",
            default=getattr(settings, "LOCAL_VIDEO_URL", "/media/videos/"),
            help="URL prefix that your web server maps to --root. Default: settings.LOCAL_VIDEO_URL.",
        )
        parser.add_argument(
            "--strip-prefix",
            default="bjj",
            help="Drop this leading path folder before deriving categories. Use '' to disable. Default: bjj.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without writing database rows.",
        )

    def handle(self, *args, **options):
        root = Path(options["root"]).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise CommandError(f"Video root does not exist or is not a directory: {root}")

        url_prefix = options["url_prefix"].strip() or "/media/videos/"
        if not url_prefix.endswith("/"):
            url_prefix = f"{url_prefix}/"

        strip_prefix = options["strip_prefix"].strip("/")
        dry_run = options["dry_run"]

        created = updated = unchanged = skipped = 0

        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.VIDEO_EXTENSIONS:
                continue

            relative = path.relative_to(root)
            parts = relative.parts
            if strip_prefix and parts and parts[0].lower() == strip_prefix.lower():
                parts = parts[1:]

            if not parts:
                skipped += 1
                continue

            category_name = parts[0] if len(parts) >= 2 else "General"
            title = path.stem

            if len(parts) >= 4:
                section_name = " / ".join(parts[1:-1])
            elif len(parts) >= 3:
                section_name = parts[1]
            else:
                section_name = "General"

            url = url_prefix + quote(str(relative).replace("\\", "/"))

            if dry_run:
                self.stdout.write(f"DRY RUN: {category_name} | {section_name} | {title} -> {url}")
                unchanged += 1
                continue

            category, _ = Category.objects.get_or_create(name=category_name)
            section, _ = Section.objects.get_or_create(name=section_name, category=category)
            video, was_created = Video.objects.get_or_create(
                title=title,
                section=section,
                defaults={"url": url},
            )

            if was_created:
                created += 1
            elif video.url != url:
                video.url = url
                video.save(update_fields=["url"])
                updated += 1
            else:
                unchanged += 1

            total = created + updated + unchanged
            if total and total % 100 == 0:
                self.stdout.write(f"Processed {total} videos...")

        action = "Scanned" if dry_run else "Imported"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} local videos. Created: {created}, updated: {updated}, unchanged: {unchanged}, skipped: {skipped}."
            )
        )
