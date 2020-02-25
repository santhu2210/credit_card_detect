# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from appserver.image_analysis import pdf_modeling, image_modeling
from appserver.serializers import UserSerializer
from appserver.forms import LoginForm, LoginNewForm  # , DashboardForm


# Create your views here.
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, get_user_model, login
from django.shortcuts import redirect  # , render_to_response, render, get_object_or_404

# from django.conf import settings
# from django.views.generic.edit import UpdateView
# from django.views.generic import View
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import get_user_model
# from django.template.loader import render_to_string
# from django.core.mail import send_mail
# from rest_framework.decorators import api_view
# from django.views.decorators.csrf import csrf_protect
# from django.template import RequestContext


def Login_view(request):
    # if request.method == 'POST':
    #     # POST, generate form with data from the request
    #     form = LoginNewForm(request.POST)
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     user = authenticate(username=username, password=password)
    #     uri = '/profile/user/'
    #     if user is not None and user.is_active:
    #         login(request, user)
    #         # return redirect('home')
    #         return render(request, 'home.html', {"user" : user})
    #     else:
    #         form = LoginNewForm()
    #         return render(request,'registration/login.html',{'form':form, 'errormessage':True})
    # else:
    #     # GET, generate blank form
    #     form = LoginNewForm()
    #     return render(request,'registration/login.html',{'form':form})

    return render(request, 'home.html', {})


class LoginView(generic.FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'registration/login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        print("user --->", user)
        uri = '/profile/user/'
        if user is not None and user.is_active:
            login(self.request, user)
            return render(self.request, 'home.html', {"user": user})

            if not user.is_staff:
                if self.request.GET.get('next') is not None and self.request.GET.get('next') != '':
                    uri = uri + '?next=' + self.request.GET.get('next')
                return redirect(uri)

            if self.request.GET.get('next') is not None and self.request.GET.get('next') != '':
                return redirect(self.request.GET.get('next'))

            return super(LoginView, self).form_valid(form)
        else:
            User = get_user_model()
            print(User._meta.fields)
            return self.form_invalid(form)


# @login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        return render(request, 'home.html', {'user': user})
    else:
        return render(request, 'home.html', {})


def Wlogout(request):
    logout(request)
    return redirect('/')


# @api_view(['GET', 'POST', ])
# @login_required(login_url='login')
def SimilarImagePredict(request, format=None):
    if request.method == 'POST':
        # form = DashboardForm(request.POST)
        if request.FILES:
            test_image_obj = request.FILES['testfile']
            # print("test file obj -->", test_file_obj )
            response = image_modeling(request, test_image_obj)

        else:
            response = {"error_status": True}
        return render(request, 'home.html', {"Result": response, "Status": True})  # 'form':form
    return render(request, 'home.html', {})


def PdfPrediction(request, format=None):
    if request.method == 'POST':
        # form = DashboardForm(request.POST)
        if request.FILES:
            test_pdf_obj = request.FILES['testfile']
            # print("test_pdf_obj file obj -->", test_pdf_obj)
            response = pdf_modeling(request, test_pdf_obj)

        else:
            response = {"error_status": True}
        return render(request, 'pdf_process.html', {"Result": response, "Status": True})  # 'form':form
    return render(request, 'pdf_process.html', {})


class MLogout(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )

    def get(self, request, format=None):
        logout(request)
        return Response({'success': True}, status=status.HTTP_200_OK)


class UserList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )

    queryset = User.objects.all()
    serializer_class = UserSerializer


def ProfileEdit(request):
    if request.method == 'POST':
        # POST, generate form with data from the request
        username = request.user
        current_password = request.POST['currentpassword']
        new_password = request.POST['newpassword']
        confirm_password = request.POST['conformpassword']
        print("request user, password ", username, current_password, confirm_password)

        user = authenticate(username=username, password=current_password)
        if user is not None and user.is_active and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            return render(request, 'home.html', {"user": user, 'EditSucess': True})
        else:
            return render(request, 'registration/profile.html', {'EditFailure': True})
    else:
        form = LoginNewForm()
        return render(request, 'registration/login.html', {'form': form})


def Profile(request):
    print(request.user)
    context = {}
    return render(request, 'registration/profile.html', context)
