from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.agents.models import CityAgentApplication
from apps.agents.services import approve_application
from apps.catalog.models import Product, ProductCategory, ProductSku
from apps.distribution.models import CommissionRecord, DistributionConfigModel, UserTeamStat
from apps.distribution.services import bind_parent, sync_user_team_stat
from apps.finance.services import add_income, get_wallet
from apps.orders.models import Order
from apps.orders.services import complete_order, confirm_order_paid, create_order
from apps.rewards.models import RewardDistributionRecord, RewardPool, RewardPoolRule
from apps.rewards.services import distribute_pool, mark_pool_records_paid
from apps.users.models import MemberLevel


DEMO_PASSWORD = "demo123456"
DEMO_PREFIX = "dist_demo_"


class Command(BaseCommand):
    help = "Create reusable demo data for distribution, team, city agent and reward testing."

    def add_arguments(self, parser):
        parser.add_argument("--quantity", type=int, default=1, help="Quantity per demo order.")
        parser.add_argument("--settle", action="store_true", help="Settle demo commissions into wallets.")
        parser.add_argument("--reward", action="store_true", help="Distribute and pay a demo reward pool.")

    def handle(self, *args, **options):
        quantity = max(options["quantity"], 1)

        with transaction.atomic():
            levels = self.ensure_levels()
            users = self.ensure_users(levels)
            self.ensure_parent(users["direct_1"], users["leader"])
            self.ensure_parent(users["indirect_1"], users["direct_1"])
            self.ensure_parent(users["direct_2"], users["leader"])
            self.ensure_parent(users["agent"], users["leader"])
            self.ensure_distribution_config()
            sku = self.ensure_product()
            agent = self.ensure_city_agent(users["agent"])

        orders = self.ensure_demo_orders(users, sku, quantity)
        commissions = self.get_demo_commissions(orders)

        if options["settle"]:
            settled_count = self.settle_demo_commissions(commissions)
        else:
            settled_count = 0

        reward_records = []
        if options["reward"]:
            reward_records = self.ensure_reward_pool_paid()

        for user in users.values():
            sync_user_team_stat(user.id)
            get_wallet(user)

        self.stdout.write(self.style.SUCCESS("Distribution demo data is ready."))
        self.stdout.write(f"Password for all demo users: {DEMO_PASSWORD}")
        self.stdout.write("")
        self.stdout.write("Demo users:")
        for key, user in users.items():
            parent_name = user.parent.username if user.parent else "-"
            self.stdout.write(f"  {key:10s} {user.username:22s} role={user.role:12s} parent={parent_name}")

        self.stdout.write("")
        self.stdout.write(f"Demo SKU: {sku.id} / {sku.sku_code} / price={sku.price} / stock={sku.stock}")
        self.stdout.write(f"City agent: {agent.region_name} ({agent.region_code}) rate={agent.commission_rate}%")
        self.stdout.write(f"Completed demo orders: {len(orders)}")
        self.stdout.write(f"Demo commission records: {len(commissions)}")
        if options["settle"]:
            self.stdout.write(f"Settled demo commission records: {settled_count}")
        if options["reward"]:
            self.stdout.write(f"Reward records: {len(reward_records)}")

        self.stdout.write("")
        self.stdout.write("Run this to inspect the result:")
        self.stdout.write("  .\\.venv\\Scripts\\python.exe backend\\manage.py check_distribution_demo")

    def ensure_levels(self):
        leader, _ = MemberLevel.objects.update_or_create(
            name="Demo Leader Level",
            defaults={
                "upgrade_amount": Decimal("0.00"),
                "team_upgrade_amount": Decimal("0.00"),
                "commission_rate_lv1": Decimal("20.00"),
                "commission_rate_lv2": Decimal("10.00"),
                "discount": Decimal("0.85"),
                "sort": 900,
            },
        )
        distributor, _ = MemberLevel.objects.update_or_create(
            name="Demo Distributor Level",
            defaults={
                "upgrade_amount": Decimal("0.00"),
                "team_upgrade_amount": Decimal("0.00"),
                "commission_rate_lv1": Decimal("10.00"),
                "commission_rate_lv2": Decimal("5.00"),
                "discount": Decimal("0.90"),
                "sort": 890,
            },
        )
        return {"leader": leader, "distributor": distributor}

    def ensure_users(self, levels):
        User = get_user_model()
        specs = {
            "leader": {
                "username": f"{DEMO_PREFIX}leader",
                "mobile": "15100000001",
                "nickname": "分销测试团队长",
                "role": User.Role.TEAM_LEADER,
                "level": levels["leader"],
                "is_distributor": True,
            },
            "direct_1": {
                "username": f"{DEMO_PREFIX}direct_1",
                "mobile": "15100000002",
                "nickname": "分销测试直推1",
                "role": User.Role.DISTRIBUTOR,
                "level": levels["distributor"],
                "is_distributor": True,
            },
            "indirect_1": {
                "username": f"{DEMO_PREFIX}indirect_1",
                "mobile": "15100000003",
                "nickname": "分销测试间推1",
                "role": User.Role.MEMBER,
                "level": None,
                "is_distributor": False,
            },
            "direct_2": {
                "username": f"{DEMO_PREFIX}direct_2",
                "mobile": "15100000004",
                "nickname": "分销测试直推2",
                "role": User.Role.MEMBER,
                "level": None,
                "is_distributor": False,
            },
            "agent": {
                "username": f"{DEMO_PREFIX}agent",
                "mobile": "15100000005",
                "nickname": "分销测试城市代理",
                "role": User.Role.CITY_AGENT,
                "level": levels["distributor"],
                "is_distributor": True,
            },
        }

        users = {}
        for key, data in specs.items():
            user, _ = User.objects.get_or_create(username=data["username"])
            user.mobile = data["mobile"]
            user.nickname = data["nickname"]
            user.role = data["role"]
            user.level = data["level"]
            user.is_distributor = data["is_distributor"]
            user.is_active = True
            user.realname = data["nickname"]
            user.id_card = f"1101011990010{len(users) + 1:02d}1234"
            user.realname_status = User.RealnameStatus.VERIFIED
            user.realname_verified_at = user.realname_verified_at or timezone.now()
            user.set_password(DEMO_PASSWORD)
            user.save()
            users[key] = user
        return users

    def ensure_parent(self, user, parent):
        if user.parent_id == parent.id and f",{parent.id}," in (user.path or ""):
            return
        bind_parent(user.id, parent.id)
        user.refresh_from_db()

    def ensure_distribution_config(self):
        DistributionConfigModel.objects.update_or_create(
            name="Demo Distribution Config",
            defaults={
                "default_rate_lv1": Decimal("10.00"),
                "default_rate_lv2": Decimal("5.00"),
                "settlement_delay_days": 0,
                "enabled": True,
            },
        )

    def ensure_product(self):
        category, _ = ProductCategory.objects.update_or_create(
            name="分销测试分类",
            parent=None,
            defaults={
                "sort": 880,
                "level": 1,
                "path": "",
                "is_show": True,
                "is_distribution": True,
                "is_active": True,
            },
        )
        product_obj, _ = Product.objects.update_or_create(
            title="分销测试商品",
            defaults={
                "sub_title": "用于团队、佣金、代理测试",
                "detail": "该商品由 seed_distribution_demo 命令自动创建。",
                "sale_status": Product.SaleStatus.ON_SALE,
                "price": Decimal("100.00"),
                "market_price": Decimal("129.00"),
                "total_stock": 1000,
                "is_distribution": True,
                "commission_type": "rate",
                "commission_rate_lv1": Decimal("10.00"),
                "commission_rate_lv2": Decimal("5.00"),
                "is_active": True,
            },
        )
        product_obj.categories.set([category])
        sku, _ = ProductSku.objects.update_or_create(
            product=product_obj,
            sku_code="DIST-DEMO-SKU",
            defaults={
                "specs": {"规格": "标准版"},
                "price": Decimal("100.00"),
                "market_price": Decimal("129.00"),
                "stock": 1000,
                "locked_stock": 0,
                "warning_stock": 10,
                "is_active": True,
            },
        )
        product_obj.total_stock = product_obj.skus.filter(is_active=True).count() * 1000
        product_obj.price = sku.price
        product_obj.save(update_fields=["total_stock", "price", "updated_at"])
        return sku

    def ensure_city_agent(self, user):
        application, created = CityAgentApplication.objects.get_or_create(
            user=user,
            region_code="330100",
            defaults={
                "level": 2,
                "region_name": "杭州市",
                "contact_name": user.nickname,
                "contact_phone": user.mobile,
            },
        )
        if not created and application.status == CityAgentApplication.Status.REJECTED:
            application.status = CityAgentApplication.Status.PENDING
            application.audit_remark = ""
            application.save(update_fields=["status", "audit_remark", "updated_at"])
        if application.status == CityAgentApplication.Status.PENDING:
            return approve_application(application.id, commission_rate=Decimal("3.00"), remark="demo approved")
        from apps.agents.models import CityAgent

        return CityAgent.objects.get(level=application.level, region_code=application.region_code)

    def ensure_demo_orders(self, users, sku, quantity):
        buyers = [users["direct_1"], users["indirect_1"], users["direct_2"]]
        orders = []
        for buyer in buyers:
            remark = f"distribution_demo:{buyer.username}"
            order = Order.objects.filter(user=buyer, remark=remark, status=Order.Status.COMPLETED).order_by("-id").first()
            if not order:
                order = create_order(
                    user=buyer,
                    items=[{"sku_id": sku.id, "quantity": quantity}],
                    address={
                        "receiver_name": buyer.nickname,
                        "receiver_mobile": buyer.mobile,
                        "province": "浙江省",
                        "city": "杭州市",
                        "district": "西湖区",
                        "address_detail": "分销测试地址",
                    },
                    remark=remark,
                )
                confirm_order_paid(
                    order.id,
                    payment_no=f"DEMO-PAY-{order.order_no}",
                    paid_amount=order.pay_amount,
                    raw_payload={"provider": "demo"},
                )
                complete_order(order.id)
                order.refresh_from_db()
            orders.append(order)
        return orders

    def get_demo_commissions(self, orders):
        return list(CommissionRecord.objects.filter(order__in=orders).select_related("user", "source_user", "order"))

    def settle_demo_commissions(self, commissions):
        settled_count = 0
        with transaction.atomic():
            for record in CommissionRecord.objects.select_for_update().filter(
                id__in=[item.id for item in commissions],
                status=CommissionRecord.Status.FROZEN,
            ):
                record.status = CommissionRecord.Status.SETTLED
                record.settle_at = timezone.now()
                record.save(update_fields=["status", "settle_at", "updated_at"])
                add_income(
                    record.user,
                    record.amount,
                    biz_type="commission",
                    biz_id=record.id,
                    remark=f"demo_order:{record.order_id}",
                )
                settled_count += 1
        return settled_count

    def ensure_reward_pool_paid(self):
        pool, _ = RewardPool.objects.update_or_create(
            name="分销测试奖励池",
            defaults={
                "pool_type": RewardPool.PoolType.TEAM_LEADER,
                "amount": Decimal("300.00"),
                "min_performance": Decimal("1.00"),
                "max_user_ratio": Decimal("80.00"),
                "enabled": True,
            },
        )
        RewardPoolRule.objects.update_or_create(
            pool=pool,
            defaults={
                "team_amount_weight": Decimal("0.50"),
                "team_count_weight": Decimal("0.20"),
                "personal_amount_weight": Decimal("0.30"),
                "rank_config": {"demo": True},
            },
        )
        if not RewardDistributionRecord.objects.filter(pool=pool).exists():
            distribute_pool(pool.id)
        mark_pool_records_paid(pool.id)
        return list(RewardDistributionRecord.objects.filter(pool=pool).select_related("user"))
