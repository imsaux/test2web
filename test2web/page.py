# -*- encoding:utf-8 -*-
from django.forms import Form
from test2web import models
from datetime import datetime, tzinfo, timedelta, timezone
from django.shortcuts import render, render_to_response
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import auth
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from django.utils.http import urlquote
from django.http import FileResponse
from pypinyin import pinyin, Style
import datetime
import json
import locale
import logging, inspect, os



global _r_start_date_, _r_end_date_, _r_site_, _r_reasons_
_r_start_date_ = None
_r_end_date_ = None
_r_site_ = None
_r_reasons_ = None

# 登录表单模型
class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

# 注册表单模型
class UserRegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    is_staff = forms.BooleanField(label='管理员权限', widget=forms.CheckboxInput(), required=False)

def _datetime_format(date=None, mode=1):
    if date is None:
        date = datetime.datetime.now()
    if mode == 1:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日'
    elif mode == 2:
        return date.strftime('%Y%m%d%H%M%S')
    elif mode == 3:
        return date.strftime('%m/%d/%Y')
    elif mode == 4:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日 ' + str(date.hour).zfill(2) + ':' + str(date.minute).zfill(2) + ':' + str(date.second).zfill(2)
    elif mode == 5:
        return date.strftime('%Y%m%d')

def _getLogger():
    logger = logging.getLogger('[web]')

    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    if not os.path.exists(os.path.join(dirpath, 'log')):
        os.makedirs(os.path.join(dirpath, 'log'))
    handler = logging.FileHandler(os.path.join(dirpath, 'log', _datetime_format(date=datetime.datetime.now(),mode=5) + ".log"))

    formatter = logging.Formatter('%(asctime)s %(name)-12s [line:%(lineno)d] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger

log = _getLogger()

def VERSION(request):
    return HttpResponse('版本号：v20180510'.encode())

def login(request):
    log.info("login > start")
    log.info("login > 日期：" + _datetime_format(mode=5))
    log.info("login > IP地址：" + request.META['REMOTE_ADDR'])
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            log.info("login > " + username)

            # 获取的表单数据与数据库进行比较
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                if user.is_staff:
                    log.info("login > 管理员")
                    return daily_manage_lab(request)
                else:
                    log.info("login > 访客")
                    return daily_view(request)
            else:
                log.info("login > 无效账户")
                return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
    log.info("login > 未注册")
    return render_to_response('login.html', {'uf': uf})

def register(request):
    log.info("register > start")
    log.info(datetime.datetime.now())
    if request.method == 'POST':
        urf = UserRegisterForm(request.POST)
        if urf.is_valid():
            # 获取表单用户密码
            username = urf.cleaned_data['username']
            password = urf.cleaned_data['password']
            isstaff = urf.cleaned_data['is_staff']
            try:
                user = User.objects.create_user(username=username)
                user.set_password(password)
                user.is_staff = isstaff
                user.save()
                log.info("register > end")
                return HttpResponseRedirect('/login/')
            except Exception as e:
                urf = UserRegisterForm()
                log.info("register > end")
                return render_to_response('register.html', {'uf': urf})
        else:
            log.info("register > end")
    else:
        urf = UserRegisterForm()
        log.info("register > end")
        return render_to_response('register.html', {'uf': urf})

def _redirect(page, params):
    _page = page + '.html'
    return render_to_response(
        _page,
        params
    ).content.decode('utf8')

def logout(request):
    log.info("logout > start")
    auth.logout(request)
    log.info("logout > end")
    return login(request)

def file_download(request, _file):
    file = open(_file, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % (urlquote(_file))
    return response

def export_xlsx(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Sheet'
    all_data = _get_daily_data(_is_confirm=True)
    ws.append(["铁路局", "车站", "过车辆数", "报警数", "问题及处理", "问题跟踪"])
    for row in all_data:
        ws.append(
            [
                row[9],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
            ]
        )
    _tab_ref = "A1:F%s" % (len(all_data)+1)
    tab = Table(displayName="Table1", ref=_tab_ref)

    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    _file_name = datetime.datetime.now().strftime('%m%d') + '接发车各站运行情况日统计表.xlsx'
    wb.save(_file_name)
    return file_download(request, _file_name)

def _auto_create_daily_info(date=None):
    # 自动创建
    _all_site_ = [x.name for x in models.Site.objects.all().order_by('order')]
    if date is None:
        date = datetime.datetime.now()
    _range_from, _range_to = _get_range_date(date)
    for site in _all_site_:
        _site_obj = models.Site.objects.get(name=site)
        _site_warning = models.ClientWarning.objects.filter(site=_site_obj, datetime__range=(_range_from, _range_to))
        _site_status = models.ClientStatus.objects.filter(site=_site_obj, datetime__range=(_range_from, _range_to))
        _site_meta = models.DailyReport_Meta.objects.filter(site=_site_obj).order_by("date", "id")

        if len(_site_warning) > 0:
            _columns = [x['warn'] for x in _site_warning.values('warn').distinct()]  # 列出报警类型
            if len(_columns) == 0:
                warning = '无'
            else:
                warning = ''
                for col in _columns:
                    if warning == '':
                        warning += str(col) + \
                                   str(_site_warning.filter(warn=col).last().count)
                    else:
                        warning += ';' + \
                                   str(col) + \
                                   str(_site_warning.filter(warn=col).last().count)
        else:
            warning = '无'

        if len(_site_status) > 0:
            carriages = int(_site_status.values('line_1_carriages').last()[
                                'line_1_carriages']) + int(
                _site_status.values('line_2_carriages').last()['line_2_carriages'])
        else:
            carriages = 0

        _new = models.DailyReport(
            date = date,
            site = _site_obj,
            warn = warning,
            carriages_count=carriages,
        )
        _new.save()

        if len(_site_meta) > 0:
            _new_meta = models.DailyReport_Meta(
                date=date,
                site=_site_obj,
                problem=_site_meta.last().problem,
                track=_site_meta.last().track,
            )
            _new_meta.save()

            # _return.append([_site_obj.name, carriages, warning, _site_meta.last().problem, _site_meta.last().track, _new.id, _new.status])
        else:
            _new_meta = models.DailyReport_Meta(
                date=date,
                site=_site_obj,
                problem='无',
                track='无',
            )
            _new_meta.save()


def _get_daily_data(_from=None, _to=None, _site_name=None, _reasons=None, _is_confirm=False):
    _return = list()
    if _from is None:
        _from = datetime.datetime.now()
    if _to is None:
        _to = datetime.datetime.now()
    if _r_reasons_ is not None:
        _reasons = _r_reasons_
    if _r_site_ is not None:
        _site_name = _r_site_
    if _r_start_date_ is not None:
        _from = datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    if _r_end_date_ is not None:
        _to = datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    if _site_name is None or _site_name == '全部':
        _all_site_ = [x.name for x in models.Site.objects.all().order_by('order')]
    else:
        try:
            _all_site_ = [models.Site.objects.get(name=_site_name).name]
        except:
            _all_site_ = [models.Site.objects.get(code=_site_name).name]
    _all_data_ = models.DailyReport.objects.filter(date__range=(_from, _to))
    _sitenames_dailyreport = [models.Site.objects.get(id=x['site']).name for x in
                              _all_data_.values('site').distinct()]
    for site in _all_site_:
        _site_obj = models.Site.objects.get(name=site)
        if site in _sitenames_dailyreport: # 有日报表数据
            _site_data_is_confirm = None
            _site_data_reasons = None
            if _is_confirm is True:
                _site_data_is_confirm = _all_data_.filter(site=_site_obj, status=True)
            else:
                _site_data_is_confirm = _all_data_.filter(site=_site_obj)
            if _reasons is None or len(_reasons) == 0 or '全部' in _reasons:
                pass
            else:
                _site_data_reasons = _all_data_.filter(reason__name__in=_reasons)
            ret_data = set(_all_data_)
            if _site_data_is_confirm is not None:
                ret_data = ret_data & set(_site_data_is_confirm)
            if _site_data_reasons is not None:
                ret_data = ret_data & set(_site_data_reasons)

            for data in ret_data:
                carriages_count = data.carriages_count
                warn = data.warn
                _data_meta = models.DailyReport_Meta.objects.filter(site=_site_obj, date=data.date)
                # 0 id
                # 1 站名
                # 2 过车数
                # 3 报警统计
                # 4 问题
                # 5 问题追踪
                # 6 问题分类
                # 7 记录发布状态
                # 8 记录日期
                # 9 所属路局

                if len(_data_meta) > 0:
                    _return.append(
                        [
                            data.id,
                            _site_obj.name,
                            carriages_count,
                            warn,
                            _data_meta.last().problem,
                            _data_meta.last().track,
                            '、'.join([x['name'] for x in data.reason.all().values('name')]),
                            data.status,
                            _datetime_format(date=data.date, mode=3),
                            _site_obj.bureau
                        ]
                    )
                else:
                    _return.append(
                        [
                            data.id,
                            _site_obj.name,
                            carriages_count,
                            warn,
                            '无',
                            '无',
                            '、'.join([x['name'] for x in data.reason.all().values('name')]),
                            data.status,
                            data.date,
                            _site_obj.bureau
                        ]
                    )
    return _return

def _init_global():
    global _r_start_date_, _r_end_date_, _r_site_, _r_reasons_
    _r_start_date_ = None
    _r_end_date_ = None
    _r_site_ = None
    _r_reasons_ = None

def daily_manage_search(request):
    global _r_start_date_, _r_end_date_ , _r_site_, _r_reasons_
    r_site = request.POST['r_site']
    _r_site_ = r_site
    r_start_date = request.POST['start_date']
    _r_start_date_ = r_start_date
    r_end_date = request.POST['end_date']
    _r_end_date_ = r_end_date
    r_reasons = request.POST.getlist('r_reason')
    _r_reasons_ = r_reasons
    _from = datetime.datetime.strptime(r_start_date, '%m/%d/%Y')
    _to = datetime.datetime.strptime(r_end_date, '%m/%d/%Y')
    _sites_name = [x.name for x in models.Site.objects.all().order_by('order')]
    _reasons = [x.name for x in models.Reason.objects.all()]



    # global _r_start_date_, _r_end_date_ , _r_site_, _r_reasons_
    # _response_data = request.POST['data'].split('@@@@@')
    # r_site = _response_data[0]
    # _r_site_ = r_site
    # r_start_date = _response_data[1]
    # _r_start_date_ = r_start_date
    # r_end_date = _response_data[2]
    # _r_end_date_ = r_end_date
    # r_reasons = _response_data[3]
    #
    # _r_reasons_ = r_reasons.split(',')
    # _from = datetime.datetime.strptime(r_start_date, '%m/%d/%Y')
    # _to = datetime.datetime.strptime(r_end_date, '%m/%d/%Y')
    _sites_code = [''.join([x[0] for x in pinyin(x.name, style=Style.FIRST_LETTER)])+x.name for x in models.Site.objects.all().order_by('order')]
    # _sites_name = [x.name for x in models.Site.objects.all().order_by('order')]
    # _reasons = [x.name for x in models.Reason.objects.all()]
    all_data = _get_daily_data(_from=_from, _to=_to, _site_name=r_site,  _reasons=r_reasons)


    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_manage_lab',
                {
                    'title': _datetime_format(date=_to),
                    'data': all_data,
                    'date_now': _datetime_format(mode=3),
                    'all_site': json.dumps(_sites_name),
                    'all_site_old': ['全部'] +_sites_code,
                    'all_site_code': ['全部'] + _sites_code,
                    'error_reason': json.dumps(_reasons),
                    'error_reason_old': _reasons,
                    'q_site': '全部' if _r_site_ is None else _r_site_,
                    'q_reason': json.dumps(list()) if _r_reasons_ is None else json.dumps(_r_reasons_),
                    'q_start_date': _datetime_format(mode=3) if _r_start_date_ is None else _r_start_date_,
                    'q_end_date': _datetime_format(mode=3) if _r_end_date_ is None else _r_end_date_,
                }
            ),
            'user': request.user,
        }
    )

