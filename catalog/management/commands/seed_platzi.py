import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Category, Product

PLATZI_BASE = "https://api.escuelajs.co/api/v1"


class Command(BaseCommand):
    help = "Seed catalog using Platzi Fake Store API"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        limit = options["limit"]

        self.stdout.write("Fetching categories...")
        categories = requests.get(f"{PLATZI_BASE}/categories").json()

        category_map = {}
        for c in categories:
            obj, _ = Category.objects.get_or_create(
                slug=slugify(c["name"]),
                defaults={"name": c["name"]},
            )
            category_map[c["id"]] = obj

        self.stdout.write(f"Loaded {len(category_map)} categories")

        self.stdout.write("Fetching products...")
        products = requests.get(
            f"{PLATZI_BASE}/products", params={"offset": 0, "limit": limit}
        ).json()

        created = 0
        for p in products:
            category = category_map.get(p["category"]["id"])
            if not category:
                continue

            slug = slugify(p["title"])

            obj, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": p["title"],
                    "description": p.get("description", ""),
                    "price_cents": int(float(p["price"]) * 100),
                    "currency": "USD",
                    "category": category,
                    "image_url": p["images"][0] if p.get("images") else "",
                    "is_active": True,
                },
            )

            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete. Created {created} new products."
            )
        )
