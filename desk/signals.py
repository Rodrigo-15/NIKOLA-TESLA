from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProcedureTracing, Procedure
from core.models import CargoArea, Area
from core.serializers import AreaSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


@receiver(post_save, sender=ProcedureTracing)
def procedure_tracing_post_save(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if instance.to_area_id and not instance.assigned_user_id:
            area = CargoArea.objects.filter(area__id=instance.to_area_id)
            # sacar los id de usuarios de la area
            for user in area:
                try:
                    async_to_sync(channel_layer.group_send)(
                        str(user.persona.user.id),
                        {
                            "type": "desk_notification",
                            "message": True,
                        },
                    )
                except Exception as e:
                    print(e)

        elif instance.to_area_id and instance.assign_user_id:
            try:
                async_to_sync(channel_layer.group_send)(
                    str(instance.assigned_user_id),
                    {
                        "type": "desk_notification",
                        "message": True,
                    },
                )
            except Exception as e:
                print(e)
    pass
