from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from automations.const import TriggerType
from automations.models import Automation
from core.models import QuizRecord
from shop.models import Order
from users.models import ShopUser


@receiver(post_save, sender=ShopUser)
def new_user_created(sender, instance, created, **kwargs):
    if created and not (instance.is_staff or instance.is_superuser):
        new_user_automations = Automation.objects.filter(
            trigger__trigger_type=TriggerType.NEW_USER, is_active=True
        )
        for automation in new_user_automations:
            for action in automation.actions.filter(is_active=True):
                action.run(
                    trigger_data={
                        "user": instance,
                        "recipients": [instance.email],
                    }
                )


@receiver(post_save, sender=Order)
def new_order_created(sender, instance, created, **kwargs):
    # We have to assure there are some items already in order to have data to use
    if instance.items.exists() and not instance.post_save_triggered:
        new_order_automations = Automation.objects.filter(
            Q(trigger__trigger_type=TriggerType.NEW_ORDER)
            & (
                (Q(trigger__products=None))
                | Q(
                    trigger__products__in=[
                        item.product for item in instance.items.all()
                    ]
                )
            )
        )
        for automation in new_order_automations:
            for action in automation.actions.filter(is_active=True):
                action.run(
                    trigger_data={
                        "order": instance,
                        "recipients": [instance.billing_address.email],
                    }
                )

        instance.post_save_triggered = True


@receiver(post_save, sender=QuizRecord)
def new_quiz_record(sender, instance, created, **kwargs):
    if created:
        new_quiz_record_automations = Automation.objects.filter(
            trigger__trigger_type=TriggerType.NEW_QUIZ_RECORD, is_active=True
        )
        for automation in new_quiz_record_automations:
            for action in automation.actions.filter(is_active=True):
                action.run(
                    trigger_data={
                        "data": instance,
                        "recipients": [instance.email],
                    }
                )
