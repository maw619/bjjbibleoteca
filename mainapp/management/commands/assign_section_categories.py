from django.core.management.base import BaseCommand, CommandError

from mainapp.models import Category, Section


class Command(BaseCommand):
    help = (
        "Bulk-assign categories to sections.\n"
        "Examples:\n"
        '  python manage.py assign_section_categories --pair "Guard Retention=Open Guard"\n'
        '  python manage.py assign_section_categories --contains "danaher=John Danaher" --dry-run'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--pair",
            action="append",
            default=[],
            help='Exact mapping in format "Section Name=Category Name". Repeatable.',
        )
        parser.add_argument(
            "--contains",
            action="append",
            default=[],
            help='Substring mapping in format "section_substring=Category Name". Repeatable.',
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview updates without saving.",
        )

    def _parse_mapping(self, raw_item, flag_name):
        if "=" not in raw_item:
            raise CommandError(f'Invalid {flag_name}: "{raw_item}". Expected format: section=category')
        left, right = [part.strip() for part in raw_item.split("=", 1)]
        if not left or not right:
            raise CommandError(f'Invalid {flag_name}: "{raw_item}". Both section and category are required.')
        return left, right

    def _assign_sections(self, sections, category_name, match_label, dry_run, seen_ids):
        if not sections.exists():
            return 0

        category = None if dry_run else Category.objects.get_or_create(name=category_name)[0]
        changed = 0

        for section in sections.select_related("category"):
            if section.id in seen_ids:
                continue
            seen_ids.add(section.id)
            current = section.category.name if section.category else "(none)"
            if current == category_name:
                continue

            changed += 1
            self.stdout.write(f"[{match_label}] {section.name}: {current} -> {category_name}")
            if not dry_run:
                section.category = category
                section.save(update_fields=["category"])

        return changed

    def handle(self, *args, **options):
        exact_pairs = [self._parse_mapping(item, "--pair") for item in options["pair"]]
        contains_pairs = [self._parse_mapping(item, "--contains") for item in options["contains"]]
        dry_run = options["dry_run"]

        if not exact_pairs and not contains_pairs:
            raise CommandError("No assignments provided. Use --pair and/or --contains.")

        changed = 0
        seen_ids = set()

        for section_name, category_name in exact_pairs:
            sections = Section.objects.filter(name=section_name)
            if not sections.exists():
                self.stdout.write(self.style.WARNING(f'No section found with exact name: "{section_name}"'))
                continue
            changed += self._assign_sections(sections, category_name, "exact", dry_run, seen_ids)

        for substring, category_name in contains_pairs:
            sections = Section.objects.filter(name__icontains=substring)
            if not sections.exists():
                self.stdout.write(self.style.WARNING(f'No section found containing: "{substring}"'))
                continue
            changed += self._assign_sections(sections, category_name, "contains", dry_run, seen_ids)

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. {changed} section(s) would be updated."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Updated {changed} section(s)."))
