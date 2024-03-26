from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProcedureTracing
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
            user_id = 2067
            cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
            if not cargo_area:
                areas = []
            data_area = cargo_area.area.all()
            areas = AreaSerializer(data_area, many=True).data
            area_id = [area["id"] for area in areas]
            tracings_for_area = ProcedureTracing.objects.filter(
                to_area_id__in=area_id, is_approved=False, assigned_user_id=None
            ).order_by("-created_at")

            obj_message = []
            for tracing in tracings_for_area:
                obj_message.append(
                    {
                        "procedure_id": tracing.procedure.id,
                        "message": f"{tracing.user}, te ha asignado un trámite con número {tracing.procedure.code_number}. Revisalo por favor.",
                        "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

            async_to_sync(channel_layer.group_send)(
                str(instance.user_id),
                {
                    "type": "desk_area_notification",
                    "message": obj_message,
                },
            )
        except Exception as e:
            print(e)
    pass
