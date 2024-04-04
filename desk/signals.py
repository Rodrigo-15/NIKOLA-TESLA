from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProcedureTracing, Procedure
from core.models import CargoArea
from core.serializers import AreaSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


@receiver(post_save, sender=ProcedureTracing)
def procedure_tracing_post_save(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                str(instance.user_id),
                {
                    "type": "desk_notification",
                    "message": True,
                },
            )
        except Exception as e:
            print(e)
    pass
