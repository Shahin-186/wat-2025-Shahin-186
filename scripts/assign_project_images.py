#!/usr/bin/env python3

import os
import sys
import django

# Ensure project root is on sys.path (script lives in scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from supply_chain.models import Project

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1526401281623-4f6f6c6a2d6f?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1505842465776-3d5075a5b5b1?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1494526585095-c41746248156?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1541832676-6c4f2f4d7b5e?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200&h=800&fit=crop",
    "https://images.unsplash.com/photo-1504286108057-649d9e160f1f?w=1200&h=800&fit=crop",
]


def assign_images():
    projects = list(Project.objects.all().order_by('pk'))
    if not projects:
        print('No projects found.')
        return

    updated = 0
    for i, project in enumerate(projects):
        if not project.main_image:
            url = IMAGE_URLS[i % len(IMAGE_URLS)]
            project.main_image = url
            project.save(update_fields=['main_image'])
            print(f"Updated Project {project.pk}: '{project.title}' -> {url}")
            updated += 1

    print(f"Done. {updated} projects updated.")


if __name__ == '__main__':
    assign_images()
