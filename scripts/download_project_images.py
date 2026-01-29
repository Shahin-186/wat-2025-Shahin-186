#!/usr/bin/env python3
"""
Download external project images into the app's static folder and update
Project.main_image to point to the local static path.

Run from the repo root (where `manage.py` is):
  python3 scripts/download_project_images.py

This script uses only the standard library.
"""
import os
import sys
import urllib.request
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from supply_chain.models import Project


STATIC_DIR = os.path.join(BASE_DIR, 'supply_chain', 'static', 'img', 'projects')
os.makedirs(STATIC_DIR, exist_ok=True)


def download(url, dest_path):
    try:
        urllib.request.urlretrieve(url, dest_path)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def main():
    projects = Project.objects.all().order_by('pk')
    if not projects:
        print('No projects found.')
        return

    updated = 0
    for project in projects:
        src = project.main_image or project.image
        if not src:
            print(f"Project {project.pk} has no image source; skipping")
            continue

        # Skip if already a local static path
        if isinstance(src, str) and src.startswith('/static/'):
            print(f"Project {project.pk} image already local: {src}")
            continue

        parsed = urlparse(src)
        if not parsed.scheme.startswith('http'):
            print(f"Project {project.pk} image not downloadable: {src}")
            continue

        # Determine extension (simple fallback)
        _, ext = os.path.splitext(parsed.path)
        if ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            ext = '.jpg'

        filename = f'project_{project.pk}{ext}'
        dest_path = os.path.join(STATIC_DIR, filename)
        print(f"Downloading {src} -> {dest_path}")
        ok = download(src, dest_path)
        if ok:
            project.main_image = f'/static/img/projects/{filename}'
            project.save(update_fields=['main_image'])
            updated += 1

    print(f"Done. {updated} projects updated with local images.")


if __name__ == '__main__':
    main()
