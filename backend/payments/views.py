from rest_framework import viewsets, permissions
from .models import Payment
from .serializers import PaymentSerializer

# Bloque: CRUD API de pagos.
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
