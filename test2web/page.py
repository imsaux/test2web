# -*- encoding:utf-8 -*-
from django.forms import *
from . import logic
from . import models
from datetime import datetime, tzinfo, timedelta, timezone
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.db.models import Max, Min, Sum
import datetime


# 定义表单模型
class UserForm(forms.Form):
    username = forms.CharField(label='用户名：', max_length=100)
    password = forms.CharField(label='密码：', widget=forms.PasswordInput())


# 登录
def login(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # 获取的表单数据与数据库进行比较
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return daily_view(request)
            else:
                return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
    return render_to_response('login.html', {'uf': uf})


def register(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            try:
                user = User.objects.create_user(username=username)
                user.set_password(password)
                user.save()
            except Exception as e:
                uf = UserForm()
                return render_to_response('register.html', {'uf': uf})
            return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
        return render_to_response('register.html', {'uf': uf})


def _redirect(page, params):
    _page = page + '.html'
    return render_to_response(
        _page,
        params
    ).content.decode('utf8')


def warning_page(request):
    _algo = [x.name for x in models.Algo.objects.exclude(pid=0)]
    _kind = [x.name for x in models.Kind.objects.all()]
    _site = [x.name for x in models.Site.objects.all()]
    _reason = [x.name for x in models.Reason.objects.all()]
    _date = datetime.datetime.now(tz=timezone(
        timedelta(hours=8))).strftime('%m/%d/%Y')
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'add_warning',
                {
                    'algo_type': _algo,
                    'train_kind': _kind,
                    'error_reason': _reason,
                    'date_now': _date,
                    'all_site': _site,
                    'user': request.user,
                }
            ),
            'user': request.user,
        }
    )


def stat_page(request):
    return get_data(request)


def get_data(request, _site=None, _date=None):
    # locale.setlocale(locale.LC_CTYPE, 'chinese')
    data = list()
    if _date is None:
        _date = datetime.datetime.now(tz=timezone(timedelta(hours=8)))
    all_warning = models.Warning.objects.filter(site=models.Site.objects.get(name=_site), date__year=_date.year,
                                                date__month=_date.month, date__day=_date.day).order_by('algo__pid')
    try:
        all_info = models.Info.objects.filter(
            site=models.Site.objects.get(name=_site), date=_date)
        _info = [
            all_info.last().sx_h_lie,
            all_info.last().sx_h_liang,
            all_info.last().sx_k_lie,
            all_info.last().sx_k_liang,
            all_info.last().xx_h_lie,
            all_info.last().xx_h_liang,
            all_info.last().xx_k_lie,
            all_info.last().xx_k_liang,
        ]
    except Exception as e:
        _info = [0] * 8
    P_algo = sorted(
        set([y[0]['pid'] for y in [x.algo.all().values('pid') for x in all_warning]]))
    _current_parent_algo = None
    _select_site = [x.name for x in models.Site.objects.all()]
    _index = 1
    for _p in P_algo:
        this_p_algo = all_warning.filter(algo__pid=_p)
        _algo = set([y[0]['id'] for y in [x.algo.all().values('id')
                                          for x in this_p_algo]])
        this_p_algo_count = len(_algo)
        for _a in _algo:
            _this = list()
            this_algo = all_warning.filter(algo=_a)
            this_algo_obj = models.Algo.objects.get(id=_a)
            this_algo_obj_name = this_algo_obj.name
            this_algo_parent_obj = models.Algo.objects.get(
                id=this_algo_obj.pid)
            this_algo_parent_obj_name = this_algo_parent_obj.name
            if _current_parent_algo is None or _current_parent_algo != this_algo_parent_obj_name:
                _this.append(str(this_p_algo_count))
                _this.append(this_algo_parent_obj_name)
                _current_parent_algo = this_algo_parent_obj_name
            else:
                _this.append('')
                _this.append('')
            _this.append(this_algo_obj_name)
            line_1_real = len(this_algo.filter(line='上行', warning_type='真实'))
            line_2_real = len(this_algo.filter(line='下行', warning_type='真实'))
            line_1_err = len(this_algo.filter(line='上行', warning_type='误报'))
            line_2_err = len(this_algo.filter(line='下行', warning_type='误报'))
            line_1_miss = len(this_algo.filter(line='上行', warning_type='漏报'))
            line_2_miss = len(this_algo.filter(line='下行', warning_type='漏报'))
            line_1_total = line_1_real + line_1_err
            line_2_total = line_2_real + line_2_err
            _this.append(line_1_total)
            _this.append(line_1_real)
            _this.append(line_1_err)
            _this.append(line_1_miss)
            _this.append(line_2_total)
            _this.append(line_2_real)
            _this.append(line_2_err)
            _this.append(line_2_miss)
            data.append(_this)
            _index += 1
    _js = r"""<script src="/static/js/my/stat.js"></script>"""
    _css = r"""<link href="/static/css/my/dict.css" rel="stylesheet">"""
    _rMenu = r"""<div id="rMenu"><img src="/static/img/gallery/photo2.jpg" /></div>"""
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'stat',
                {
                    'body_script': _js,
                    'body_style': _css,
                    'body_root_content': _rMenu,
                    'stat_data': data,
                    'data_date': _date.strftime('%Y') + '年' + _date.strftime('%m') + '月' + _date.strftime('%d') + '日',
                    'data_title': str(_date.month) + '月' + str(_date.day) + '日8时 - ' + str(_date.month) + '月' + str(
                        _date.day + 1) + '日8时',
                    'all_site': _select_site,
                    'current_site': _site,
                    'date_now': _date.strftime('%m/%d/%Y'),
                    'info': _info,

                }
            ),
            'user': request.user,
        }
    )


