from django.core.management.base import BaseCommand
from supply_chain.models import Supplier, ProjectSupplier, Project, Council
from decimal import Decimal, ROUND_HALF_UP
import random
import re


def mk_email(name):
    s = re.sub(r"[^a-z0-9]+", '.', name.lower()).strip('.')
    return f"contact@{s}.example.com"


def mk_phone():
    # simple UK-like mobile format
    return f"07{random.randint(100000000,999999999)}"


def mk_address(name, council_name=None):
    street = random.choice(['High Street', 'Station Road', 'Victoria Avenue', 'Market Place', 'Church Lane'])
    number = random.randint(1, 220)
    town = council_name or random.choice(['Leeds', 'Bradford', 'York', 'Sheffield'])
    return f"{number} {street}, {town}"


SPECIALTIES = {
    'edu': 'Education & public buildings',
    'road': 'Highway & surfacing',
    'bridge': 'Bridge engineering',
    'cycle': 'Cycleways & sustainable transport',
    'landscape': 'Parks & landscaping',
    'housing': 'Housing development',
    'drain': 'Drainage & flood defence',
    'bus': 'Public transport services',
    'general': 'General construction & civils',
}


class Command(BaseCommand):
    help = 'Populate supplier contact info and fill missing ProjectSupplier contract values.'

    def handle(self, *args, **options):
        suppliers = Supplier.objects.all()
        created = 0
        updated = 0

        for s in suppliers:
            changed = False

            # contact person
            if not s.contact_person:
                s.contact_person = random.choice(['Alex Patel','Sam Johnson','Lea Brown','Mohammed Singh','Rachel Taylor','James Smith'])
                changed = True

            # email
            if not s.contact_email:
                s.contact_email = mk_email(s.name)
                changed = True

            # phone
            if not s.phone:
                s.phone = mk_phone()
                changed = True

            # specialty inference
            if not s.specialty:
                key = 'general'
                name = s.name.lower()
                if any(k in name for k in ['edu','school','university','library']):
                    key = 'edu'
                elif any(k in name for k in ['road','surf','highway','junction']):
                    key = 'road'
                elif 'bridge' in name:
                    key = 'bridge'
                elif any(k in name for k in ['cycle','bike']):
                    key = 'cycle'
                elif any(k in name for k in ['park','landscape','greenspace']):
                    key = 'landscape'
                elif any(k in name for k in ['home','housing']):
                    key = 'housing'
                elif any(k in name for k in ['drain','flood','aqua']):
                    key = 'drain'
                elif any(k in name for k in ['bus','transport','metro']):
                    key = 'bus'
                s.specialty = SPECIALTIES.get(key, SPECIALTIES['general'])
                changed = True

            # address
            if not s.address:
                # try to pick a council to use as town
                council = Council.objects.order_by('?').first()
                s.address = mk_address(s.name, council.name if council else None)
                changed = True

            if changed:
                s.save()
                updated += 1

        # Now fill ProjectSupplier.contract_value where blank using project budget fractions
        links = ProjectSupplier.objects.filter(contract_value__isnull=True)
        links_updated = 0
        for l in links:
            budget = getattr(l.project, 'budget', None)
            if budget and budget > 0:
                # assign a smaller contractor fraction for suppliers when multiple suppliers may exist
                frac = random.uniform(0.05, 0.5)
                val = Decimal(budget * frac).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                val = Decimal(random.randint(5000, 500000)).quantize(Decimal('0.01'))
            l.contract_value = val
            l.save()
            links_updated += 1

        self.stdout.write(self.style.SUCCESS(f'Suppliers updated: {updated}'))
        self.stdout.write(self.style.SUCCESS(f'ProjectSupplier links updated: {links_updated}'))
