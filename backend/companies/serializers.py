from rest_framework import serializers
from .models import Company, Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan_name', 'start_date', 'end_date', 'active']


class CompanySerializer(serializers.ModelSerializer):
    active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'rut', 'active', 'active_subscription']
        # ajusta fields a lo que tengas

    def get_active_subscription(self, obj):
        sub = obj.get_active_subscription()
        if not sub:
            return None
        return {
            'id': sub.id,
            'plan_name': sub.plan_name,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'active': sub.active,
        }
