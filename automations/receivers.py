from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from automations.const import TriggerType
from automations.models import Automation
from core.models import QuizRecord
from shop.models import Order, ServiceOrder, ProductOrder
from users.models import ShopUser


@receiver(post_save, sender=ShopUser)
def new_user_created(sender, instance, created, **kwargs):
    if created and not (instance.is_staff or instance.is_superuser):
        new_user_automations = Automation.objects.filter(
            trigger__trigger_type=TriggerType.NEW_USER, is_active=True
        )
        for automation in new_user_automations:
            for action in automation.actions.filter(is_active=True):
                action.run(trigger_data={"user": instance, "recipients": [instance.email]})


@receiver(pre_save, sender=ServiceOrder)
@receiver(pre_save, sender=ProductOrder)
def new_order_created(sender, instance, **kwargs):
    if instance.billing_address:
        current_instance = sender.objects.filter(id=instance.id).first()
        current_billing_address = None
        if current_instance:
            current_billing_address = current_instance.billing_address

        if not current_billing_address:
            new_order_automations = Automation.objects.filter(
                trigger__trigger_type=TriggerType.NEW_ORDER
            )
            for automation in new_order_automations:
                for action in automation.actions.filter(is_active=True):
                    action.run(trigger_data={"order": instance, "recipients": [instance.billing_address.email]})


@receiver(post_save, sender=QuizRecord)
def new_quiz_record(sender, instance, created, **kwargs):
    if created:
        new_quiz_record_automations = Automation.objects.filter(trigger__trigger_type=TriggerType.NEW_QUIZ_RECORD,
                                                                is_active=True)
        for automation in new_quiz_record_automations:
            for action in automation.actions.filter(is_active=True):
                action.run(trigger_data={"data": instance, "recipients": [instance.email]})
