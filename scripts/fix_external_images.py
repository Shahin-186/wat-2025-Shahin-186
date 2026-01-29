#!/usr/bin/env python3
"""
Download images from Unsplash's source endpoint for projects that still
reference external URLs, save them under `supply_chain/static/img/projects/`
and update `Project.main_image` to point to the local static path.

Run from the repository root (where `manage.py` lives):
  python3 scripts/fix_external_images.py
"""
import os
import sys
from urllib.parse import urlparse
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from supply_chain.models import Project

STATIC_DIR = os.path.join(BASE_DIR, 'supply_chain', 'static', 'img', 'projects')
os.makedirs(STATIC_DIR, exist_ok=True)


def download(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def main():
    qs = Project.objects.filter(main_image__startswith='http').order_by('pk')
    if not qs.exists():
        print('No external images found. Nothing to do.')
        return

    updated = 0
    for p in qs:
        # Use the stable Unsplash source with a sig tied to project pk to get unique images
        source_url = f'https://source.unsplash.com/1200x800/?construction&sig={p.pk}'
        filename = f'project_{p.pk}.jpg'
        dest_path = os.path.join(STATIC_DIR, filename)

        print(f'Downloading for Project {p.pk} -> {dest_path}')
        ok = download(source_url, dest_path)
        if not ok:
            # Try a reliable fallback (picsum) if Unsplash fails
            fallback = f'https://picsum.photos/1200/800?random={p.pk}'
            print(f'  Unsplash failed, trying fallback {fallback}')
            ok = download(fallback, dest_path)

        if ok:
            p.main_image = f'/static/img/projects/{filename}'
            p.save(update_fields=['main_image'])
            updated += 1

    print(f'Done. {updated} projects updated to local images.')


if __name__ == '__main__':
    main()
