from django.shortcuts import render
from django.views import View

# Create your views here.

class RegisterView(View):
    "用户的注册"
    def get(slef,request):
        """提供数据：用户注册页面"""
        """后端渲染界面"""
        return render(request,'register.html')