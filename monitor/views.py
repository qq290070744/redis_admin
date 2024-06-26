# coding:utf-8
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from users.models import RedisConf
from conf import logs
import time
import threading
# from dss.Serializer import serializer
# import serializer

from conf.conf import scan_batch, search_scan_batch, PYTHONENV
from public.redis_api import get_cl, get_redis_conf, redis_conf_save, check_redis_connect, get_redis_info
from utils.utils import LoginRequiredMixin, is_binary


# Create your views here.


class GetRedisInfo(LoginRequiredMixin, View):
    """
    首页获取redis info信息
    """

    def get_info(self, redis_obj):
        status = check_redis_connect(name=redis_obj.name)
        if status is True:
            client = get_cl(redis_name=redis_obj.name)
            info_dict = get_redis_info(cl=client, number=1)
            # print(info_dict)
            time_local = time.localtime(info_dict.get('rdb_last_save_time'))
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            info_dict['rdb_last_save_time'] = dt
            info_dict.update(host=redis_obj.host)
            info_dict.update(redis_id=redis_obj.id)
            return info_dict
        return False

    def get(self, request):
        # print request.META["HTTP_REFERER"]
        servers = get_redis_conf(name=None, user=request.user)
        # "分页"
        # limit = int(request.GET.get('limit', 2))
        paginator = Paginator(servers, 2)  # 每页显示2个集群
        page = int(request.GET.get('page', 1))
        # start = (page - 1) * limit
        # end = start + limit
        # servers = servers[start:end]
        servers = paginator.get_page(page)
        # print(start, end)
        # print(len(servers))
        data = []
        threading_li = []

        def sync_exec(ser):
            try:
                redis_obj = RedisConf.objects.get(id=ser.redis)
                # print(ser)
                # print(ser.redis)
                # print(redis_obj.name)
                if redis_obj.type == 1:
                    redis_cluster_obj = RedisConf.objects.filter(name__iexact=redis_obj.name)

                    def sync_exec1(redis_cluster):
                        info = self.get_info(redis_cluster)
                        info['name'] = redis_obj.name
                        if not isinstance(info, bool):
                            data.append(info)

                    threads1 = []
                    for redis_cluster in redis_cluster_obj:
                        t1 = threading.Thread(target=sync_exec1, args=(redis_cluster,))
                        t1.start()
                        threads1.append(t1)
                    for t1 in threads1:
                        t1.join()
                else:
                    # print(redis_obj.name)
                    info = self.get_info(redis_obj)
                    # print(redis_obj.name)
                    info['name'] = redis_obj.name
                    if not isinstance(info, bool):
                        data.append(info)
            except Exception as e:
                logs.error(e)

        for ser in servers:
            t = threading.Thread(target=sync_exec, args=(ser,))
            t.start()
            threading_li.append(t)
        for t in threading_li:
            t.join()
        return render(request, 'index.html', {
            'data': data,
            'console': 'console',
            'current_page': servers,
            "PYTHONENV": PYTHONENV
        })


class RedisErrorHtmlView(LoginRequiredMixin, View):
    """
    错误页视图
    """

    def get(self, request):
        return render(request, 'redis_error.html', {
            'error': 'error',
            "PYTHONENV": PYTHONENV
        })


class CheckRedisContent(LoginRequiredMixin, View):
    """
    获取连接错误信息
    """

    def check_redis_status(self, redis_obj):
        status = check_redis_connect(name=redis_obj.name)
        if status is not True:
            data = {'name': status["redis"], 'error': status["message"]}
            return data
        return True

    def get(self, request):
        servers = get_redis_conf(name=None, user=request.user)
        data_list = []
        for ser in servers:
            try:
                redis_obj = RedisConf.objects.get(id=ser.redis)
                if redis_obj.type == 1:
                    redis_cluster_obj = RedisConf.objects.filter(name__iexact=redis_obj.name)
                    for redis_cluster in redis_cluster_obj:
                        redis_status = self.check_redis_status(redis_cluster)
                        if redis_status is not True:
                            data_list.append(redis_status)
                else:
                    redis_status = self.check_redis_status(redis_obj)
                    if redis_status is not True:
                        data_list.append(redis_status)
            except Exception as e:
                logs.error(e)
        if len(data_list) != 0:
            data = {'code': 0, 'msg': '', 'data': data_list}
        else:
            data = {'code': 1, 'msg': '无连接错误', 'data': ''}

        return JsonResponse(data)