def daily_view_search(request):

    global _r_start_date_, _r_end_date_ , _r_site_, _r_reasons_
    r_site = request.POST['r_site']
    _r_site_ = r_site
    r_start_date = request.POST['start_date']
    _r_start_date_ = r_start_date
    r_end_date = request.POST['end_date']
    _r_end_date_ = r_end_date
    r_reasons = request.POST.getlist('r_reason')
    _r_reasons_ = r_reasons
    _from = datetime.datetime.strptime(r_start_date, '%m/%d/%Y')
    _to = datetime.datetime.strptime(r_end_date, '%m/%d/%Y')
    _sites = ['全部'] + [x.name for x in models.Site.objects.all().order_by('order')]
    _reasons = ['全部'] + [x.name for x in models.Reason.objects.all()]

    if r_site == '全部':
        all_data = _get_daily_data(_from=_from, _to=_to, _is_confirm=True, _reasons=r_reasons)

    else:
        all_data = _get_daily_data(_from=_from, _to=_to, _site_name=r_site, _is_confirm=True,  _reasons=r_reasons)


    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_view',
                {
                    'title': _datetime_format(date=_to),
                    'data': all_data,
                    'date_now': _datetime_format(mode=3),
                    'all_site': _sites,
                    'error_reason': _reasons,
                    'q_site': r_site,
                    'q_reason': r_reasons,
                    'q_start_date': r_start_date,
                    'q_end_date': r_end_date,
                }
            ),
            'user': request.user,
        }
    )




