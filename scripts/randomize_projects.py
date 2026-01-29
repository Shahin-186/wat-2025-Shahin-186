#!/usr/bin/env python3
"""Randomize project dates/budgets and create suppliers + ProjectSupplier links.

Run from the project root (this script configures Django).
"""
import os
import sys
import random
from decimal import Decimal
from datetime import timedelta

# Ensure project root is on sys.path (script lives in scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

from django.utils import timezone
from supply_chain.models import Project, Supplier, ProjectSupplier


SUPPLIER_NAMES = [
    'Northside Materials', 'Urban Aggregates', 'Greencrete Ltd', 'Metro Scaffolding',
    'Precision Steelworks', 'Blue River Logistics', 'ModuBuild Supplies', 'RoadSafe Traffic',
    'BridgeStone Components', 'EcoTile Systems', 'Harbour Heavy Goods', 'Riverbank Timber',
    'Vertex Hardware', 'Allied Plant Hire', 'Cornerstone Concrete', 'Peak Insulation',
    'Swift Lifts', 'GroundWorks Ltd', 'Fabrication Co', 'Urban Supply Co'
]


def random_past_datetime(max_days=1200):
    # pick a random moment within the past `max_days`
    delta = timedelta(days=random.randint(1, max_days), seconds=random.randint(0, 86400))
    return timezone.now() - delta


def ensure_suppliers():
    created = 0
    existing = list(Supplier.objects.values_list('name', flat=True))
    for name in SUPPLIER_NAMES:
        if name not in existing:
            Supplier.objects.create(name=name)
            created += 1
    print(f"Suppliers ensured. Created: {created}")


def randomize_projects():
    projects = list(Project.objects.all())
    if not projects:
        print('No projects found.')
        return

    for project in projects:
        # randomize created_at to a past date and updated_at shortly after
        created_at = random_past_datetime(max_days=1200)
        updated_at = created_at + timedelta(days=random.randint(0, 60))
        project.created_at = created_at
        project.updated_at = updated_at

        # random budget between 10k and 2M
        project.budget = random.randint(10_000, 2_000_000)

        # optional: random project manager
        if not project.project_manager:
            project.project_manager = random.choice(['A. Patel','S. Jones','M. Smith','R. Khan','L. Brown'])

        project.save(update_fields=['created_at', 'updated_at', 'budget', 'project_manager'])
        print(f"Updated Project {project.pk}: {project.title} — budget={project.budget}")


def attach_suppliers():
    suppliers = list(Supplier.objects.all())
    if not suppliers:
        print('No suppliers found to attach.')
        return

    for project in Project.objects.all():
        # choose 1-4 suppliers per project
        chosen = random.sample(suppliers, k=random.randint(1, min(4, len(suppliers))))
        for supplier in chosen:
            # skip existing relation
            ps, created = ProjectSupplier.objects.get_or_create(
                project=project, supplier=supplier,
                defaults={'contract_value': Decimal(random.randint(5_000, max(10_000, project.budget // 4)))},
            )
            if not created:
                # update contract value randomly
                ps.contract_value = Decimal(random.randint(5_000, max(10_000, project.budget // 4)))
                ps.save(update_fields=['contract_value'])

    print('Attached suppliers to projects.')


if __name__ == '__main__':
    ensure_suppliers()
    randomize_projects()
    attach_suppliers()
    print('Done.')