class GetKeyView(LoginRequiredMixin, View):
    """
    获取key
    """

    def get(self, request, redis_name, db_id):
        from public.redis_api import get_cl, get_all_keys_tree

        values = []
        "搜索"
        search_name = request.GET.get('key[id]', None)
        "分页"
        limit = int(request.GET.get('limit', 30))
        page = int(request.GET.get('page', 1))
        max_num = limit * page
        min_num = max_num - limit

        cl = get_cl(redis_name, int(db_id))
        if search_name is not None:
            keys = get_all_keys_tree(client=cl, key=search_name, cursor=0, min_num=min_num, max_num=max_num)
        else:
            keys = get_all_keys_tree(client=cl, cursor=0, min_num=min_num, max_num=max_num)
        for key in keys:
            # print(type(key))
            if is_binary(key):
                try:
                    key = key.decode('utf-8')
                except Exception as e:
                    logs.error(e)
                    key = str(key)
                    # print(key)
            values.append({'key': key})

        db_key_num = cl.dbsize()
        if isinstance(db_key_num, dict):
            all_keys = 0
            for k, v in db_key_num.items():
                all_keys = all_keys + v
            db_key_num = all_keys / 2
        batch_key_num = scan_batch
        if batch_key_num > db_key_num:
            key_num = db_key_num
        else:
            key_num = batch_key_num
        key_value_dict = {'code': 0, 'msg': '', 'count': key_num, 'data': values}
        # print(values)
        return JsonResponse(key_value_dict, safe=False)


class GetValueView(LoginRequiredMixin, View):
    """
    获取key对应value
    """

    def get(self, request, redis_name, value_db_id, key):
        from public.redis_api import get_cl
        from public.data_view import get_value
        logs.info('get value: redis_name={0}, db={1}, key={2}'.format(redis_name, value_db_id, key))
        cl = get_cl(redis_name, int(value_db_id))
        value_dict = {'code': 0, 'msg': '', 'data': ''}
        if cl.exists(key):
            value = ''
            if request.GET.get("type", None) == 'ttl':
                value = cl.ttl(key)
                if value is None:
                    value = -1
                logs.info('get key ttl: redis_name={0}, db={1}, key={2}, ttl={3}'.format(
                    redis_name, value_db_id, key, value))
            else:
                try:
                    value = get_value(key, int(value_db_id), cl)
                except Exception as e:
                    logs.error('get value is error: redis_name:{0}, key:{1}, db:{2}, cl:{3}, error_info:{4}'.format(
                        redis_name, key, value_db_id, cl, e))
                    value_dict['code'] = 1
            value_dict['data'] = value
        else:
            logs.warning('key is not exists: redis_name={0}, db={1}, key={2}'.format(redis_name, value_db_id, key))
            value_dict['code'] = 1
        for k in value_dict:
            # print(k, value_dict[k])
            if is_binary(value_dict[k]):
                value_dict[k] = str(value_dict[k], encoding="utf-8")
        if isinstance(value_dict['data'], dict):
            for k, v in value_dict['data'].items():
                # print(k, v)
                if is_binary(v):
                    value_dict['data'][k] = str(v, encoding="utf-8")
        if isinstance(value_dict['data']['value'], list):
            for index, v in enumerate(value_dict['data']['value']):
                # print(index, v)
                if is_binary(v):
                    value_dict['data']['value'][index] = str(v, encoding="utf-8")
        if isinstance(value_dict['data']['value'], dict):
            new_dic = {}
            for k, v in value_dict['data']['value'].items():
                # print(k, v)
                if is_binary(k):
                    k = str(k, encoding="utf-8")
                if is_binary(v):
                    v = str(v, encoding="utf-8")
                new_dic[k] = v
            value_dict['data']['value'] = new_dic
        # print(value_dict)
        return JsonResponse(value_dict, safe=False)

    def post(self, request, redis_name, value_db_id, key):
        """
        修改TTL
        """
        from public.redis_api import get_cl
        cl = get_cl(redis_name, int(value_db_id))
        value_dict = {'code': 0, 'msg': '', 'data': ''}
        ttl = request.POST.get("ttl", None)
        if cl.exists(key) and ttl:
            try:
                cl.expire(key, ttl)
                logs.info('change key tll: redis_name={0}, db={1}, key={2}, ttl={3}'.format(
                    redis_name, value_db_id, key, ttl))
                value_dict['msg'] = "修改成功"
            except Exception as e:
                logs.error(e)
                value_dict['msg'] = '修改失败，请联系管理员'
        return JsonResponse(value_dict)


class GetIdView(LoginRequiredMixin, View):
    """
    key列表
    """

    def get(self, request, redis_name, id):
        return render(request, 'keyvalue.html', {
            'db_id': id,
            'redis_name': redis_name,
            'db_num': 'db' + str(id),
            "PYTHONENV": PYTHONENV
        })


