from itertools import product as cartesian_product
from uuid import uuid4

from django.db import transaction
from django.db.models import Sum

from .models import Product, ProductSku


def build_category_tree(categories):
    nodes = {}
    roots = []

    for category in categories:
        nodes[category.id] = {
            "id": category.id,
            "name": category.name,
            "parent": category.parent_id,
            "level": category.level,
            "path": category.path,
            "icon": category.icon,
            "banner": category.banner,
            "sort": category.sort,
            "is_show": category.is_show,
            "is_distribution": category.is_distribution,
            "children": [],
        }

    for category in categories:
        node = nodes[category.id]
        if category.parent_id and category.parent_id in nodes:
            nodes[category.parent_id]["children"].append(node)
        else:
            roots.append(node)

    sort_tree(roots)
    return roots


def sort_tree(nodes):
    nodes.sort(key=lambda item: (-item["sort"], item["id"]))
    for node in nodes:
        sort_tree(node["children"])


def generate_product_skus(product_id, spec_options, defaults, overwrite=False):
    normalized_options = normalize_spec_options(spec_options)
    combinations = list(cartesian_product(*[option["values"] for option in normalized_options]))

    with transaction.atomic():
        product = Product.objects.select_for_update().get(pk=product_id)
        if overwrite:
            product.skus.all().delete()
            existing_specs = set()
        else:
            existing_specs = {spec_signature(sku.specs) for sku in product.skus.all()}

        created_skus = []
        for combination in combinations:
            specs = {
                option["name"]: value
                for option, value in zip(normalized_options, combination)
            }
            if spec_signature(specs) in existing_specs:
                continue

            sku = ProductSku.objects.create(
                product=product,
                sku_code=build_sku_code(product),
                specs=specs,
                price=defaults["price"],
                market_price=defaults.get("market_price", 0),
                stock=defaults.get("stock", 0),
                warning_stock=defaults.get("warning_stock", 0),
                is_active=True,
            )
            created_skus.append(sku)
            existing_specs.add(spec_signature(specs))

        total_stock = product.skus.aggregate(total=Sum("stock"))["total"] or 0
        product.total_stock = total_stock
        if created_skus and product.price == 0:
            product.price = created_skus[0].price
        product.save(update_fields=["total_stock", "price", "updated_at"])

    return product, created_skus, len(combinations)


def normalize_spec_options(spec_options):
    if not spec_options:
        raise ValueError("spec_options is required.")

    normalized = []
    seen_names = set()
    for option in spec_options:
        name = str(option.get("name", "")).strip()
        values = [str(value).strip() for value in option.get("values", []) if str(value).strip()]

        if not name:
            raise ValueError("Each spec option needs a name.")
        if name in seen_names:
            raise ValueError(f"Duplicate spec option name: {name}.")
        if not values:
            raise ValueError(f"Spec option {name} needs at least one value.")

        seen_names.add(name)
        normalized.append({"name": name, "values": values})

    return normalized


def spec_signature(specs):
    return tuple(sorted(specs.items()))


def build_sku_code(product):
    return f"P{product.pk:06d}-{uuid4().hex[:10].upper()}"
