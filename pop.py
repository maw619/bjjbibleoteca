import os
import django
import boto3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bjj_library.settings")
django.setup()

from mainapp.models import Category, Section, Video

bucket_name = "my-bucket-maw"
s3 = boto3.client("s3")

paginator = s3.get_paginator("list_objects_v2")

total = 0

for page in paginator.paginate(Bucket=bucket_name, Prefix="bjj/"):
    for obj in page.get("Contents", []):
        key = obj["Key"]

        if not key.endswith(".mp4"):
            continue

        parts = key.split("/")

        if len(parts) < 3:
            continue

        category_name = parts[1]
        video_name = parts[-1].replace(".mp4", "")

        # 🔥 HANDLE BOTH STRUCTURES

        if len(parts) >= 5:
            # Deep structure
            section_name = parts[2] + " / " + parts[3]
        elif len(parts) >= 4:
            # Medium structure
            section_name = parts[2]
        else:
            # Flat structure
            section_name = "General"

        category, _ = Category.objects.get_or_create(name=category_name)

        section, _ = Section.objects.get_or_create(
            name=section_name,
            category=category
        )

        Video.objects.get_or_create(
            title=video_name,
            section=section,
            url=f"https://{bucket_name}.s3.amazonaws.com/{key}"
        )

        total += 1

        if total % 100 == 0:
            print(f"Imported {total} videos...")

print(f"🎉 DONE: {total} videos imported")