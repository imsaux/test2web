# -*- encoding:utf-8 -*-
from django.forms import *
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
import locale
# excel
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
# 文件下载
from django.utils.http import urlquote
from django.http import FileResponse

# 登录表单模型
class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

# 注册表单模型
class UserRegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    is_staff = forms.BooleanField(label='管理员权限', widget=forms.CheckboxInput(), required=False)


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
                if user.is_staff:
                    return daily_manage(request)
                else:
                    return daily_view(request)
            else:
                return HttpResponseRedirect('/login/')
    else:
        uf = UserForm()
    return render_to_response('login.html', {'uf': uf})

# 注册
def register(request):
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
            except Exception as e:
                urf = UserRegisterForm()
                return render_to_response('register.html', {'uf': urf})
            return HttpResponseRedirect('/login/')
    else:
        urf = UserRegisterForm()
        return render_to_response('register.html', {'uf': urf})


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
    _select_site = [x.name for x in models.Site.objects.all()]
    return get_data(request, _site=_select_site[0])


def get_data(request, _site=None, _date=None):
    locale.setlocale(locale.LC_CTYPE, 'chinese')
    data = list()
    _select_site = [x.name for x in models.Site.objects.all()]
    if _date is None:
        _date = datetime.datetime.now()
    try:
        all_info = models.Info.objects.filter(
            site=models.Site.objects.get(name=_site), datetime=_date.date())
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
    try:
        all_warning = models.Warning.objects.filter(site=models.Site.objects.get(name=_site), date__year=_date.year,
                                                date__month=_date.month, date__day=_date.day).order_by('algo__pid')

        P_algo = sorted(
            set([y[0]['pid'] for y in [x.algo.all().values('pid') for x in all_warning]]))
        _current_parent_algo = None
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

    except Exception as e:
        pass

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
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
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


def _datetime_format(date=datetime.datetime.now(), mode=1):
    if mode == 1:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日'
    elif mode == 2:
        return date.strftime('%Y%m%d%H%M%S')
    elif mode == 3:
        return date.strftime('%m/%d/%Y')
    elif mode == 4:
        return str(date.year) + '年' + str(date.month) + '月' + str(date.day) + '日 ' + str(date.hour).zfill(2) + ':' + str(date.minute).zfill(2) + ':' + str(date.second).zfill(2)


def _auto_create_daily_info(date=datetime.datetime.now()):
    # 自动创建
    # _return = list()
    _all_site_ = [x.code for x in models.Site.objects.all().order_by('order')]
    _range_from, _range_to = _get_range_date(date)
    for site in _all_site_:
        _site_obj = models.Site.objects.get(code=site)
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
            # _return.append([_site_obj.name, carriages, warning, '无', '无', _new.id, _new.status])


def _get_daily_data(_from=datetime.datetime.now(), _to=datetime.datetime.now(), _site_name=None, _reasons=None, _is_confirm=False):
    _return = list()
    if _r_reasons_ is not None:
        _reasons = _r_reasons_
    if _r_site_ is not None:
        _site_name = _r_site_
    if _r_start_date_ is not None:
        _from = datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    if _r_end_date_ is not None:
        _to = datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    if _site_name is None or _site_name == '全部':
        _all_site_ = [x.code for x in models.Site.objects.all().order_by('order')]
    else:
        _all_site_ = [models.Site.objects.get(name=_site_name).code]
    _all_data_ = models.DailyReport.objects.filter(date__range=(_from, _to))
    _sitenames_dailyreport = [models.Site.objects.get(id=x['site']).code for x in
                              _all_data_.values('site').distinct()]
    for site in _all_site_:
        _site_obj = models.Site.objects.get(code=site)
        if site in _sitenames_dailyreport: # 有日报表数据
            _site_data_ = _all_data_
            if _is_confirm is True:
                _site_data_ = _site_data_.filter(site=_site_obj, status=True)
            else:
                _site_data_ = _site_data_.filter(site=_site_obj)
            if _reasons is None or len(_reasons) == 0 or '全部' in _reasons:
                pass
            else:
                _site_data_ = _site_data_.filter(reason__name__in=_reasons)
            for data in _site_data_:
                carriages_count = data.carriages_count
                warn = data.warn
                _data_meta = models.DailyReport_Meta.objects.filter(site=_site_obj, date=data.date)
                if len(_data_meta) > 0:
                    _return.append(
                        [
                            _site_obj.name,
                            carriages_count,
                            warn,
                            _data_meta.last().problem,
                            _data_meta.last().track,
                            data.id,
                            data.status,
                            '、'.join([x['name'] for x in data.reason.all().values('name')]),
                            _datetime_format(date=data.date, mode=3),
                            _site_obj.bureau,
                        ]
                    )
                else:
                    _return.append(
                        [
                            _site_obj.name,
                            carriages_count,
                            warn,
                            '无',
                            '无',
                            data.id,
                            data.status,
                            '、'.join([x['name'] for x in data.reason.all().values('name')]),
                            _datetime_format(date=data.date, mode=3),
                            _site_obj.bureau,
                        ]
                    )
    return _return