class ClientListView(LoginRequiredMixin, View):
    """
    获取客户端主机
    """

    def get(self, request):
        client_id = request.GET.get('client_id', None)
        if client_id is not None:
            redis_obj = RedisConf.objects.get(id=client_id)
            status = check_redis_connect(name=redis_obj.name)
            if status is True:
                client = get_cl(redis_name=redis_obj.name)
                client_list = client.client_list()
                "分页"
                limit = int(request.GET.get('limit', 30))
                page = int(request.GET.get('page', 1))
                max_num = limit * page
                min_num = max_num - limit
                # print(client_list)
                client_list_data = []
                client_list_len = 0
                if isinstance(client_list, list):
                    client_list_data = client_list[min_num:max_num]
                    client_list_len = len(client_list)
                else:
                    for k, v in client_list.items():
                        client_list_data += v
                    client_list_len = len(client_list_data)

                data = {'code': 0, 'msg': '', 'count': client_list_len, 'data': client_list_data}
        else:
            data = {'code': 1, 'msg': 'Error, 请联系系统管理员！', 'data': ''}

        return JsonResponse(data, safe=False)


class ClientHtmlView(LoginRequiredMixin, View):
    def get(self, request, client_id):
        return render(request, 'client_list.html', {
            'client_id': client_id,
            "PYTHONENV": PYTHONENV
        })


class DelKeyView(LoginRequiredMixin, View):
    """
    删除key
    """

    def post(self, request):
        from public.data_change import ChangeData
        from loginfo.models import OperationInfo
        from public.redis_api import get_cl
        from public.data_view import get_value

        redis_name = request.POST.get('redis_name', None)
        db_id = request.POST.get('db_id', None)
        key = request.POST.get('key', None)

        cl = get_cl(redis_name, int(db_id))
        old_data = get_value(key, int(db_id), cl)
        db = OperationInfo(
            username=request.user.username,
            server=redis_name,
            db=db_id,
            key=key,
            old_value=old_data,
            type='del',
        )
        db.save()

        if key:
            ch_data = ChangeData(redis_name=redis_name, db_id=db_id)

            if ch_data.delete_key(key=key):
                data = {'code': 0, 'msg': 'KEY: ' + key + ' is Success', 'data': ''}
                return JsonResponse(data)

        data = {'code': 1, 'msg': 'KEY: ' + key + ' is Failed', 'data': ''}

        return JsonResponse(data)


class EditValueTableView(LoginRequiredMixin, View):
    """
    编辑value
    """

    def get(self, request, redis_name, edit_db_id):
        from public.redis_api import get_cl
        from public.data_view import get_value
        cl = get_cl(redis_name, int(edit_db_id))
        key = request.GET.get('key', None)
        if cl.exists(key):
            value = get_value(key, int(edit_db_id), cl)
            if cl.type(key) == 'list':
                value_list = []
                num = 0
                for i in value['value']:
                    value_dict = {str(num): i}
                    num += 1
                    value_list.append(value_dict)
                value['value'] = value_list
        if is_binary(value['value']):
            value['value'] = str(value['value'], encoding="utf-8")
        return render(request, 'edit.html', {
            'db_num': 'db' + str(edit_db_id),
            'redis_name': redis_name,
            'data': value,
            "PYTHONENV": PYTHONENV
        })

    def post(self, request, redis_name, edit_db_id):
        from public.data_change import ChangeData
        from public.redis_api import get_cl
        from public.data_view import get_value
        from loginfo.models import OperationInfo

        cl = get_cl(redis_name, int(edit_db_id))
        ch_data = ChangeData(redis_name=redis_name, db_id=edit_db_id)

        key = request.GET.get('key', None)
        post_key_type = request.POST.get('Type', None)
        old_data = get_value(key, int(edit_db_id), cl)

        if post_key_type == 'string':
            post_value = request.POST.get('value', None)
            ch_data.edit_value(key=key, value=None, new=post_value, score=None)
        elif post_key_type == 'zset':
            score = request.POST.get('Score', None)
            value = request.POST.get('Value', None)
            old_value = request.POST.get('Old_Value', None)
            ch_data.edit_value(key=key, value=old_value, new=value, score=score)
        elif post_key_type == 'set':
            value = request.POST.get('Value', None)
            old_value = request.POST.get('Old_Value', None)
            ch_data.edit_value(key=key, value=old_value, new=value, score=None)
        elif post_key_type == 'hash':
            value_key = request.POST.get('Key', None)
            value = request.POST.get('Value', None)
            ch_data.edit_value(key=key, value=value_key, new=value, score=None)
        elif post_key_type == 'list':
            index = request.POST.get('Index', None)
            value = request.POST.get('Value', None)
            ch_data.edit_value(key=key, value=index, new=value, score=None)

        data = get_value(key, int(edit_db_id), cl)
        if cl.type(key) == 'list':
            value_list = []
            num = 0
            for i in data['value']:
                value_dict = {str(num): i}
                num += 1
                value_list.append(value_dict)
            data['value'] = value_list

        db = OperationInfo(
            username=request.user.username,
            server=redis_name,
            db='db' + edit_db_id,
            key=key,
            old_value=old_data,
            value=data,
            type='edit',
        )
        db.save()

        return render(request, 'edit.html', {
            'db_num': 'db' + str(edit_db_id),
            'redis_name': redis_name,
            'data': data,
            "PYTHONENV": PYTHONENV
        })