def logout(request):
    auth.logout(request)
    return login(request)


def dict_page(request):
    _js = r"""<script src="/static/js/my/dict.js"></script>"""
    _css = r"""<link href="/static/css/my/dict.css" rel="stylesheet">"""
    _rMenu = r"""
        <div id="rMenu">
            <ul>
                <li id="m_add" onclick="addTreeNode();">增加节点</li>
                <li id="m_del" onclick="removeTreeNode();">删除节点</li>
                <li id="m_check" onclick="editTreeNode();">修改节点</li>
            </ul>
        </div>"""
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'dict',
                {
                }
            ),
            'body_script': _js,
            'body_style': _css,
            'body_root_content': _rMenu,
            'user': request.user,
        },
    )


def info_page(request):
    _date = datetime.datetime.now(tz=timezone(
        timedelta(hours=8))).strftime('%m/%d/%Y')
    _site = [x.name for x in models.Site.objects.all()]
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'add_info',
                {
                    'date_now': _date,
                    'all_site': _site,
                }
            ),
            'user': request.user,
        }
    )

    _set = [x.name for x in models.Algo.objects.exclude(pid=0)]
    return render_to_response(
        'add_warning.html',
        {
            'algo_type': _set,
        }
    )


def import_data(request):
    # 接收4G站点数据
    site_name = request.POST['站点']
    _line_1_trains = request.POST['1列数']
    _line_2_trains = request.POST['2列数']
    _line_1_carriages = request.POST['1辆数']
    _line_2_carriages = request.POST['2辆数']

    new_status = models.ClientStatus(
        datetime=datetime.datetime.strptime(
            request.POST['datetime'], '%Y%m%d%H%M%S'),
        site=site_name,
        line_1_trains=_line_1_trains,
        line_1_carriages=_line_1_carriages,
        line_2_trains=_line_2_trains,
        line_2_carriages=_line_2_carriages,
    )
    new_status.save()
    for key in request.POST.keys():
        if key in ['站点', '1列数', '2列数', '1辆数', '2辆数', 'datetime']:
            pass
        else:
            _key = key
            if ',' in key:          # support 2.5
                _key = key.split(',')[0]
            new_warning = models.ClientWarning(
                datetime=datetime.datetime.strptime(
                    request.POST['datetime'], '%Y%m%d%H%M%S'),
                site=site_name,
                algo=_key,
                count=int(request.POST[key])
            )
            new_warning.save()
    return HttpResponse(status=200)


def _datetime_format(date=datetime.datetime.now(), mode=1):
    if mode == 1:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日'
    elif mode == 2:
        return date.strftime('%Y%m%d%H%M%S')
    elif mode == 3:
        return date.strftime('%m/%d/%Y')
    elif mode == 4:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日 ' + str(date.hour).zfill(2) + ':' + str(date.minute).zfill(2) + ':' + str(date.second).zfill(2)


