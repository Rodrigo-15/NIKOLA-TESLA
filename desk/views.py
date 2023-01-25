from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from desk.models import File,Procedure

from django.db.models import  Q

from desk.serializers import ProcedureSerializer
# Create your views here.

@api_view(['POST'])
def get_procedures(request):
    if request.method == 'POST':
        data = request.data
        date = data['date']
        user_id = data['user_id']
        code_number = data['code_number']
        if user_id == '':
            procedures = Procedure.objects.filter(Q(created_at__icontains=date) | Q(code_number__icontains=code_number) )
        else:
            procedures = Procedure.objects.filter(Q(created_at__icontains=date) | Q(code_number__icontains=code_number), user_id=user_id )
        serilaizer = ProcedureSerializer(procedures, many=True)
        return Response(serilaizer.data)








