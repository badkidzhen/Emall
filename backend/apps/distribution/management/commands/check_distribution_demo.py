from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Sum

from apps.agents.models import CityAgent, CityAgentApplication
from apps.distribution.models import CommissionRecord, UserTeamStat
from apps.distribution.services import sync_user_team_stat
from apps.finance.models import Wallet
from apps.orders.models import Order
from apps.rewards.models import RewardDistributionRecord, RewardPool


DEMO_PREFIX = "dist_demo_"


class Command(BaseCommand):
    help = "Inspect and validate distribution demo data."

    def handle(self, *args, **options):
        User = get_user_model()
        users = {user.username: user for user in User.objects.filter(username__startswith=DEMO_PREFIX).select_related("parent", "level")}
        expected_users = [
            "dist_demo_leader",
            "dist_demo_direct_1",
            "dist_demo_indirect_1",
            "dist_demo_direct_2",
            "dist_demo_agent",
        ]

        failures = []
        missing = [username for username in expected_users if username not in users]
        if missing:
            failures.append(f"Missing demo users: {', '.join(missing)}")

        for user in users.values():
            sync_user_team_stat(user.id)

        orders = list(
            Order.objects.filter(
                user__username__startswith=DEMO_PREFIX,
                remark__startswith="distribution_demo:",
                status=Order.Status.COMPLETED,
            ).select_related("user")
        )
        commissions = list(
            CommissionRecord.objects.filter(order__in=orders).select_related("user", "source_user", "order")
        )
        total_order_amount = sum((order.pay_amount for order in orders), Decimal("0.00"))
        total_commission = sum((record.amount for record in commissions), Decimal("0.00"))

        if len(orders) < 3:
            failures.append("Expected at least 3 completed demo orders.")
        if len(commissions) < 4:
            failures.append("Expected at least 4 commission records.")

        self.stdout.write("Distribution demo check")
        self.stdout.write("=" * 72)
        self.stdout.write("")

        self.stdout.write("Users:")
        for username in expected_users:
            user = users.get(username)
            if not user:
                self.stdout.write(f"  {username:24s} MISSING")
                continue
            parent = user.parent.username if user.parent else "-"
            level = user.level.name if user.level else "-"
            self.stdout.write(
                f"  {username:24s} role={user.role:12s} parent={parent:24s} level={level}"
            )

        self.stdout.write("")
        self.stdout.write("Team stats:")
        for username in expected_users:
            user = users.get(username)
            if not user:
                continue
            stat = UserTeamStat.objects.filter(user=user).first()
            if not stat:
                self.stdout.write(f"  {username:24s} no stat")
                continue
            self.stdout.write(
                f"  {username:24s} team={stat.team_count:<3d} direct={stat.direct_count:<3d} "
                f"indirect={stat.indirect_count:<3d} team_amount={stat.team_order_amount} "
                f"commission={stat.team_commission}"
            )

        self.stdout.write("")
        self.stdout.write("Orders:")
        for order in orders:
            self.stdout.write(f"  {order.order_no} buyer={order.user.username:24s} amount={order.pay_amount}")
        self.stdout.write(f"  total_order_amount={total_order_amount}")

        self.stdout.write("")
        self.stdout.write("Commissions:")
        for record in commissions:
            self.stdout.write(
                f"  id={record.id:<4d} user={record.user.username:24s} source={record.source_user.username:24s} "
                f"level={record.level} rate={record.rate}% amount={record.amount} status={record.status}"
            )
        self.stdout.write(f"  total_commission={total_commission}")

        self.stdout.write("")
        self.stdout.write("Wallets:")
        for username in expected_users:
            user = users.get(username)
            if not user:
                continue
            wallet = Wallet.objects.filter(user=user).first()
            if wallet:
                self.stdout.write(
                    f"  {username:24s} balance={wallet.balance} frozen={wallet.frozen_balance} "
                    f"total_income={wallet.total_income}"
                )
            else:
                self.stdout.write(f"  {username:24s} no wallet")

        self.stdout.write("")
        self.stdout.write("City agent:")
        applications = CityAgentApplication.objects.filter(user__username__startswith=DEMO_PREFIX).select_related("user")
        agents = CityAgent.objects.filter(user__username__startswith=DEMO_PREFIX).select_related("user")
        for application in applications:
            self.stdout.write(
                f"  application id={application.id} user={application.user.username} "
                f"region={application.region_name} status={application.status}"
            )
        for agent in agents:
            self.stdout.write(
                f"  agent id={agent.id} user={agent.user.username} region={agent.region_name} "
                f"rate={agent.commission_rate}% enabled={agent.enabled}"
            )
        if not agents.exists():
            failures.append("Expected one approved city agent.")

        self.stdout.write("")
        self.stdout.write("Reward pool:")
        pool = RewardPool.objects.filter(name="分销测试奖励池").first()
        if pool:
            records = RewardDistributionRecord.objects.filter(pool=pool).select_related("user")
            self.stdout.write(f"  pool={pool.name} amount={pool.amount} records={records.count()}")
            for record in records:
                self.stdout.write(
                    f"  reward id={record.id:<4d} user={record.user.username:24s} "
                    f"score={record.score} amount={record.amount} status={record.status}"
                )
        else:
            self.stdout.write("  no demo reward pool, run seed_distribution_demo --reward to create one")

        self.stdout.write("")
        if failures:
            self.stdout.write(self.style.ERROR("FAIL"))
            for failure in failures:
                self.stdout.write(self.style.ERROR(f"  - {failure}"))
        else:
            self.stdout.write(self.style.SUCCESS("PASS: distribution demo data looks consistent."))
