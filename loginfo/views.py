# coding:utf-8
from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from public.menu import Menu
from utils.utils import LoginRequiredMixin
from loginfo.models import OperationInfo
from users.models import DctUser
from conf.conf import PYTHONENV


# Create your views here.


class OperationInfoEditView(LoginRequiredMixin, View):
    """
    编辑记录
    """

    def get(self, request):

        if request.GET.get('type', None) == 'json':
            "分页"
            limit = int(request.GET.get('limit', 30))
            page = int(request.GET.get('page', 1))
            max_num = limit * page
            min_num = max_num - limit

            search_data = request.GET.get('key[id]', None)

            if search_data is not None:
                db_count = OperationInfo.objects.filter(Q(type='edit') & Q(key__contains=search_data)).count()
                db_data = list(
                    OperationInfo.objects.filter(Q(type='edit') & Q(key__contains=search_data)).order_by('-id')[
                    min_num:max_num].values())
            else:
                db_count = OperationInfo.objects.filter(type='edit').count()
                db_data = list(OperationInfo.objects.filter(type='edit').order_by('-id')[min_num:max_num].values())
            data = {'code': 0, 'msg': '', 'count': db_count, 'data': db_data}

            return JsonResponse(data, safe=False)

        return render(request, 'operation_edit.html', {
            'record': 'record',
            "PYTHONENV": PYTHONENV
        })


class OperationInfoDelView(LoginRequiredMixin, View):
    """
    删除记录
    """

    def get(self, request):

        if request.GET.get('type', None) == 'json':
            limit = int(request.GET.get('limit', 30))
            page = int(request.GET.get('page', 1))
            max_num = limit * page
            min_num = max_num - limit

            search_data = request.GET.get('key[id]', None)

            if search_data is not None:
                db_count = OperationInfo.objects.filter(Q(type='del') & Q(key__contains=search_data)).count()
                db_data = list(
                    OperationInfo.objects.filter(Q(type='del') & Q(key__contains=search_data)).order_by('-id')[
                    min_num:max_num].values())
            else:
                db_count = OperationInfo.objects.filter(type='del').count()
                db_data = list(OperationInfo.objects.filter(type='del').order_by('-id')[min_num:max_num].values())
            data = {'code': 0, 'msg': '', 'count': db_count, 'data': db_data}

            return JsonResponse(data, safe=False)

        return render(request, 'operation_del.html', {
            'record': 'record',
            "PYTHONENV": PYTHONENV
        })


class UserManageView(LoginRequiredMixin, View):
    def get(self, request):

        if request.GET.get('type', None) == 'json':
            limit = int(request.GET.get('limit', 30))
            page = int(request.GET.get('page', 1))
            max_num = limit * page
            min_num = max_num - limit

            search_data = request.GET.get('key[id]', None)

            if search_data is not None:
                db_count = OperationInfo.objects.filter(Q(type='del') & Q(key__contains=search_data)).count()
                db_data = list(OperationInfo.objects.filter(Q(type='del') & Q(key__contains=search_data))[
                               min_num:max_num].values())
            else:
                db_count = DctUser.objects.all().count()
                db_data = list(DctUser.objects.all()[min_num:max_num].values())

            # 处理一下时间
            for i in db_data:
                try:
                    # add_8_time = i['last_login'].strftime('%Y-%m-%d %H:%M:%S')
                    add_8_time = timezone.localtime(i['last_login'])
                    # print(add_8_time)
                    i['last_login'] = add_8_time
                except Exception as e:
                    print(e)

            data = {'code': 0, 'msg': '', 'count': db_count, 'data': db_data}

            return JsonResponse(data, safe=False)

        return render(request, 'user_manage.html', {
            'top_menu': 'user',
            "PYTHONENV": PYTHONENV
        })

    def post(self, request):

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            id = request.POST.get('id', None)

            data = {'code': 0, 'msg': '', 'data': ''}
            try:
                user = DctUser.objects.get(id=id)
                user.delete()
                data['msg'] = '删除成功'
            except Exception as e:
                data['code'] = 1
                data['msg'] = e

            return JsonResponse(data)