def _get_daily_data(date=datetime.datetime.now()):
    _return = list()

    # 日期输入合法性检查
    _range_from, _range_to = _get_range_date(date)

    # 列出站点
    _data_sites = models.ClientWarning.objects.filter(
        datetime__range=(_range_from, _range_to))
    _data_daily = models.DailyReport.objects.filter(date=_range_to.date())
    if len(_data_sites) > 0:
        _sites = [x['site'] for x in _data_sites.values('site').distinct()]
        for _site in _sites:    # 遍历每个站点信息
            _data_warning = models.ClientWarning.objects.filter(
                site=_site, datetime__range=(_range_from, _range_to))
            _data_status = models.ClientStatus.objects.filter(
                site=_site, datetime__range=(_range_from, _range_to))
            _columns = [x['algo']
                        for x in _data_warning.values('algo').distinct()]  # 列出报警类型
            if len(_columns) == 0:
                warning_str = '无'
            else:
                warning_str = ''
                for col in _columns:
                    if warning_str == '':
                        warning_str += str(col) + \
                            str(_data_warning.filter(algo=col).last().count)
                    else:
                        warning_str += ';' + \
                            str(col) + \
                            str(_data_warning.filter(algo=col).last().count)
            if len(_data_status) > 0:
                carriages_count = int(_data_status.values('line_1_carriages').last()[
                                      'line_1_carriages']) + int(_data_status.values('line_2_carriages').last()['line_2_carriages'])
            else:
                carriages_count = 0

            # 读取当日日报记录，若没有将新建
            try:

                _data_info = models.DailyReport.objects.get(
                    site=_site, date=_range_to.date())
                carriages_count = _data_info.carriages
                warning_str = _data_info.warning

            except:
                _last_info = models.DailyReport.objects.last()
                if _last_info is None:
                    _new = models.DailyReport(
                        site=_site,
                        date=_range_to.date(),
                        carriages=carriages_count,
                        warning=warning_str,
                        qa='无'.encode(),
                        track='无'.encode(),
                    )
                else:
                    _new = models.DailyReport(
                        site=_site,
                        date=_range_to.date(),
                        carriages=carriages_count,
                        warning=warning_str,
                        qa=_last_info.qa,
                        track=_last_info.track,
                    )
                _new.save()
            finally:
                _data_info = models.DailyReport.objects.get(
                    site=_site, date=_range_to.date())
                report_qa = str(_data_info.qa, encoding='utf-8')
                report_track = str(_data_info.track, encoding='utf-8')

            # 将一个站点的名称、过车辆数、报警记录与日报表中问题追踪及处理情况汇总并返回该列表
            _return.append([_site, carriages_count, warning_str, report_qa,
                            report_track, _data_info.id, _data_info.status])
        return _return
    elif len(_data_daily) > 0:
        for site in _data_daily:
            _return.append([site.site, site.carriages, site.warning, str(site.qa, encoding='utf-8'), str(site.track, encoding='utf-8'), site.id, site.status])
        return _return
    else:
        _sites = [x.name for x in models.Site.objects.all()]
        for site in _sites:

            _new = models.DailyReport(
                site=site,
                date=_range_to.date(),
                carriages=0,
                warning='无',
                qa='无'.encode(),
                track='无'.encode(),
            )
            _new.save()
            _data_info = models.DailyReport.objects.get(
                site=site, date=_range_to.date())
            carriages_count = _data_info.carriages
            warning_str = _data_info.warning
            report_qa = str(_data_info.qa, encoding='utf-8')
            report_track = str(_data_info.track, encoding='utf-8')
            _return.append([site, carriages_count, warning_str, report_qa,
                                        report_track, _data_info.id, _data_info.status])
        return _return


def daily_search(request):
    _range_from, _range_to = _get_range_date(datetime.datetime.now())

    _site = request.POST['r_site']
    _date = datetime.datetime.strptime(request.POST['r_date'], '%m/%d/%Y')
    _data = models.DailyReport.objects.get(site=_site, date=_date)
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_view',
                {
                    'title': _datetime_format(date=_range_to),
                    'data': [[_site, _data.carriages, _data.warning, str(_data.qa, encoding='utf-8'), str(_data.track, encoding='utf-8'), _data.id]],
                }
            ),
            'user': request.user,
        }
    )