def daily_view(request, _date=None):
    log.info("daily_view > 用户（ " + request.user.username + ' )')
    log.info("daily_view > IP（ " + request.META['REMOTE_ADDR'] + ' )')
    log.debug("daily_view > " + repr(_date))
    if _date is None:
        _date = datetime.datetime.now()
    # _range_from, _range_to = _get_range_date(_date)
    _init_global()
    _sites = ['全部'] + [x.name for x in models.Site.objects.all().order_by('order')]
    _all_data_ = _get_daily_data(_from=_date, _to=_date, _is_confirm=True)
    _reasons = ['全部'] + [x.name for x in models.Reason.objects.all()]
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_view',
                {
                    'title': _datetime_format(),
                    'data': _all_data_,
                    'all_site': _sites,
                    'date_now': _datetime_format(mode=3),
                    'error_reason': _reasons,
                    'q_site': '全部',
                    'q_reason': list(),
                    'q_start_date': _datetime_format(mode=3),
                    'q_end_date': _datetime_format(mode=3),
                }
            ),
            'user': request.user,
        }
    )

@login_required
def daily_manage_lab(request, _date=None, init_global=True, loc=None):
    log.info("daily_manage_lab > 用户（ " + request.user.username + ' )')
    log.info("daily_manage_lab > IP（ " + request.META['REMOTE_ADDR'] + ' )')
    log.info("daily_manage_lab > " + repr(_date) + ' , ' + repr(init_global) + ' , ' + repr(loc))
    if _date is None:
        _date = datetime.datetime.now()
    if init_global:
        _init_global()
    # _range_from, _range_to = _get_range_date(_date)
    _sites_code = [''.join([x[0] for x in pinyin(x.name, style=Style.FIRST_LETTER)])+x.name for x in models.Site.objects.all().order_by('order')]
    _sites_name = [x.name for x in models.Site.objects.all().order_by('order')]
    _reasons = [x.name for x in models.Reason.objects.all().order_by('name')]

    all_data = _get_daily_data()
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_manage_lab',
                {
                    'title': _datetime_format(date=_date),
                    'data': all_data,
                    'date_now': _datetime_format(mode=3),
                    'all_site': json.dumps(_sites_name),
                    'all_site_old': ['全部'] +_sites_code,
                    # 'all_site_code': ['全部'] + _sites_code,
                    'all_site_code': ['全部'] + _sites_code,
                    'error_reason': json.dumps(_reasons),
                    'error_reason_old': _reasons,
                    'q_site': '全部' if _r_site_ is None else _r_site_,
                    'q_reason': json.dumps(list()) if _r_reasons_ is None else json.dumps(_r_reasons_),
                    'q_start_date': _datetime_format(mode=3) if _r_start_date_ is None else _r_start_date_,
                    'q_end_date': _datetime_format(mode=3) if _r_end_date_ is None else _r_end_date_,
                    'loc': int(loc) if loc is not None else None,

                }
            ),
            'user': request.user,
            # 'body_script': _js,
        }
    )

