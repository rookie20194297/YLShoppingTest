#确保可以使用模板引擎中的static、url这类语句
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

def jinja2_environment(**options):
    '''Jinja2模板配置文件，自定义语法'''
    env = Environment(**options)
    env.globals.update({
        'static':staticfiles_storage.url,#获取静态文件的前缀
        'url':reverse,#反向解析
    })
    return env