def daily_view(request):
    _range_from, _range_to = _get_range_date(datetime.datetime.now())
    _data_sites = models.ClientWarning.objects.filter(
        datetime__range=(_range_from, _range_to))

    _sites = [x['site'] for x in _data_sites.values('site').distinct()]
    public_reports = models.DailyReport.objects.filter(
        date=_range_to, status=True)
    _return = list()
    for site in public_reports:
        _site = site.site
        _carriages = site.carriages
        _warning = site.warning
        _qa = str(site.qa, encoding='utf-8')
        _track = str(site.track, encoding='utf-8')
        _return.append([_site, _carriages, _warning, _qa, _track, site.id])
    if len(_return) == 0:
        _return = None
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_view',
                {
                    'title': _datetime_format(date=_range_to),
                    'data': _return,
                    'all_site': _sites,
                    'date_now': _datetime_format(mode=3),
                }
            ),
            'user': request.user,
        }
    )

@login_required
def daily_manage(request, _date=datetime.datetime.now()):
    _range_from, _range_to = _get_range_date(datetime.datetime.now())

    all_data = _get_daily_data(date=_date)
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_manage',
                {
                    'title': _datetime_format(date=_range_to),
                    'data': all_data,
                }
            ),
            'user': request.user,
        }
    )


def daily_delete(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.delete()
    return daily_manage(request)


def daily_confirm(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.status = True
    obj.save()
    return daily_manage(request)


def daily_unconfirm(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.status = False
    obj.save()
    return daily_manage(request)


def daily_save(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    try:
        obj.carriages = int(request.POST['carriages'])
    except Exception as e:
        pass
    try:
        obj.qa = str(request.POST['qa']).encode()
    except Exception as e:
        pass

    try:
        obj.track = str(request.POST['track']).encode()
    except Exception as e:
        pass

    obj.warning = request.POST['warning']
    obj.save()
    return daily_manage(request)


def daily_detail(request, _id, _mode):
    _data_info = models.DailyReport.objects.get(id=_id)
    _range_from, _range_to = _get_range_date(datetime.datetime.now())

    _title = _datetime_format(date=_range_to)
    _r = None
    if _mode == '0':
        _r = str(_data_info.qa, encoding='utf-8')
    elif _mode == '1':
        _r = str(_data_info.track, encoding='utf-8')

    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_qa_detail',
                {
                    'title': _data_info.site + '  ' + _title,
                    'item': _r,
                }
            ),
            'user': request.user,

        }
    )


def daily_edit(request, _id):
    _range_from = _get_range_date(datetime.datetime.now())[0]
    _range_to = _get_range_date(datetime.datetime.now())[1]
    _from_str = _datetime_format(date=_range_from, mode=4)
    _to_str = _datetime_format(date=_range_to, mode=4)
    _report_data = models.DailyReport.objects.get(id=_id)
    _qa = str(_report_data.qa, encoding='utf-8')
    _track = str(_report_data.track, encoding='utf-8')
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_edit',
                {
                    'title': _report_data.site + '  ' + ' - '.join([_from_str, _to_str]),
                    'data': [_report_data.site, _report_data.carriages, _report_data.warning, _qa, _track, _report_data.id],
                }
            ),
            'user': request.user,

        }
    )


def _get_range_date(date, _startwith=8):
    tz = timezone(timedelta(hours=8))
    _date = date.astimezone(tz=tz)
    if _date.hour >= _startwith:
        # now -> 2018-01-22 08:10:00
        # 2018-01-21 08:00:00 ~ 2018-01-22 08:00:00
        _delta = timedelta(days=-1)
        _start_date = datetime.datetime.strptime((_date + _delta).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                                 '%Y-%m-%d %H:%M:%S')
        _end_date = datetime.datetime.strptime(_date.strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                               '%Y-%m-%d %H:%M:%S')
    else:
        # now -> 2018-01-22 07:50:00
        # 2018-01-20 08:00:00 ~ 2018-01-21 08:00:00
        _delta1 = timedelta(days=-2)
        _delta2 = timedelta(days=-1)
        _start_date = datetime.datetime.strptime((_date + _delta1).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                                 '%Y-%m-%d %H:%M:%S')
        _end_date = datetime.datetime.strptime((_date + _delta2).strftime('%Y-%m-%d') + ' ' + str(_startwith).zfill(2) + ':00:00',
                                               '%Y-%m-%d %H:%M:%S')

    return _start_date, _end_date