def daily_ajax_search(request):
    try:
        _site = request.POST['r_site']
        _site_obj = models.Site.objects.get(name=_site)
        _meta_obj = models.DailyReport_Meta.objects.filter(site=_site_obj.id).last()
        ret = list()
        ret.append(_meta_obj.problem)
        ret.append(',')
        ret.append(_meta_obj.track)
        return HttpResponse(ret)
    except Exception as e:
        return HttpResponse(None)

def daily_create_all(request):
    log.info("daily_create_all > 用户（ " + request.user.username + ' )')
    log.info("daily_create_all > 一键新增记录")
    _auto_create_daily_info()
    return HttpResponseRedirect(reverse('daily_manage_lab'))

def daily_delete(request, _id):
    log.info("daily_delete > 用户（ " + request.user.username + ' )')
    log.info("daily_delete > 删除记录（ #" + repr(_id) + ' )')
    obj = models.DailyReport.objects.get(id=_id)
    obj.delete()
    return daily_manage_lab(request, init_global=False)

def daily_confirm(request, _id):
    log.info("daily_confirm > 用户（ " + request.user.username + ' )')
    log.info("daily_confirm > 发布记录（ #" + repr(_id) + ' )')
    obj = models.DailyReport.objects.get(id=_id)
    obj.status = True
    obj.save()
    return daily_manage_lab(request, init_global=False, loc=_id)

