from rest_framework import serializers
from django.contrib.auth.models import User
from appserver.models import *
# from django.core.mail import EmailMessage
from django.conf import settings



class UserSerializer(serializers.ModelSerializer):	
	class Meta:
		model = User
		fields = (
			'id',
			'username',
			'password',
			'email',
			'first_name',
			'last_name','is_staff',
			'is_superuser',
			'is_active',
			'date_joined',
		)
		extra_kwargs = {'password': {'write_only': True}}
		read_only_fields = ('id','is_staff', 'is_active', 'date_joined',)

	def send_email_to_user(self, user, passwd):
		if user.email and passwd:
			html_content ="Hi,<br> Your username: %s <br> Password: %s"
			from_email   = settings.DEFAULT_FROM_EMAIL
			message      = EmailMessage('Welcome', html_content %(user.email, passwd), from_email, [user.email])
			message.content_subtype = "html"  # Main content is now text/html
			message.send()

	def create(self, validated_data):
		user = User.objects.create(**validated_data)
		user.set_password(validated_data['password'])
		user.save()
		#self.send_email_to_user(user, validated_data['password'])
		return user

	def update(self, instance, validated_data):	
		#instance.email = validated_data['email']
		instance.username = validated_data['username']
		# instance.first_name = validated_data['first_name']
		# instance.last_name = validated_data['last_name']
		if validated_data['password']:
			instance.set_password(validated_data['password'])
		instance.save()
		return instance