def warning_detail(request, _date, _site, _algo, _line, _err_type, _user):
    _date = datetime.datetime.strptime(_date, '%Y年%m月%d日')
    all_warning = models.Warning.objects.filter(
        warning_type=_err_type,
        algo=models.Algo.objects.get(name=_algo),
        line=_line,
        date=_date,
        site=models.Site.objects.get(name=_site),
    )
    data = list()
    for w in all_warning:
        _this = list()
        _this.append(w.date.strftime('%Y年%m月%d日'))
        _this.append(w.site.name)
        _this.append(w.line)
        _this.append(w.kind.name)
        _this.append(w.side)
        _this.append(w.warning_type)
        _this.append(w.algo.all().values('name')[0]['name'])
        _this.append('、'.join([x['name']
                               for x in w.reason.all().values('name')]))
        _this.append('/' + w.pic.name)
        data.append(_this)

    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'detail',
                {
                    'detail_data': data,
                }
            ),
        }
    )


def search_warning(request, _user):
    _date = request.POST['r_date']
    _to_date = datetime.datetime.strptime(_date, '%m/%d/%Y')
    _site = request.POST['r_site']
    return get_data(request, _site, _to_date)


def add_info(request, _user):
    _date = datetime.datetime.strptime(request.POST['r_date'], '%m/%d/%Y')
    _site = models.Site.objects.get(name=request.POST['r_site'])
    _sx_h_lie = int(request.POST['sx_h_lie']
                    ) if request.POST['sx_h_lie'] != '' else 0
    _sx_h_liang = int(request.POST['sx_h_liang']
                      ) if request.POST['sx_h_liang'] != '' else 0
    _sx_k_lie = int(request.POST['sx_k_lie']
                    ) if request.POST['sx_k_lie'] != '' else 0
    _sx_k_liang = int(request.POST['sx_k_liang']
                      ) if request.POST['sx_k_liang'] != '' else 0
    _xx_h_lie = int(request.POST['xx_h_lie']
                    ) if request.POST['xx_h_lie'] != '' else 0
    _xx_h_liang = int(request.POST['xx_h_liang']
                      ) if request.POST['xx_h_liang'] != '' else 0
    _xx_k_lie = int(request.POST['xx_k_lie']
                    ) if request.POST['xx_k_lie'] != '' else 0
    _xx_k_liang = int(request.POST['xx_k_liang']
                      ) if request.POST['xx_k_liang'] != '' else 0
    _new = models.Info(
        date=_date,
        site=_site,
        sx_h_liang=_sx_h_liang,
        sx_h_lie=_sx_h_lie,
        sx_k_liang=_sx_k_liang,
        sx_k_lie=_sx_k_lie,
        xx_h_liang=_xx_h_liang,
        xx_h_lie=_xx_h_lie,
        xx_k_liang=_xx_k_liang,
        xx_k_lie=_xx_k_lie,
    )
    _new.save()
    return info_page(request, _user)


def add_warning(request, _user):
    # if request.Method == 'POST':
    _date = request.POST['r_date']
    _to_date = datetime.datetime.strptime(_date, '%m/%d/%Y')
    _site = models.Site.objects.get(name=request.POST['r_site'])
    _kind = models.Kind.objects.get(name=request.POST['r_kind'])
    _side = request.POST['r_side']
    _line = request.POST['r_line']
    _pic = request.FILES['r_pic']
    _type = request.POST['r_type']
    _algo = models.Algo.objects.get(name=request.POST['r_algo_type'])
    try:
        _add = models.Warning(
            date=_to_date,
            site=_site,
            side=_side,
            line=_line,
            kind=_kind,
            warning_type=_type,
            pic=_pic,
        )
        _add.save()
        _add.algo.add(_algo)
        if _type != '真实':
            _reasons = [models.Reason.objects.get(
                name=x) for x in request.POST.getlist('r_reason')]
            for r in _reasons:
                _add.reason.add(r)

    except Exception as e:
        logic.to_log('error', repr(e))
    finally:
        return warning_page(request)


