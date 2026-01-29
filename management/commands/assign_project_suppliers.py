from django.core.management.base import BaseCommand
from supply_chain.models import Project, Supplier, ProjectSupplier
from django.db import transaction
import random
from decimal import Decimal, ROUND_HALF_UP


class Command(BaseCommand):
    help = 'Ensure each Project has at least one key Supplier; create Suppliers when needed.'

    def handle(self, *args, **options):
        # mapping of keywords to supplier defaults
        mapping = [
            (['school', 'college', 'university', 'academy', 'education', 'library'],
             {'name': 'EduBuild Contractors', 'specialty': 'Education & public buildings'}),
            (['road', 'resurface', 'resurfacing', 'highway', 'junction', 'traffic'],
             {'name': 'Metro Roadworks Ltd', 'specialty': 'Highway & surfacing'}),
            (['bridge'],
             {'name': 'BridgeTech Ltd', 'specialty': 'Bridge engineering'}),
            (['cycle', 'bike', 'cycleway'],
             {'name': 'GreenCycle Solutions', 'specialty': 'Cycleways & sustainable transport'}),
            (['park', 'playground', 'greenspace', 'green'],
             {'name': 'Urban Landscapes Co', 'specialty': 'Parks & landscaping'}),
            (['housing', 'homes', 'residential', 'affordable'],
             {'name': 'City Homes Builders', 'specialty': 'Housing development'}),
            (['drain', 'flood', 'sewer', 'drainage'],
             {'name': 'AquaWorks Ltd', 'specialty': 'Drainage & flood defence'}),
        ]

        # fallback pool of suppliers
        fallback = [
            {'name': 'Acme Construction', 'specialty': 'General construction'},
            {'name': 'Northside Contractors', 'specialty': 'Civil engineering'},
            {'name': 'BlueStar Maintainers', 'specialty': 'Maintenance & repairs'},
        ]

        projects = Project.objects.all()
        created_links = 0
        created_suppliers = 0

        for p in projects:
            if p.project_suppliers.exists():
                continue

            text = ' '.join(filter(None, [p.title, getattr(p.category, 'name', ''), p.description or ''])).lower()
            chosen_supplier_info = None
            for keywords, info in mapping:
                for kw in keywords:
                    if kw in text:
                        chosen_supplier_info = info
                        break
                if chosen_supplier_info:
                    break

            if not chosen_supplier_info:
                chosen_supplier_info = random.choice(fallback)

            # get or create supplier
            supplier, created = Supplier.objects.get_or_create(
                name=chosen_supplier_info['name'],
                defaults={
                    'contact_person': '',
                    'contact_email': '',
                    'phone': '',
                    'address': '',
                    'specialty': chosen_supplier_info.get('specialty', '')
                }
            )
            if created:
                created_suppliers += 1

            # determine contract value (a fraction of project budget if available)
            contract_value = None
            if p.budget:
                frac = random.uniform(0.25, 0.8)
                val = Decimal(p.budget * frac).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                contract_value = val

            with transaction.atomic():
                ps = ProjectSupplier.objects.create(project=p, supplier=supplier, contract_value=contract_value)
                created_links += 1
                self.stdout.write(self.style.SUCCESS(f'Attached supplier "{supplier.name}" to project id={p.id}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Suppliers created: {created_suppliers}. Links created: {created_links}.'))