def _search_session(request):
    pass


global _r_start_date_, _r_end_date_, _r_site_, _r_reasons_
_r_start_date_ = None
_r_end_date_ = None
_r_site_ = None
_r_reasons_ = None


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
    _sites = ['全部'] + [x.name for x in models.Site.objects.all().order_by('order')]
    _reasons = ['全部'] + [x.name for x in models.Reason.objects.all()]

    if r_site == '全部':
        all_data = _get_daily_data(_from=_from, _to=_to, _reasons=r_reasons)
    else:
        all_data = _get_daily_data(_from=_from, _to=_to, _site_name=r_site,  _reasons=r_reasons)


    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_manage',
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




def daily_view(request, _date=datetime.datetime.now()):
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
def daily_manage(request, _date=datetime.datetime.now(), init_global=True, loc=None):
    _js = r"""<script src="/static/js/location.js"></script>"""
    if init_global:
        _init_global()
    _range_from, _range_to = _get_range_date(_date)
    _sites = ['全部'] + [x.code for x in models.Site.objects.all().order_by('order')]
    _reasons = ['全部'] + [x.name for x in models.Reason.objects.all()]

    all_data = _get_daily_data()
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_manage',
                {
                    'title': _datetime_format(date=_range_to),
                    'data': all_data,
                    'date_now': _datetime_format(mode=3),
                    'all_site': _sites,
                    'error_reason': _reasons,
                    'q_site': '全部' if _r_site_ is None else _r_site_,
                    'q_reason': list() if _r_reasons_ is None else _r_reasons_,
                    'q_start_date': _datetime_format(mode=3) if _r_start_date_ is None else _r_start_date_,
                    'q_end_date': _datetime_format(mode=3) if _r_end_date_ is None else _r_end_date_,
                    'loc': int(loc) if loc is not None else None,

                }
            ),
            'user': request.user,
            'body_script': _js,
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

def daily_create_single(request):
    # _site = request.POST['r_site']
    _site_obj = models.Site.objects.all().first()
    # _site_obj = models.Site.objects.get(code=_site)
    _meta_obj = models.DailyReport_Meta.objects.filter(site=_site_obj.id)
    return daily_edit(request, _site=_site_obj.name, _site_problem=_meta_obj.last().problem if len(_meta_obj)>0 else "无", _site_track=_meta_obj.last().track  if len(_meta_obj)>0 else "无")

def daily_create_all(request):
    _auto_create_daily_info()
    return daily_manage(request)

def daily_copy(request, _id):
    return daily_edit(request, _id=_id, _is_copy=True)

