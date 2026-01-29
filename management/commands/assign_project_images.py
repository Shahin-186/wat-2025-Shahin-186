from django.core.management.base import BaseCommand
from django.conf import settings
from supply_chain.models import Project
import os


class Command(BaseCommand):
    help = 'Assign project images based on project title or category keywords'

    def handle(self, *args, **options):
        base_static = os.path.join(settings.BASE_DIR, 'supply_chain', 'static', 'img', 'projects')

        # mapping of keyword -> filename (choose a representative image available in static)
        mapping = [
            (['school', 'college', 'university', 'academy'], 'project_31.jpg'),
            (['library', 'libraries'], 'project_13.jpg'),
            (['road', 'resurfacing', 'resurface', 'highway', 'junction'], 'project_16.jpg'),
            (['bridge'], 'project_28.jpg'),
            (['cycle', 'bike', 'cycleway'], 'project_24.jpg'),
            (['park', 'playground', 'greenspace', 'green'], 'project_20.jpg'),
            (['housing', 'homes', 'affordable', 'residential'], 'project_22.jpg'),
            (['drain', 'flood', 'sewer', 'drainage'], 'project_29.jpg'),
            (['school'], 'project_31.jpg'),
        ]

        # gather fallback list of available images in the folder
        try:
            available = [f for f in os.listdir(base_static) if f.lower().endswith('.jpg')]
        except Exception:
            available = []

        projects = Project.objects.all()
        updated = 0
        for p in projects:
            text = ' '.join(filter(None, [p.title, getattr(p.category, 'name', '')])).lower()
            chosen = None
            for keywords, fname in mapping:
                for kw in keywords:
                    if kw in text:
                        path = os.path.join(base_static, fname)
                        if os.path.exists(path):
                            chosen = f'/static/img/projects/{fname}'
                            break
                if chosen:
                    break

            if not chosen:
                # fallback: choose by simple heuristics or cycle through available
                if available:
                    # pick a consistent file using id
                    fname = available[p.id % len(available)]
                    chosen = f'/static/img/projects/{fname}'
                else:
                    chosen = ''

            if chosen and p.main_image != chosen:
                p.main_image = chosen
                if not p.image:
                    p.image = chosen
                p.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Updated project id={p.id} -> {chosen}"))

        self.stdout.write(self.style.SUCCESS(f'Completed. {updated} projects updated.'))
