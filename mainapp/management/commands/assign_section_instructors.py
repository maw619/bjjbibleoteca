from django.core.management.base import BaseCommand, CommandError

from mainapp.models import Instructor, Section


class Command(BaseCommand):
    help = (
        "Bulk-assign instructors to sections.\n"
        "Example:\n"
        '  python manage.py assign_section_instructors --pair "Guard Retention=Lachlan Giles"'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--pair",
            action="append",
            default=[],
            help='Assignment pair in the format "Section Name=Instructor Name". Repeat for multiple assignments.',
        )
        parser.add_argument(
            "--contains",
            action="append",
            default=[],
            help=(
                'Pattern assignment in the format "section_substring=Instructor Name". '
                "Any section name containing the substring (case-insensitive) will be assigned."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving.",
        )

    def _parse_mapping(self, raw_item, label):
        if "=" not in raw_item:
            raise CommandError(f'Invalid {label}: "{raw_item}". Expected format: section=instructor')
        left, right = [part.strip() for part in raw_item.split("=", 1)]
        if not left or not right:
            raise CommandError(f'Invalid {label}: "{raw_item}". Both section and instructor are required.')
        return left, right

    def handle(self, *args, **options):
        exact_pairs = [self._parse_mapping(item, "--pair") for item in options["pair"]]
        contains_pairs = [self._parse_mapping(item, "--contains") for item in options["contains"]]
        dry_run = options["dry_run"]

        if not exact_pairs and not contains_pairs:
            raise CommandError("No assignments provided. Use --pair and/or --contains.")

        changed = 0
        seen_section_ids = set()

        for section_name, instructor_name in exact_pairs:
            sections = Section.objects.filter(name=section_name).select_related("instructor")
            if not sections.exists():
                self.stdout.write(self.style.WARNING(f'No section found with exact name: "{section_name}"'))
                continue
            instructor = None if dry_run else Instructor.objects.get_or_create(name=instructor_name)[0]
            for section in sections:
                seen_section_ids.add(section.id)
                current = section.instructor.name if section.instructor else "(none)"
                if current == instructor_name:
                    continue
                changed += 1
                self.stdout.write(f'[exact] {section.name}: {current} -> {instructor_name}')
                if not dry_run:
                    section.instructor = instructor
                    section.save(update_fields=["instructor"])

        for substring, instructor_name in contains_pairs:
            sections = Section.objects.filter(name__icontains=substring).select_related("instructor")
            if not sections.exists():
                self.stdout.write(self.style.WARNING(f'No section found containing: "{substring}"'))
                continue
            instructor = None if dry_run else Instructor.objects.get_or_create(name=instructor_name)[0]
            for section in sections:
                if section.id in seen_section_ids:
                    continue
                seen_section_ids.add(section.id)
                current = section.instructor.name if section.instructor else "(none)"
                if current == instructor_name:
                    continue
                changed += 1
                self.stdout.write(f'[contains] {section.name}: {current} -> {instructor_name}')
                if not dry_run:
                    section.instructor = instructor
                    section.save(update_fields=["instructor"])

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. {changed} section(s) would be updated."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Updated {changed} section(s)."))
