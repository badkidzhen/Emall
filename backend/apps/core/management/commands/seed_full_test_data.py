from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.agents.models import CityAgent, CityAgentApplication
from apps.catalog.models import Product, ProductCategory, ProductSku, StockLog
from apps.catalog.services import generate_product_skus
from apps.distribution.models import CommissionRecord, DistributionConfigModel
from apps.distribution.services import calculate_order_commission, sync_user_team_stat
from apps.finance.models import FundFlow, Wallet, WithdrawApplication
from apps.marketing.activity_models import ActivityPurchaseRecord
from apps.marketing.models import CouponTemplate, GroupBuyingActivity, SeckillActivity, UserCoupon
from apps.orders.models import (
    CartItem,
    InvoiceApplication,
    LogisticsRecord,
    Order,
    OrderAddress,
    OrderItem,
    PaymentRecord,
    RefundApplication,
)
from apps.rewards.models import RewardDistributionRecord, RewardPool, RewardPoolRule
from apps.users.models import MemberLevel, User


TEST_PREFIX = "test_"
TEST_PASSWORD = "test123456"


class Command(BaseCommand):
    help = "Seed comprehensive reusable test data for full mall testing."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=40, help="Number of test users to create.")
        parser.add_argument("--products", type=int, default=24, help="Number of test products to create.")
        parser.add_argument("--orders", type=int, default=80, help="Number of test orders to create.")

    def handle(self, *args, **options):
        user_count = max(options["users"], 20)
        product_count = max(options["products"], 12)
        order_count = max(options["orders"], 40)

        call_command("seed_initial_data", verbosity=0)

        with transaction.atomic():
            levels = self.ensure_levels()
            users = self.ensure_users(user_count, levels)
            self.ensure_user_tree(users)
            categories = self.ensure_categories()
            products = self.ensure_products(product_count, categories)
            skus = list(ProductSku.objects.filter(product__in=products, is_active=True).select_related("product"))
            self.ensure_addresses(users)
            self.ensure_carts(users, skus)
            coupons = self.ensure_marketing(users, products, skus, categories)
            orders = self.ensure_orders(order_count, users, skus)
            self.ensure_order_extensions(orders)
            self.ensure_activity_records(users, orders)
            self.ensure_commissions(orders)
            self.ensure_wallets(users)
            self.ensure_withdrawals(users)
            self.ensure_agents(users)
            self.ensure_rewards(users)
            self.sync_team_stats(users)

        self.stdout.write(self.style.SUCCESS("Full test data is ready."))
        self.stdout.write(f"Test user password: {TEST_PASSWORD}")
        self.stdout.write(f"Users: {len(users)}")
        self.stdout.write(f"Products: {len(products)}")
        self.stdout.write(f"SKUs: {ProductSku.objects.filter(product__in=products).count()}")
        self.stdout.write(f"Orders: {len(orders)}")
        self.stdout.write(f"Coupons: {len(coupons)} templates")
        self.stdout.write("")
        self.stdout.write("Useful accounts:")
        for username in ["test_admin", "test_leader_001", "test_agent_001", "test_buyer_001"]:
            self.stdout.write(f"  {username} / {TEST_PASSWORD}")

    def ensure_levels(self):
        specs = [
            ("测试普通会员", "0.00", "0.00", "0.00", "0.00", "1.00", 100),
            ("测试银牌分销", "1000.00", "3000.00", "8.00", "4.00", "0.95", 110),
            ("测试金牌分销", "3000.00", "10000.00", "12.00", "6.00", "0.90", 120),
            ("测试团队长", "8000.00", "30000.00", "18.00", "9.00", "0.85", 130),
            ("测试城市代理", "15000.00", "50000.00", "20.00", "10.00", "0.80", 140),
        ]
        levels = {}
        for name, upgrade, team_upgrade, lv1, lv2, discount, sort in specs:
            level, _ = MemberLevel.objects.update_or_create(
                name=name,
                defaults={
                    "upgrade_amount": Decimal(upgrade),
                    "team_upgrade_amount": Decimal(team_upgrade),
                    "commission_rate_lv1": Decimal(lv1),
                    "commission_rate_lv2": Decimal(lv2),
                    "discount": Decimal(discount),
                    "sort": sort,
                },
            )
            levels[name] = level
        DistributionConfigModel.objects.update_or_create(
            name="测试分销配置",
            defaults={
                "default_rate_lv1": Decimal("10.00"),
                "default_rate_lv2": Decimal("5.00"),
                "settlement_delay_days": 3,
                "enabled": True,
            },
        )
        return levels

    def ensure_users(self, count, levels):
        users = []
        specs = [
            ("test_admin", "测试管理员", "16690000000", User.Role.ADMIN, levels["测试城市代理"], True, True, True),
            ("test_leader_001", "测试团队长一号", "16690000001", User.Role.TEAM_LEADER, levels["测试团队长"], True, True, False),
            ("test_leader_002", "测试团队长二号", "16690000002", User.Role.TEAM_LEADER, levels["测试团队长"], True, True, False),
            ("test_agent_001", "测试城市代理一号", "16690000003", User.Role.CITY_AGENT, levels["测试城市代理"], True, True, False),
        ]
        role_cycle = [
            (User.Role.DISTRIBUTOR, levels["测试金牌分销"], True),
            (User.Role.DISTRIBUTOR, levels["测试银牌分销"], True),
            (User.Role.MEMBER, levels["测试普通会员"], False),
            (User.Role.NORMAL, None, False),
        ]
        for index in range(1, count - len(specs) + 1):
            role, level, is_distributor = role_cycle[(index - 1) % len(role_cycle)]
            specs.append(
                (
                    f"test_buyer_{index:03d}",
                    f"测试用户{index:03d}",
                    f"1669{index:07d}",
                    role,
                    level,
                    is_distributor,
                    False,
                    False,
                )
            )

        for username, nickname, mobile, role, level, is_distributor, is_verified, is_staff in specs:
            user, _ = User.objects.get_or_create(username=username)
            user.nickname = nickname
            user.mobile = self.available_mobile(mobile, user)
            user.role = role
            user.level = level
            user.is_distributor = is_distributor
            user.is_active = True
            user.is_staff = is_staff
            user.is_superuser = is_staff
            user.realname = f"{nickname}实名" if is_verified else ""
            user.id_card = f"11010119900101{user.id % 10000:04d}" if is_verified else ""
            user.realname_status = User.RealnameStatus.VERIFIED if is_verified else User.RealnameStatus.UNVERIFIED
            user.realname_verified_at = timezone.now() if is_verified else None
            user.openid = f"test_openid_{username}"
            user.set_password(TEST_PASSWORD)
            user.save()
            users.append(user)
        return users

    def available_mobile(self, mobile, user):
        if not User.objects.filter(mobile=mobile).exclude(pk=user.pk).exists():
            return mobile
        for suffix in range(1000, 9999):
            candidate = f"1668{suffix:07d}"[-11:]
            if not User.objects.filter(mobile=candidate).exclude(pk=user.pk).exists():
                return candidate
        return None

    def ensure_user_tree(self, users):
        leaders = [user for user in users if user.role == User.Role.TEAM_LEADER]
        agent = next((user for user in users if user.role == User.Role.CITY_AGENT), None)
        members = [user for user in users if user.username.startswith("test_buyer_")]
        roots = leaders + ([agent] if agent else [])
        for index, user in enumerate(members):
            parent = roots[index % len(roots)] if index < 18 else members[(index - 8) % max(len(members), 1)]
            if parent.id == user.id:
                parent = roots[0]
            user.bind_parent(parent)
            if user.role == User.Role.NORMAL:
                user.role = User.Role.MEMBER
            user.save(update_fields=["parent", "path", "role"])

    def ensure_categories(self):
        tree = [
            ("测试数码家电", ["摄影摄像", "智能穿戴", "电脑办公"]),
            ("测试美妆个护", ["面部护理", "彩妆香氛", "洗护清洁"]),
            ("测试食品生鲜", ["休闲零食", "冲调饮品", "粮油调味"]),
            ("测试家居生活", ["居家日用", "厨房用品", "收纳清洁"]),
            ("测试服饰鞋包", ["女装搭配", "男装运动", "箱包配饰"]),
        ]
        categories = []
        for root_index, (root_name, children) in enumerate(tree, start=1):
            root, _ = ProductCategory.objects.update_or_create(
                name=root_name,
                parent=None,
                defaults={"level": 1, "path": "", "sort": 900 - root_index, "is_show": True, "is_distribution": True},
            )
            categories.append(root)
            for child_index, child_name in enumerate(children, start=1):
                child, _ = ProductCategory.objects.update_or_create(
                    name=child_name,
                    parent=root,
                    defaults={
                        "level": 2,
                        "path": f"{root.path or ','}{root.id},",
                        "sort": 900 - child_index,
                        "is_show": True,
                        "is_distribution": True,
                    },
                )
                categories.append(child)
        return categories

    def ensure_products(self, count, categories):
        names = [
            "智能运动手表", "便携蓝牙音箱", "高清微单相机", "轻薄笔记本电脑", "氨基酸洁面乳", "玻尿酸精华液",
            "持久粉底液", "香氛洗护套装", "低脂坚果礼盒", "精品挂耳咖啡", "有机五谷杂粮", "厨房调味组合",
            "恒温电水壶", "多功能收纳箱", "抗菌毛巾套装", "轻量跑步鞋", "通勤双肩包", "防晒冰丝外套",
            "儿童学习台灯", "无线降噪耳机", "家用空气炸锅", "旅行拉杆箱", "护眼阅读灯", "保温杯礼盒",
        ]
        products = []
        for index in range(1, count + 1):
            base_price = Decimal("59.00") + Decimal(index * 18)
            product, _ = Product.objects.update_or_create(
                title=f"测试商品{index:03d}-{names[(index - 1) % len(names)]}",
                defaults={
                    "sub_title": f"用于功能联调的测试商品 {index:03d}",
                    "detail": "这是由 seed_full_test_data 自动生成的测试商品，覆盖普通购买、分销佣金、团购秒杀和售后流程。",
                    "sale_status": [Product.SaleStatus.ON_SALE, Product.SaleStatus.DRAFT, Product.SaleStatus.OFF_SALE][index % 3],
                    "price": base_price,
                    "market_price": base_price + Decimal("30.00"),
                    "total_stock": 0,
                    "is_distribution": index % 4 != 0,
                    "commission_type": "percent" if index % 5 else "fixed",
                    "commission_rate_lv1": Decimal("10.00") + Decimal(index % 5),
                    "commission_rate_lv2": Decimal("5.00") + Decimal(index % 3),
                    "is_active": True,
                },
            )
            product.categories.set([categories[index % len(categories)]])
            spec_options = self.product_spec_options(index)
            generate_product_skus(
                product.id,
                spec_options,
                defaults={
                    "price": base_price,
                    "market_price": base_price + Decimal("30.00"),
                    "stock": 80 + index * 3,
                    "warning_stock": 10,
                },
                overwrite=False,
            )
            products.append(product)
        return products

    def product_spec_options(self, index):
        if index % 3 == 0:
            return [{"name": "颜色", "values": ["曜石黑", "月光银", "珊瑚粉"]}, {"name": "套餐", "values": ["标准版", "礼盒版"]}]
        if index % 3 == 1:
            return [{"name": "规格", "values": ["小号", "中号", "大号"]}, {"name": "包装", "values": ["单件", "三件装"]}]
        return [{"name": "容量", "values": ["250ml", "500ml", "1L"]}, {"name": "口味", "values": ["原味", "清新款"]}]

    def ensure_addresses(self, users):
        for index, user in enumerate(users, start=1):
            for seq in range(1, 3):
                OrderAddress.objects.update_or_create(
                    user=user,
                    receiver_mobile=f"1398{index:04d}{seq:03d}",
                    defaults={
                        "receiver_name": user.nickname or user.username,
                        "province": "浙江省",
                        "city": "杭州市",
                        "district": "西湖区" if seq == 1 else "滨江区",
                        "address_detail": f"测试街道 {index} 号 {seq} 单元",
                        "postal_code": "310000",
                        "is_default": seq == 1,
                    },
                )

    def ensure_carts(self, users, skus):
        for index, user in enumerate(users[:20], start=1):
            for sku in skus[index:index + 2]:
                CartItem.objects.update_or_create(
                    user=user,
                    sku=sku,
                    defaults={"quantity": index % 3 + 1, "selected": index % 2 == 0},
                )

    def ensure_marketing(self, users, products, skus, categories):
        now = timezone.now()
        coupon_specs = [
            ("测试满100减20", CouponTemplate.CouponType.FULL_REDUCTION, "100.00", "20.00", "1.00"),
            ("测试新人立减15", CouponTemplate.CouponType.NEW_USER, "0.00", "15.00", "1.00"),
            ("测试九折券", CouponTemplate.CouponType.DISCOUNT, "50.00", "0.00", "0.90"),
            ("测试指定商品券", CouponTemplate.CouponType.PRODUCT, "80.00", "25.00", "1.00"),
            ("测试分类专享券", CouponTemplate.CouponType.CATEGORY, "120.00", "30.00", "1.00"),
        ]
        templates = []
        for index, (name, coupon_type, threshold, discount, rate) in enumerate(coupon_specs, start=1):
            template, _ = CouponTemplate.objects.update_or_create(
                name=name,
                defaults={
                    "coupon_type": coupon_type,
                    "threshold_amount": Decimal(threshold),
                    "discount_amount": Decimal(discount),
                    "discount_rate": Decimal(rate),
                    "total_quantity": 500,
                    "per_user_limit": 2,
                    "started_at": now - timezone.timedelta(days=3),
                    "ended_at": now + timezone.timedelta(days=30),
                    "valid_days": 15,
                },
            )
            if coupon_type == CouponTemplate.CouponType.PRODUCT:
                template.products.set(products[:5])
            if coupon_type == CouponTemplate.CouponType.CATEGORY:
                template.categories.set(categories[:3])
            templates.append(template)

        statuses = [UserCoupon.Status.UNUSED, UserCoupon.Status.USED, UserCoupon.Status.EXPIRED]
        for user_index, user in enumerate(users[:30], start=1):
            for template in templates[:3]:
                status = statuses[(user_index + template.id) % len(statuses)]
                UserCoupon.objects.update_or_create(
                    user=user,
                    template=template,
                    defaults={
                        "status": status,
                        "valid_from": now - timezone.timedelta(days=2),
                        "valid_to": now + timezone.timedelta(days=10) if status != UserCoupon.Status.EXPIRED else now - timezone.timedelta(days=1),
                        "used_at": now - timezone.timedelta(days=1) if status == UserCoupon.Status.USED else None,
                    },
                )

        for index, sku in enumerate(skus[:8], start=1):
            GroupBuyingActivity.objects.update_or_create(
                name=f"测试团购活动{index:02d}",
                defaults={
                    "sku": sku,
                    "group_price": max(sku.price - Decimal("10.00"), Decimal("1.00")),
                    "min_members": 2 + index % 4,
                    "stock": 50 + index * 5,
                    "started_at": now - timezone.timedelta(days=index % 3),
                    "ended_at": now + timezone.timedelta(days=10 + index),
                    "enabled": index % 5 != 0,
                },
            )
            SeckillActivity.objects.update_or_create(
                name=f"测试秒杀活动{index:02d}",
                defaults={
                    "sku": sku,
                    "seckill_price": max(sku.price - Decimal("20.00"), Decimal("1.00")),
                    "stock": 20 + index * 3,
                    "per_user_limit": 1 + index % 2,
                    "started_at": now - timezone.timedelta(hours=2),
                    "ended_at": now + timezone.timedelta(days=3),
                    "enabled": index % 4 != 0,
                },
            )
        return templates

    def ensure_orders(self, count, users, skus):
        statuses = [
            Order.Status.PENDING_PAYMENT,
            Order.Status.PENDING_SHIPMENT,
            Order.Status.PENDING_RECEIPT,
            Order.Status.COMPLETED,
            Order.Status.REFUNDING,
            Order.Status.REFUNDED,
            Order.Status.CLOSED,
        ]
        orders = []
        buyers = [user for user in users if not user.is_staff]
        for index in range(1, count + 1):
            user = buyers[index % len(buyers)]
            sku = skus[index % len(skus)]
            quantity = index % 3 + 1
            total = sku.price * quantity
            discount = Decimal("10.00") if index % 6 == 0 else Decimal("0.00")
            pay_amount = max(total - discount, Decimal("0.00"))
            status = statuses[(index - 1) % len(statuses)]
            paid_at = timezone.now() - timezone.timedelta(days=index % 20) if status not in {Order.Status.PENDING_PAYMENT, Order.Status.CLOSED} else None
            completed_at = timezone.now() - timezone.timedelta(days=index % 8) if status in {Order.Status.COMPLETED, Order.Status.REFUNDED} else None
            order, _ = Order.objects.update_or_create(
                order_no=f"TESTORDER{index:05d}",
                defaults={
                    "user": user,
                    "status": status,
                    "total_amount": total,
                    "discount_amount": discount,
                    "pay_amount": pay_amount,
                    "paid_at": paid_at,
                    "completed_at": completed_at,
                    "remark": f"全流程测试订单 {index}",
                    "receiver_name": user.nickname or user.username,
                    "receiver_mobile": user.mobile or "13900000000",
                    "province": "浙江省",
                    "city": "杭州市",
                    "district": "西湖区",
                    "address_detail": f"测试收货地址 {index} 号",
                    "postal_code": "310000",
                },
            )
            OrderItem.objects.update_or_create(
                order=order,
                sku=sku,
                defaults={
                    "product": sku.product,
                    "product_title": sku.product.title,
                    "sku_code": sku.sku_code,
                    "spec_json": sku.specs,
                    "price": sku.price,
                    "quantity": quantity,
                    "total_amount": total,
                },
            )
            if status not in {Order.Status.PENDING_PAYMENT, Order.Status.CLOSED}:
                PaymentRecord.objects.update_or_create(
                    payment_no=f"TESTPAY{index:05d}",
                    defaults={
                        "order": order,
                        "channel": PaymentRecord.Channel.MOCK if index % 3 else PaymentRecord.Channel.WECHAT,
                        "amount": pay_amount,
                        "status": PaymentRecord.Status.SUCCESS,
                        "gateway_trade_no": f"MOCKTRADE{index:05d}",
                        "paid_at": paid_at or timezone.now(),
                        "raw_payload": {"seed": "seed_full_test_data", "index": index},
                    },
                )
            orders.append(order)
        return orders

    def ensure_order_extensions(self, orders):
        now = timezone.now()
        for index, order in enumerate(orders, start=1):
            if order.status in {Order.Status.PENDING_RECEIPT, Order.Status.COMPLETED}:
                LogisticsRecord.objects.update_or_create(
                    order=order,
                    defaults={
                        "company": ["顺丰速运", "中通快递", "京东物流"][index % 3],
                        "tracking_no": f"TESTLOG{index:08d}",
                        "shipped_at": now - timezone.timedelta(days=2),
                        "delivered_at": now - timezone.timedelta(days=1) if order.status == Order.Status.COMPLETED else None,
                        "traces": [
                            {"time": "2026-07-20 09:00", "text": "测试包裹已揽收"},
                            {"time": "2026-07-21 12:30", "text": "测试包裹运输中"},
                        ],
                        "raw_payload": {"seed": "seed_full_test_data"},
                    },
                )
            if order.status != Order.Status.PENDING_PAYMENT and index % 5 == 0:
                invoice_status = [InvoiceApplication.Status.PENDING, InvoiceApplication.Status.ISSUED, InvoiceApplication.Status.REJECTED][index % 3]
                InvoiceApplication.objects.update_or_create(
                    order=order,
                    defaults={
                        "user": order.user,
                        "invoice_type": InvoiceApplication.InvoiceType.COMPANY if index % 2 else InvoiceApplication.InvoiceType.PERSONAL,
                        "title": f"测试发票抬头{index}",
                        "tax_no": f"TESTTAX{index:05d}",
                        "email": f"invoice{index}@example.com",
                        "content": "商品明细",
                        "amount": order.pay_amount,
                        "status": invoice_status,
                        "audit_remark": "测试发票数据",
                        "issued_at": now if invoice_status == InvoiceApplication.Status.ISSUED else None,
                    },
                )
            if order.status in {Order.Status.REFUNDING, Order.Status.REFUNDED}:
                refund_status = RefundApplication.Status.REFUNDED if order.status == Order.Status.REFUNDED else RefundApplication.Status.PENDING
                RefundApplication.objects.update_or_create(
                    refund_no=f"TESTRF{index:05d}",
                    defaults={
                        "order": order,
                        "user": order.user,
                        "refund_type": RefundApplication.RefundType.RETURN_AND_REFUND if index % 2 else RefundApplication.RefundType.REFUND_ONLY,
                        "reason": "测试售后申请",
                        "amount": min(order.pay_amount, Decimal("50.00")),
                        "status": refund_status,
                        "audit_remark": "测试售后审核备注",
                        "gateway_refund_no": f"MOCKRF{index:05d}" if refund_status == RefundApplication.Status.REFUNDED else "",
                        "requested_at": now - timezone.timedelta(days=1),
                        "refunded_at": now if refund_status == RefundApplication.Status.REFUNDED else None,
                        "raw_payload": {"seed": "seed_full_test_data"},
                    },
                )

    def ensure_activity_records(self, users, orders):
        group_ids = list(GroupBuyingActivity.objects.values_list("id", flat=True)[:8])
        seckill_ids = list(SeckillActivity.objects.values_list("id", flat=True)[:8])
        paid_orders = [order for order in orders if order.status != Order.Status.PENDING_PAYMENT]
        for index, order in enumerate(paid_orders[:20], start=1):
            activity_type = ActivityPurchaseRecord.ActivityType.GROUP if index % 2 else ActivityPurchaseRecord.ActivityType.SECKILL
            activity_ids = group_ids if activity_type == ActivityPurchaseRecord.ActivityType.GROUP else seckill_ids
            if not activity_ids:
                continue
            ActivityPurchaseRecord.objects.update_or_create(
                user=order.user,
                order=order,
                activity_type=activity_type,
                defaults={"activity_id": activity_ids[index % len(activity_ids)], "quantity": index % 3 + 1},
            )

    def ensure_commissions(self, orders):
        for order in orders:
            if order.status == Order.Status.COMPLETED:
                calculate_order_commission(order.id)
        records = CommissionRecord.objects.filter(order__order_no__startswith="TESTORDER").order_by("id")
        for index, record in enumerate(records, start=1):
            record.status = [CommissionRecord.Status.FROZEN, CommissionRecord.Status.SETTLED, CommissionRecord.Status.CANCELED][index % 3]
            if record.status == CommissionRecord.Status.SETTLED:
                record.settle_at = timezone.now() - timezone.timedelta(days=1)
            record.save(update_fields=["status", "settle_at", "updated_at"])

    def ensure_wallets(self, users):
        flow_types = [FundFlow.FlowType.INCOME, FundFlow.FlowType.ADJUST, FundFlow.FlowType.FREEZE, FundFlow.FlowType.WITHDRAW]
        for index, user in enumerate(users, start=1):
            wallet, _ = Wallet.objects.update_or_create(
                user=user,
                defaults={
                    "balance": Decimal("100.00") + Decimal(index * 13),
                    "frozen_balance": Decimal(index % 5 * 10),
                    "total_income": Decimal("300.00") + Decimal(index * 20),
                    "total_withdraw": Decimal(index % 4 * 30),
                },
            )
            for seq in range(1, 4):
                FundFlow.objects.update_or_create(
                    user=user,
                    wallet=wallet,
                    biz_type="seed_full_test_data",
                    biz_id=f"{user.id}-{seq}",
                    defaults={
                        "flow_type": flow_types[(index + seq) % len(flow_types)],
                        "amount": Decimal(seq * 10 + index),
                        "balance_after": wallet.balance,
                        "remark": f"测试资金流水 {seq}",
                    },
                )

    def ensure_withdrawals(self, users):
        statuses = [
            WithdrawApplication.Status.PENDING,
            WithdrawApplication.Status.APPROVED,
            WithdrawApplication.Status.PAYING,
            WithdrawApplication.Status.REJECTED,
            WithdrawApplication.Status.PAID,
        ]
        channels = [WithdrawApplication.Channel.MANUAL, WithdrawApplication.Channel.WECHAT, WithdrawApplication.Channel.BANK]
        for index, user in enumerate(users[:20], start=1):
            status = statuses[index % len(statuses)]
            WithdrawApplication.objects.update_or_create(
                account_no=f"TEST-WITHDRAW-{index:05d}",
                defaults={
                    "user": user,
                    "amount": Decimal("20.00") + Decimal(index * 3),
                    "channel": channels[index % len(channels)],
                    "account_name": user.nickname or user.username,
                    "status": status,
                    "audit_remark": "测试提现申请",
                    "audited_at": timezone.now() if status != WithdrawApplication.Status.PENDING else None,
                    "payout_no": f"TESTPAYOUT{index:05d}" if status in {WithdrawApplication.Status.PAYING, WithdrawApplication.Status.PAID} else "",
                    "paid_at": timezone.now() if status == WithdrawApplication.Status.PAID else None,
                    "raw_payload": {"seed": "seed_full_test_data"},
                },
            )

    def ensure_agents(self, users):
        candidates = users[3:15]
        statuses = [CityAgentApplication.Status.PENDING, CityAgentApplication.Status.APPROVED, CityAgentApplication.Status.REJECTED]
        for index, user in enumerate(candidates, start=1):
            status = statuses[index % len(statuses)]
            app, _ = CityAgentApplication.objects.update_or_create(
                user=user,
                region_code=f"3301{index:02d}",
                defaults={
                    "level": index % 3 + 1,
                    "region_name": f"测试代理区域{index:02d}",
                    "contact_name": user.nickname or user.username,
                    "contact_phone": user.mobile or f"1388{index:07d}",
                    "status": status,
                    "audit_remark": "测试代理申请",
                },
            )
            if status == CityAgentApplication.Status.APPROVED:
                CityAgent.objects.update_or_create(
                    level=app.level,
                    region_code=app.region_code,
                    defaults={
                        "user": user,
                        "region_name": app.region_name,
                        "commission_rate": Decimal("3.00") + Decimal(index),
                        "enabled": True,
                    },
                )

    def ensure_rewards(self, users):
        pool_specs = [
            ("测试平台全局池", RewardPool.PoolType.GLOBAL, "10000.00"),
            ("测试团队长池", RewardPool.PoolType.TEAM_LEADER, "6000.00"),
            ("测试城市代理池", RewardPool.PoolType.CITY_AGENT, "5000.00"),
            ("测试月度争霸池", RewardPool.PoolType.MONTHLY, "8000.00"),
        ]
        for pool_index, (name, pool_type, amount) in enumerate(pool_specs, start=1):
            pool, _ = RewardPool.objects.update_or_create(
                name=name,
                defaults={
                    "pool_type": pool_type,
                    "amount": Decimal(amount),
                    "min_performance": Decimal("100.00"),
                    "max_user_ratio": Decimal("35.00"),
                    "enabled": True,
                },
            )
            RewardPoolRule.objects.update_or_create(
                pool=pool,
                defaults={
                    "team_amount_weight": Decimal("0.50"),
                    "team_count_weight": Decimal("0.20"),
                    "personal_amount_weight": Decimal("0.30"),
                    "rank_config": {"top1": "30%", "top2_3": "20%", "others": "50%"},
                },
            )
            for user_index, user in enumerate(users[1:10], start=1):
                status = [RewardDistributionRecord.Status.PENDING, RewardDistributionRecord.Status.PAID, RewardDistributionRecord.Status.CANCELED][(pool_index + user_index) % 3]
                RewardDistributionRecord.objects.update_or_create(
                    pool=pool,
                    user=user,
                    defaults={
                        "score": Decimal(1000 - user_index * 37),
                        "amount": Decimal("100.00") + Decimal(pool_index * user_index * 15),
                        "status": status,
                        "distributed_at": timezone.now() if status == RewardDistributionRecord.Status.PAID else None,
                    },
                )

    def sync_team_stats(self, users):
        for user in users:
            try:
                sync_user_team_stat(user.id)
            except User.DoesNotExist:
                continue
