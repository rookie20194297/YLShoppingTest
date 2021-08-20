from django.http import response
from django.shortcuts import render
from django.views import View
import json
from django import http
from django_redis import get_redis_connection
from youliaomall.utils.response_code import RETCODE
import base64
import pickle
# Create your views here.

class CartsView():
    """购物车管理"""
    def post(self,request):
        """保存购物车/添加购物车"""
        # 接受参数
        json_dict=json.loads(request.body.decode())
        sku_id=json_dict.get('sku_id')
        count =json_dict.get('count')
        selected=json_dict.get('selected',True)
        # 校验参数
        #判断必要参数是否齐全
        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必传参数')
        #校验sku_id是否合法
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        #校验count是否是数字
        try:
            count =int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected 错误')
        #判断用户是否登录
        user =request.user
        if user.is_authenticated:
            #如果登录，则操作redis数据库
            redis_conn=get_redis_connection('carts')
            pl=redis_conn.pipeline()

            #需要以增量计算的形式保存商品数量
            pl.hincrby('carts_%s'% user.id,sku_id,count)
            #保存商品勾选状态
            if selected:
                pl.sadd('selected_%s'% user.id,sku_id)
            # 执行
            pl.execute()
            #响应结果
            return http.JsonResponse({'code':RETCODE,'errmsg':'OK'})
            
        else:    
            #如果没登录，则操作浏览器cookie
            #获取cookie中的购物车，并且判断是否有购物车数据
            cart_str= request.COOKIES.get('carts')
            if cart_str :
                cart_str_bytes= cart_str.encode()# str ->byte
                cart_dict_bytes=base64.b64decode(cart_str_bytes) #byte ->byte(序列)
                cart_dict=pickle.loads(cart_dict_bytes)# 序列化->dict
            else:
                cart_dict={}
            
            #判断当前要加的商品是否在cart_dict中
            if sku_id  in cart_dict:
                # 在购物车中
                origin_count=cart_dict[sku_id]['count']
                count+=origin_count
            cart_dict[sku_id]={
                'count':count,
                'selected':selected
            }
            #购物数据重写回去cooki
            cart_dict_bytes=pickle.dumps(cart_dict)
            cart_str_bytes=base64.b64encode(cart_dict_bytes)
            cart_str=cart_str_bytes.decode()
            response=http.JsonResponse({"code":RETCODE.OK,"errmsg":"OK"})
            response.set_cookie('carts','cookie_cart_str')
    
    def get(self,request):
        """查询购物车"""
        #判断是否登录
        user=request.user
        if user.is_authenticated:
            #已登录
            #创建链接到redis库
            redis_conn=get_redis_connection("carts")

            #查询 哈希（用户id：{商品id：数量}）
            redis_cart=redis_conn.hgetall('carts_%s'%user.id)
            #查询 被勾选状态（用户id：{商品id}）
            redis_conn.smembers('selected_%s'%user.id)
        else:
            pass
        return render(request,'cart.html')

        