class BgSaveView(LoginRequiredMixin, View):
    """
    保存数据 bgsave
    """

    def get(self, request, redis_id):
        redis_obj = RedisConf.objects.get(id=redis_id)
        cl = get_cl(redis_name=redis_obj.name, db_id=0)
        cl.bgsave()

        return HttpResponseRedirect(reverse("index"))


class AddKeyView(LoginRequiredMixin, View):
    """
    添加数据
    """

    def get(self, request, redis_name):
        this_tab = 'string'
        db_id = request.GET.get('db', None)

        return render(request, 'add_key.html', {
            'this_tab': this_tab,
            'db': db_id,
            "PYTHONENV": PYTHONENV
        })

    def post(self, request, redis_name):
        from public.data_change import ChangeData
        db_id = request.POST.get('db_id', None)
        type = request.POST.get('type', None)
        key = request.POST.get('key', None)
        value = request.POST.get('value', None)

        ch_data = ChangeData(redis_name=redis_name, db_id=db_id)
        if type == 'string':
            ch_data.add_key(key=key, value=value, type=type)
        elif type == 'zset':
            score = request.POST.get('score', None)
            ch_data.add_key(key=key, value=value, score=int(score), type=type)
        elif type == 'set':
            ch_data.add_key(key=key, value=value, type=type)
        elif type == 'hash':
            vkey = request.POST.get('vkey', None)
            ch_data.add_key(key=key, vkey=vkey, value=value, type=type)
        elif type == 'list':
            ch_data.add_key(key=key, value=value, type=type)

        return HttpResponseRedirect('/' + redis_name + '/db' + db_id + '/')


class ClearDbView(LoginRequiredMixin, View):
    """
    清空DB
    """

    def post(self, request):
        data = {"code": 0, "msg": "successful", "data": ""}
        redis_name = request.POST.get("redis_name", None)
        db_id = request.POST.get("db_id", None)
        try:
            cl = get_cl(redis_name=redis_name, db_id=db_id)
            cl.flushdb()
        except Exception as e:
            logs.error(e)
            data["code"] = 1
            data["msg"] = "failed"
        return JsonResponse(data=data, safe=False)


class RedisListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            data = {"code": 0, "msg": "", "data": ""}
            redis_objs = RedisConf.objects.all()
            redis_li = []
            for i in redis_objs:
                redis_li.append({"name": i.name, "host": i.host, "port": i.port,
                                 "username": i.username, "password": i.password,
                                 "database": i.database, "type": i.type, "id": i.id}
                                )
            # data["data"] = serializer(redis_objs)
            data["data"] = redis_li
            return JsonResponse(data=data)
        return render(request, 'redis_list.html', {
            "PYTHONENV": PYTHONENV
        })


class RedisEditView(LoginRequiredMixin, View):
    def post(self, request):
        data = {"code": 0, "data": "", "msg": "成功"}
        status = redis_conf_save(request)
        if not status:
            data["code"] = 1
            data["msg"] = "失败"
        return JsonResponse(data=data, safe=False)


class RedisAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'redis_add.html', {
            'X-Frame-Options': 'ALLOW-FROM',
            "PYTHONENV": PYTHONENV}, )

    def post(self, request):
        data = {"code": 0, "data": "", "msg": "成功"}
        status = redis_conf_save(request)
        if not status:
            data["code"] = 1
            data["msg"] = "失败"
        return JsonResponse(data=data, safe=False)


class RedisDelView(LoginRequiredMixin, View):
    def post(self, request):
        redis_id = request.POST.get('id', None)
        data = {'code': 0, 'data': '', 'msg': '成功'}
        try:
            RedisConf.objects.get(id=redis_id).delete()
        except Exception as e:
            logs.error(e)
            data['code'] = 1
            data['msg'] = '失败，请查看日志'
        return JsonResponse(data=data)