def daily_unconfirm(request, _id):
    log.info("daily_unconfirm > 用户（ " + request.user.username + ' )')
    log.info("daily_unconfirm > 取消发布记录（ #" + repr(_id) + ' )')

    obj = models.DailyReport.objects.get(id=_id)
    obj.status = False
    obj.save()
    return daily_manage_lab(request, init_global=False, loc=_id)

def _save_dailyreport(dailyreport_id, site=None, date=None, warn=None, carriages=None, imgs=None):
    if dailyreport_id is None:
        if site is not None:
            try:
                site = models.Site.objects.get(name=site)
            except Exception as e:
                _order = models.Site.objects.all().last().order + 1
                site = models.Site.objects.create(name=site, order=_order)
            _new = models.DailyReport(
                date=date if date is not None else datetime.datetime.now(),
                site=site,
                warn=warn if warn is not None else "",
                carriages_count=carriages if carriages is not None else "",
                imgs=imgs if imgs is not None else "".encode()
            )
            _new.save()
            return _new.id
        else:
            return -1
    else:
        dailyreport_obj = models.DailyReport.objects.get(id=dailyreport_id)
        site = models.Site.objects.get(name=site)

        if site is not None:
            dailyreport_obj.site = site
        if date is not None:
            dailyreport_obj.date = date
        if warn is not None:
            dailyreport_obj.warn = warn
        if carriages is not None:
            dailyreport_obj.carriages_count = carriages
        if imgs is not None:
            dailyreport_obj.imgs = imgs
        dailyreport_obj.save()
        return dailyreport_obj.id

def _save_dailyreportmeta(date, site, problem, track):
    _new = models.DailyReport_Meta(
        date=date,
        site=site,
        problem=problem,
        track=track
    )
    _new.save()

def _save_dailyreportreason(dailyreport_id, reason):
    _dailyreport_obj = models.DailyReport.objects.get(id=dailyreport_id)
    _dailyreport_obj.reason.clear()
    _reasons = [models.Reason.objects.get(
        name=x) for x in reason if x != '']
    for r in _reasons:
        _dailyreport_obj.reason.add(r)
    _dailyreport_obj.save()

def daily_save_data(request):

    try:
        request_data = request.POST['data'].split('@@@@@')
        _id = request_data[0]
        _site = request_data[1]
        _carriages = request_data[2]
        _warn = request_data[3]
        _problem = request_data[4]
        _track = request_data[5]
        _reason = [x.strip() for x in str(request_data[6]).split('、')]

        log.info("daily_save_data > 用户（ " + request.user.username + ' )')
        id = _save_dailyreport(
            _id if _id != 'new' else None,
            site=_site,
            date=datetime.datetime.now() if _id =='new' else None,
            carriages=_carriages,
            warn=_warn
        )
        _save_dailyreportmeta(
            datetime.datetime.now(),
            models.Site.objects.get(name=_site),
            _problem,
            _track
        )
        _save_dailyreportreason(
            id,
            _reason
        )
        log.info("daily_save_data > 保存成功 " + repr(_id) + " -> " + repr(id))
        return daily_manage_lab(request, init_global=False)
    except:
        log.info("daily_save_data > 保存失败" + repr(_id) + " -> " + repr(id))
        return daily_manage_lab(request, init_global=False)