def daily_delete(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.delete()
    return daily_manage(request, init_global=False)

def daily_confirm(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.status = True
    obj.save()
    return daily_manage(request, init_global=False, loc=_id)


def daily_unconfirm(request, _id):
    obj = models.DailyReport.objects.get(id=_id)
    obj.status = False
    obj.save()
    return daily_manage(request, init_global=False, loc=_id)


def _save_dailyreport(self, dailyreport_id, site, date, warn=None, carriages=None, imgs=None):
    if dailyreport_id is None:
        _new = models.DailyReport(
            date=date,
            site=site,
            warn=warn if warn is not None else "",
            carriages_count=carriages if carriages is not None else "",
            imgs=imgs if imgs is not None else ""
        )
        _new.save()
        return _new.id
    else:
        dailyreport_obj = models.DailyReport.objects.get(id=dailyreport_id)
        if warn is not None:
            dailyreport_obj.warn = warn
        if carriages is not None:
            dailyreport_obj.carriages_count = carriages
        if imgs is not None:
            dailyreport_obj.imgs = imgs
        dailyreport_obj.save()
        return dailyreport_obj.id


def _save_dailyreportmeta(self, date, site, problem, track):
    _new = models.DailyReport_Meta(
        date=date,
        site=site,
        problem=problem,
        track=track
    )
    _new.save()

def _save_dailyreportreason(self, dailyreport_id, reason):
    _reasons = [models.Reason.objects.get(
        name=x) for x in reason]
    _dailyreport_obj = models.DailyReport.objects.get(id=dailyreport_id)
    _dailyreport_obj.reason.clear();
    for r in _reasons:
        _dailyreport_obj.reason.add(r)


def daily_save(request, _id):
    try:
        _site = models.Site.objects.get(name=str(request.POST['r_sites']))
        _date = datetime.datetime.strptime(request.POST['r_date'], '%m/%d/%Y')
        _carriages = int(request.POST['r_carriages'])
        _imgs = str(request.POST['r_remark']).encode()
        _warn = str(request.POST['r_warning'])
        _problem = request.POST['r_problem']
        _track = request.POST['r_track']
        _reason = request.POST.getlist('r_reason')
        id = _save_dailyreport(
            _id if _id != '-1' else None,
            _site,
            _date,
            carriages=_carriages,
            warn=_warn,
            imgs=_imgs
        )
        _save_dailyreportmeta(
            _date,
            _site,
            _problem,
            _track
        )
        _save_dailyreportreason(
            id,
            _reason
        )
    except Exception as e:
        pass

    return daily_manage(request, loc=_id)


def daily_detail_img(request, _id):
    _data_info = models.DailyReport.objects.get(id=_id)
    _range_from, _range_to = _get_range_date(datetime.datetime.now())

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

def daily_edit(request, _id=None, _site=None,  _site_problem='无', _site_track='无', _is_copy=False):
    _js = r"""<script src="/static/js/daily_edit.js"></script>"""
    _range_from, _range_to = _get_range_date(datetime.datetime.now())
    _reasons = [x.name for x in models.Reason.objects.all()]
    _data_ = list()
    _sites = [x.name for x in models.Site.objects.all()]

    if _id is None:
        _data_= [
            '全部',
            '0',
            '无',
            _site_problem,
            _site_track,
            '',
            -1,
            _datetime_format(mode=3),
            [],
        ]

    else:

        _report_data = models.DailyReport.objects.get(id=_id)
        _meta_data = models.DailyReport_Meta.objects.filter(site=_report_data.site, date=_report_data.date).last()
        _problem = _meta_data.problem if _meta_data is not None else '无'
        _track = _meta_data.track if _meta_data is not None else '无'
        _imgs = str(_report_data.imgs, encoding='utf-8')
        _data_ = [
            _report_data.site.name,
            _report_data.carriages_count,
            _report_data.warn,
            _problem,
            _track,
            _imgs,
            _report_data.id if not _is_copy else -1,
            _datetime_format(date=_report_data.date, mode=3),
            [x.name for x in _report_data.reason.all()],
        ]
    return render_to_response(
        'base.html',
        {
            'box_content': _redirect(
                'daily_edit',
                {
                    'title': '编辑记录',
                    'all_site': _sites,
                    'date_now': _datetime_format(mode=3),
                    'error_reason': _reasons,
                    'data': _data_,
                    # 'single': True if _id is None else False,
                }
            ),
            'user': request.user,
            'body_script': _js,
        }
    )


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

def test_test(request):
    return HttpResponse(content=b'haha')

#
# def warning_detail(request, _date, _site, _algo, _line, _err_type):
#     _date = datetime.datetime.strptime(_date, '%Y年%m月%d日')
#     all_warning = models.Warning.objects.filter(
#         warning_type=_err_type,
#         algo=models.Algo.objects.get(name=_algo),
#         line=_line,
#         date=_date,
#         site=models.Site.objects.get(name=_site),
#     )
#     data = list()
#     for w in all_warning:
#         _this = list()
#         _this.append(_datetime_format(date=w.date))
#         _this.append(w.site.name)
#         _this.append(w.line)
#         _this.append(w.kind.name)
#         _this.append(w.side)
#         _this.append(w.warning_type)
#         _this.append(w.algo.all().values('name')[0]['name'])
#         _this.append('、'.join([x['name']
#                                for x in w.reason.all().values('name')]))
#         _this.append('/' + w.pic.name)
#         data.append(_this)
#
#     return render_to_response(
#         'base.html',
#         {
#             'box_content': _redirect(
#                 'detail',
#                 {
#                     'detail_data': data,
#                 }
#             ),
#             'user': request.user,
#         }
#     )


# def search_warning(request):
#     _date = request.POST['r_date']
#     _to_date = datetime.datetime.strptime(_date, '%m/%d/%Y')
#     _site = request.POST['r_site']
#     return get_data(request, _site, _to_date)
#

# def add_info(request):
#     _date = datetime.datetime.strptime(request.POST['r_date'], '%m/%d/%Y')
#     _site = models.Site.objects.get(name=request.POST['r_site'])
#     _sx_h_lie = int(request.POST['sx_h_lie']
#                     ) if request.POST['sx_h_lie'] != '' else 0
#     _sx_h_liang = int(request.POST['sx_h_liang']
#                       ) if request.POST['sx_h_liang'] != '' else 0
#     _sx_k_lie = int(request.POST['sx_k_lie']
#                     ) if request.POST['sx_k_lie'] != '' else 0
#     _sx_k_liang = int(request.POST['sx_k_liang']
#                       ) if request.POST['sx_k_liang'] != '' else 0
#     _xx_h_lie = int(request.POST['xx_h_lie']
#                     ) if request.POST['xx_h_lie'] != '' else 0
#     _xx_h_liang = int(request.POST['xx_h_liang']
#                       ) if request.POST['xx_h_liang'] != '' else 0
#     _xx_k_lie = int(request.POST['xx_k_lie']
#                     ) if request.POST['xx_k_lie'] != '' else 0
#     _xx_k_liang = int(request.POST['xx_k_liang']
#                       ) if request.POST['xx_k_liang'] != '' else 0
#     _new = models.Info(
#         datetime=_date,
#         site=_site,
#         sx_h_liang=_sx_h_liang,
#         sx_h_lie=_sx_h_lie,
#         sx_k_liang=_sx_k_liang,
#         sx_k_lie=_sx_k_lie,
#         xx_h_liang=_xx_h_liang,
#         xx_h_lie=_xx_h_lie,
#         xx_k_liang=_xx_k_liang,
#         xx_k_lie=_xx_k_lie,
#     )
#     _new.save()
#     return stat_page(request)


# def add_warning(request):
#     # if request.Method == 'POST':
#     _date = request.POST['r_date']
#     _to_date = datetime.datetime.strptime(_date, '%m/%d/%Y')
#     _site = models.Site.objects.get(name=request.POST['r_site'])
#     _kind = models.Kind.objects.get(name=request.POST['r_kind'])
#     _side = request.POST['r_side']
#     _line = request.POST['r_line']
#     _pic = request.FILES['r_pic']
#     _type = request.POST['r_type']
#     _algo = models.Algo.objects.get(name=request.POST['r_algo_type'])
#     try:
#         _add = models.Warning(
#             date=_to_date,
#             site=_site,
#             side=_side,
#             line=_line,
#             kind=_kind,
#             warning_type=_type,
#             pic=_pic,
#         )
#         _add.save()
#         _add.algo.add(_algo)
#         if _type != '真实':
#             _reasons = [models.Reason.objects.get(
#                 name=x) for x in request.POST.getlist('r_reason')]
#             for r in _reasons:
#                 _add.reason.add(r)
#
#     except Exception as e:
#         logic.to_log('error', repr(e))
#     finally:
#         return warning_page(request)

def daily_delete_selected(request):
    ids = [int(x) for x in request.POST['selected'].split(',')[1:]]
    models.DailyReport.objects.filter(id__in=ids).delete()
    return daily_manage(request, init_global=False)

def daily_confirm_selected(request):
    ids = [int(x) for x in request.POST['selected'].split(',')[1:]]
    for dr in models.DailyReport.objects.filter(id__in=ids):
        dr.status = True
        dr.save()
    return daily_manage(request, init_global=False)

def daily_unconfirm_selected(request):
    ids = [int(x) for x in request.POST['selected'].split(',')[1:]]
    for dr in models.DailyReport.objects.filter(id__in=ids):
        dr.status = False
        dr.save()
    return daily_manage(request, init_global=False)

def daily_all_confirm(request):
    x = datetime.datetime.now() if _r_start_date_ is None else datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    y = datetime.datetime.now() if _r_end_date_ is None else datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    _data_ = models.DailyReport.objects.filter(date__range=(x, y))
    for data in _data_:
        data.status = True
        data.save()
    return daily_manage(request, init_global=False)

def daily_all_unconfirm(request):
    x = datetime.datetime.now() if _r_start_date_ is None else datetime.datetime.strptime(_r_start_date_, '%m/%d/%Y')
    y = datetime.datetime.now() if _r_end_date_ is None else datetime.datetime.strptime(_r_end_date_, '%m/%d/%Y')
    _data_ = models.DailyReport.objects.filter(date__range=(x, y))
    for data in _data_:
        data.status = False
        data.save()
    return daily_manage(request, init_global=False)


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