def init(request):
    _r1 = models.Reason(pid=0, name='图像质量')
    _r2 = models.Reason(pid=0, name='截图不准')
    _r3 = models.Reason(pid=0, name='TOEC服务')
    _r4 = models.Reason(pid=0, name='算法本身')
    _r5 = models.Reason(pid=0, name='其他')
    _r1.save()
    _r2.save()
    _r3.save()
    _r4.save()
    _r5.save()

    _site1 = models.Site(name='杨柳青')
    _site2 = models.Site(name='静海')
    _site3 = models.Site(name='唐官屯')
    _site4 = models.Site(name='虎石台')
    _site5 = models.Site(name='炎方')
    _site6 = models.Site(name='江都')
    _site7 = models.Site(name='南莫')
    _site8 = models.Site(name='泰州西')
    _site9 = models.Site(name='扬州东')
    _site10 = models.Site(name='白浦')
    _site11 = models.Site(name='六合')
    _site12 = models.Site(name='浦口北')
    _site13 = models.Site(name='如皋')
    _site14 = models.Site(name='殷庄')
    _site15 = models.Site(name='饮马峡')
    _site16 = models.Site(name='小桥')
    _site17 = models.Site(name='双寨')
    _site18 = models.Site(name='柯柯')
    _site19 = models.Site(name='海石湾')
    _site20 = models.Site(name='哈尔盖')
    _site21 = models.Site(name='察尔汗')
    _site22 = models.Site(name='那曲')
    _site23 = models.Site(name='拉萨')
    _site24 = models.Site(name='查汗诺')
    _site1.save()
    _site2.save()
    _site3.save()
    _site4.save()
    _site5.save()
    _site6.save()
    _site7.save()
    _site8.save()
    _site9.save()
    _site10.save()
    _site11.save()
    _site12.save()
    _site13.save()
    _site14.save()
    _site15.save()
    _site16.save()
    _site17.save()
    _site18.save()
    _site19.save()
    _site20.save()
    _site21.save()
    _site22.save()
    _site23.save()
    _site24.save()

    #
    _kind1 = models.Kind(name='C（敞车）')
    _kind2 = models.Kind(name='P（篷车）')
    _kind3 = models.Kind(name='G（罐车）')
    _kind4 = models.Kind(name='N、X（平车）')
    _kind5 = models.Kind(name='W（毒品车）')
    _kind6 = models.Kind(name='B（冷藏车）')
    _kind1.save()
    _kind2.save()
    _kind3.save()
    _kind4.save()
    _kind5.save()
    _kind6.save()

    _algo1 = models.Algo(pid=0, name='图像算法（线阵左右侧图像）')
    _algo1.save()
    _algo11 = models.Algo(pid=_algo1.id, name='车门开启')
    _algo12 = models.Algo(pid=_algo1.id, name='客车车门开启')
    _algo13 = models.Algo(pid=_algo1.id, name='异物')
    _algo14 = models.Algo(pid=_algo1.id, name='尾管未吊起')
    _algo15 = models.Algo(pid=_algo1.id, name='动车注水口')
    _algo16 = models.Algo(pid=_algo1.id, name='车厢连接处异物')
    _algo11.save()
    _algo12.save()
    _algo13.save()
    _algo14.save()
    _algo15.save()
    _algo16.save()

    _algo17 = models.Algo(pid=_algo1.id, name='车窗开启')
    _algo18 = models.Algo(pid=_algo1.id, name='闲杂人员')
    _algo17.save()
    _algo18.save()

    _algo2 = models.Algo(pid=0, name='图像算法（线阵走形部图像）')
    _algo2.save()
    _algo21 = models.Algo(pid=_algo2.id, name='折角塞门关闭')
    _algo22 = models.Algo(pid=_algo2.id, name='闸链拉紧')
    _algo23 = models.Algo(pid=_algo2.id, name='风管断开')
    _algo24 = models.Algo(pid=_algo2.id, name='客车蓄电池盖开启')
    _algo25 = models.Algo(pid=_algo2.id, name='鞲鞴杆拉链拉紧')
    _algo26 = models.Algo(pid=_algo2.id, name='尾管未吊起（走行部检测）')
    _algo27 = models.Algo(pid=_algo2.id, name='折角塞门开启')
    _algo21.save()
    _algo22.save()
    _algo23.save()
    _algo24.save()
    _algo25.save()
    _algo26.save()
    _algo27.save()