def daily_get_pic(request):
    log.info("daily_get_pic > " + request.user.username)
    _id = request.POST['id']
    log.info("daily_get_pic > 获取图片 > " + repr(_id))
    _dr = models.DailyReport.objects.get(id=_id)
    return HttpResponse(str(_dr.imgs, encoding='utf-8'))

def daily_detail_img(request, _id):
    _data_info = models.DailyReport.objects.get(id=_id)
    _title = _datetime_format(date=_data_info.date)
    _r = str(_data_info.imgs, encoding='utf-8')

    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_detail_img',
                {
                    'title': _data_info.site.name + '  ' + _title,
                    'item': _r,
                }
            ),
            'user': request.user,

        }
    )

def date_now(request):
    return HttpResponse(_datetime_format(mode=2).encode())

def _get_range_date(date, _startwith=8):
    if date.hour >= _startwith:
        # now -> 2018-01-22 08:10:00
        # 2018-01-21 08:00:00 ~ 2018-01-22 08:00:00
        _delta = timedelta(days=-1)
        _start_date = datetime.datetime.strptime((date + _delta).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                                 '%Y-%m-%d %H:%M:%S')
        _end_date = datetime.datetime.strptime(date.strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                               '%Y-%m-%d %H:%M:%S')
    else:
        # now -> 2018-01-22 07:50:00
        # 2018-01-20 08:00:00 ~ 2018-01-21 08:00:00
        _delta1 = timedelta(days=-2)
        _delta2 = timedelta(days=-1)
        _start_date = datetime.datetime.strptime((date + _delta1).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                                 '%Y-%m-%d %H:%M:%S')
        _end_date = datetime.datetime.strptime((date + _delta2).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                               '%Y-%m-%d %H:%M:%S')

    return _start_date, _end_date

def daily_delete_selected(request):
    ids = [int(x.split('_')[1]) for x in request.POST['data'].split('@@@@@')[1:]]
    models.DailyReport.objects.filter(id__in=ids).delete()
    log.info("daily_delete_selected > 用户（ " + request.user.username + ' )')
    log.info("daily_delete_selected > IP地址：" + request.META['REMOTE_ADDR'])
    log.info("daily_delete_selected > 删除 ( " + repr(ids) + " )")
    return daily_manage_lab(request, init_global=False)

def daily_confirm_selected(request):
    ids = [int(x.split('_')[1]) for x in request.POST['data'].split('@@@@@')[1:]]
    for dr in models.DailyReport.objects.filter(id__in=ids):
        dr.status = True
        dr.save()
    log.info("daily_confirm_selected > 用户（ " + request.user.username + ' )')
    log.info("daily_confirm_selected > IP地址：" + request.META['REMOTE_ADDR'])
    log.info("daily_confirm_selected > 发布 ( " + repr(ids) + " )")
        
    return daily_manage_lab(request, init_global=False)

def daily_unconfirm_selected(request):
    ids = [int(x.split('_')[1]) for x in request.POST['data'].split('@@@@@')[1:]]
    for dr in models.DailyReport.objects.filter(id__in=ids):
        dr.status = False
        dr.save()
    log.info("daily_unconfirm_selected > 用户（ " + request.user.username + ' )')
    log.info("daily_unconfirm_selected > IP地址：" + request.META['REMOTE_ADDR'])
    log.info("daily_unconfirm_selected > 取消发布 ( " + repr(ids) + " )")

    return daily_manage_lab(request, init_global=False)

def daily_save_pic(request):
    try:
        drObjId = request.POST['data'].split('@@@@@')[0]
        contents = request.POST['data'].split('@@@@@')[1]
        obj = models.DailyReport.objects.get(id=drObjId)
        obj.imgs = str(contents).encode()
        obj.save()
        return HttpResponse(True)
    except:
        return HttpResponse(False)



