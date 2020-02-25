import json

from django.utils import timezone
from appserver.serializers import *


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'user': UserSerializer(user).data,
        'token': token,
        # 'user_group': [x.name for x in user.groups.all()]
    }
