from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import ProductCategory, SpecTemplate
from apps.core.menu import ADMIN_MENU
from apps.core.models import AdminMenu
from apps.distribution.models import DistributionConfigModel
from apps.users.models import MemberLevel, User


MEMBER_LEVELS = [
    {
        "name": "普通用户",
        "upgrade_amount": Decimal("0.00"),
        "team_upgrade_amount": Decimal("0.00"),
        "commission_rate_lv1": Decimal("0.00"),
        "commission_rate_lv2": Decimal("0.00"),
        "discount": Decimal("1.00"),
        "sort": 10,
    },
    {
        "name": "青铜会员",
        "upgrade_amount": Decimal("500.00"),
        "team_upgrade_amount": Decimal("0.00"),
        "commission_rate_lv1": Decimal("0.00"),
        "commission_rate_lv2": Decimal("0.00"),
        "discount": Decimal("0.95"),
        "sort": 20,
    },
    {
        "name": "白银会员",
        "upgrade_amount": Decimal("2000.00"),
        "team_upgrade_amount": Decimal("0.00"),
        "commission_rate_lv1": Decimal("10.00"),
        "commission_rate_lv2": Decimal("5.00"),
        "discount": Decimal("0.90"),
        "sort": 30,
    },
    {
        "name": "黄金会员",
        "upgrade_amount": Decimal("2000.00"),
        "team_upgrade_amount": Decimal("10000.00"),
        "commission_rate_lv1": Decimal("15.00"),
        "commission_rate_lv2": Decimal("8.00"),
        "discount": Decimal("0.85"),
        "sort": 40,
    },
    {
        "name": "钻石会员",
        "upgrade_amount": Decimal("2000.00"),
        "team_upgrade_amount": Decimal("50000.00"),
        "commission_rate_lv1": Decimal("20.00"),
        "commission_rate_lv2": Decimal("10.00"),
        "discount": Decimal("0.80"),
        "sort": 50,
    },
]

CATEGORY_TREE = [
    ("服饰鞋包", [("女装", ["T恤", "连衣裙", "牛仔裤"]), ("男装", []), ("鞋靴", [])]),
    ("美妆个护", [("护肤", []), ("彩妆", []), ("洗护", [])]),
    ("食品饮料", []),
    ("家居日用", []),
    ("数码家电", []),
]

SPEC_TEMPLATES = [
    {"name": "颜色/尺寸", "spec_names": ["颜色", "尺寸"]},
    {"name": "套餐/容量", "spec_names": ["套餐", "容量"]},
]

DEMO_ACCOUNTS = [
    {
        "username": "demo_admin",
        "password": "demoAdmin123456",
        "defaults": {
            "is_staff": True,
            "is_superuser": True,
            "role": User.Role.ADMIN,
            "nickname": "平台管理员",
            "mobile": "13800000000",
        },
    },
    {
        "username": "demo_buyer",
        "password": "demo123456",
        "defaults": {
            "is_staff": False,
            "is_superuser": False,
            "role": User.Role.NORMAL,
            "nickname": "测试买家",
            "mobile": "13900000000",
        },
    },
]


class Command(BaseCommand):
    help = "Seed baseline mall data without using Django admin."

    def handle(self, *args, **options):
        with transaction.atomic():
            level_count = self.seed_member_levels()
            config_count = self.seed_distribution_config()
            category_count = self.seed_categories()
            template_count = self.seed_spec_templates()
            account_count = self.seed_demo_accounts()
            menu_count = self.seed_admin_menus()

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: "
                f"{level_count} member levels, "
                f"{config_count} distribution configs, "
                f"{category_count} categories, "
                f"{template_count} spec templates, "
                f"{account_count} demo accounts, "
                f"{menu_count} admin menus."
            )
        )

    def seed_member_levels(self):
        count = 0
        for item in MEMBER_LEVELS:
            _, created = MemberLevel.objects.update_or_create(
                name=item["name"],
                defaults={
                    "upgrade_amount": item["upgrade_amount"],
                    "team_upgrade_amount": item["team_upgrade_amount"],
                    "commission_rate_lv1": item["commission_rate_lv1"],
                    "commission_rate_lv2": item["commission_rate_lv2"],
                    "discount": item["discount"],
                    "sort": item["sort"],
                },
            )
            count += int(created)
        return count

    def seed_distribution_config(self):
        _, created = DistributionConfigModel.objects.update_or_create(
            name="平台默认配置",
            defaults={
                "default_rate_lv1": Decimal("10.00"),
                "default_rate_lv2": Decimal("5.00"),
                "settlement_delay_days": 7,
                "enabled": True,
            },
        )
        return int(created)

    def seed_categories(self):
        count = 0
        for root_index, (root_name, children) in enumerate(CATEGORY_TREE, start=1):
            root, created = self.upsert_category(root_name, None, 1, root_index * 10)
            count += int(created)
            for child_index, child in enumerate(children, start=1):
                child_name, grandchildren = child
                second, created = self.upsert_category(child_name, root, 2, child_index * 10)
                count += int(created)
                for grand_index, grand_name in enumerate(grandchildren, start=1):
                    _, created = self.upsert_category(grand_name, second, 3, grand_index * 10)
                    count += int(created)
        return count

    def upsert_category(self, name, parent, level, sort):
        category, created = ProductCategory.objects.update_or_create(
            name=name,
            parent=parent,
            defaults={
                "level": level,
                "sort": sort,
                "path": self.category_path(parent),
                "is_show": True,
                "is_distribution": True,
                "is_active": True,
            },
        )
        expected_path = self.category_path(parent)
        if category.path != expected_path or category.level != level:
            category.path = expected_path
            category.level = level
            category.save(update_fields=["path", "level", "updated_at"])
        return category, created

    def category_path(self, parent):
        if not parent:
            return ""
        return f"{parent.path or ','}{parent.pk},"

    def seed_spec_templates(self):
        count = 0
        for item in SPEC_TEMPLATES:
            _, created = SpecTemplate.objects.update_or_create(
                name=item["name"],
                defaults={"spec_names": item["spec_names"]},
            )
            count += int(created)
        return count

    def seed_demo_accounts(self):
        count = 0
        for item in DEMO_ACCOUNTS:
            user, created = User.objects.get_or_create(username=item["username"])
            user.is_staff = item["defaults"]["is_staff"]
            user.is_superuser = item["defaults"]["is_superuser"]
            user.role = item["defaults"]["role"]
            user.nickname = item["defaults"]["nickname"]
            user.mobile = item["defaults"]["mobile"]
            user.is_active = True
            user.set_password(item["password"])
            user.save()
            count += int(created)
        return count

    def seed_admin_menus(self):
        count = 0
        for section in ADMIN_MENU:
            parent, created = AdminMenu.objects.update_or_create(
                code=section["code"],
                defaults={
                    "parent": None,
                    "name": section["name"],
                    "icon": section.get("icon", ""),
                    "path": "",
                    "component": "",
                    "permission": "",
                    "sort": section.get("sort", 0),
                    "level": 1,
                    "is_show": True,
                },
            )
            count += int(created)
            for child in section.get("children", []):
                code = f'{section["code"]}:{child["path"]}'
                _, created = AdminMenu.objects.update_or_create(
                    code=code,
                    defaults={
                        "parent": parent,
                        "name": child["name"],
                        "icon": child.get("icon", ""),
                        "path": child.get("path", ""),
                        "component": child.get("component", ""),
                        "permission": child.get("permission", ""),
                        "sort": child.get("sort", 0),
                        "level": 2,
                        "is_show": True,
                    },
                )
                count += int(created)
        return count