def daily_all_confirm(request):
    x = datetime.datetime.now() if _r_start_date_ is None else datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    y = datetime.datetime.now() if _r_end_date_ is None else datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    _data_ = models.DailyReport.objects.filter(date__range=(x, y))
    for data in _data_:
        data.status = True
        data.save()
    log.info("daily_all_confirm > 用户（ " + request.user.username + ' )')
    log.info("daily_all_confirm > IP地址：" + request.META['REMOTE_ADDR'])
    log.info("daily_all_confirm > 发布 ( " + repr([x[0] for x in _data_.values_list('id')]) + " )")

    return daily_manage_lab(request, init_global=False)

def daily_all_unconfirm(request):
    x = datetime.datetime.now() if _r_start_date_ is None else datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    y = datetime.datetime.now() if _r_end_date_ is None else datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    _data_ = models.DailyReport.objects.filter(date__range=(x, y))
    for data in _data_:
        data.status = False
        data.save()
    log.info("daily_all_unconfirm > 用户（ " + request.user.username + ' )')
    log.info("daily_all_unconfirm > IP地址：" + request.META['REMOTE_ADDR'])
    log.info("daily_all_unconfirm > 取消发布 ( " + repr([x[0] for x in _data_.values_list('id')]) + " )")

    return daily_manage_lab(request, init_global=False)

def daily_all_delete(request):
    log.info("daily_all_delete > 用户（ " + request.user.username + ' )')
    log.info("daily_all_delete > IP地址：" + request.META['REMOTE_ADDR'])
    x = datetime.datetime.now() if _r_start_date_ is None else datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    y = datetime.datetime.now() if _r_end_date_ is None else datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    delete_rows = models.DailyReport.objects.filter(date__range=(x, y))
    log.info("daily_all_delete > 删除全部 ( " + repr([x[0] for x in delete_rows.values_list('id')]) + " )")
    delete_rows.delete()
    # models.DailyReport.objects.filter(date__range=(x, y)).delete()
    return daily_manage_lab(request, init_global=False)


def data_init(request):

    init_reason = True
    init_site = True
    init_warn = True

    if init_reason:
        _reason_ = [
            ['图像质量', 0],
            ['截图不准', 0],
            ['TOEC服务', 0],
            ['算法本身', 0],
            ['其他', 0],
        ]

        for reason in _reason_:
            _new = models.Reason(name=reason[0], pid=reason[1])
            _new.save()

    if init_site:
        _site_ = [
            ['杨柳青', 'ylq', '北京局'],
            ['静海', 'jh', '北京局'],
            ['唐官屯', 'tgt', '北京局'],
            ['虎石台', 'hst', '沈阳局'],
            ['炎方', 'yf', '昆明局'],
            ['江都', 'jd', '上海局'],
            ['南莫', 'nm', '上海局'],
            ['泰州西', 'tzx', '上海局'],
            ['扬州东', 'yzd', '上海局'],
            ['白浦', 'bp', '上海局'],
            ['六合', 'lh', '上海局'],
            ['浦口北', 'pkb', '上海局'],
            ['如皋', 'rg', '上海局'],
            ['殷庄', 'yz', '上海局'],
            ['姜堰', 'jy', '上海局'],
            ['饮马峡', 'ymx', '青藏公司'],
            ['小桥', 'xq', '青藏公司'],
            ['双寨', 'sz', '青藏公司'],
            ['柯柯', 'kk', '青藏公司'],
            ['海石湾', 'hsw', '青藏公司'],
            ['哈尔盖', 'heg', '青藏公司'],
            ['察尔汗', 'ceh', '青藏公司'],
            ['那曲', 'nq', '青藏公司'],
            ['拉萨', 'ls', '青藏公司'],
            ['查汗诺', 'chn', '青藏公司'],
            ['罗江', 'lj', '成都局'],
        ]

        for site in _site_:
            _new = models.Site(name=site[0], code=site[1]+site[0], bureau=site[2], order=_site_.index(site))
            _new.save()

    if init_warn:

        _warn_ = [
            '车门开启',
            '客车车门开启',
            '异物',
            '尾管未吊起',
            '动车注水口',
            '车厢连接处异物',
        ]

        for warn in _warn_:
            _new = models.Warn(name=warn)
            _new.save()


    return HttpResponse(status=200)
