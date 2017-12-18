from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template.loader import get_template
from django.forms import *
from . import logic
from . import models
from datetime import datetime, tzinfo,timedelta, timezone

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
    _date = datetime.now(tz=timezone(timedelta(hours=8))).strftime('%m/%d/%Y')
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
                }
            ),
        }
    )

def stat_page(request):
    return get_data()

def get_data(_site='杨柳青', _date=None):
    data = list()
    if _date is None:
        _date = datetime.now(tz=timezone(timedelta(hours=8)))
    all_warning = models.Warning.objects.filter(site=models.Site.objects.get(name=_site), date__year=_date.year, date__month=_date.month, date__day=_date.day).order_by('algo__pid')
    try:
        all_info = models.Info.objects.get(site=models.Site.objects.get(name=_site), date=_date)
        _info = [
            all_info.sx_h_lie,
            all_info.sx_h_liang,
            all_info.sx_k_lie,
            all_info.sx_k_liang,
            all_info.xx_h_lie,
            all_info.xx_h_liang,
            all_info.xx_k_lie,
            all_info.xx_k_liang,
            ]
    except Exception as e:
        _info = [0]*8
    P_algo = sorted(set([y[0]['pid'] for y in [x.algo.all().values('pid') for x in all_warning]]))
    _current_parent_algo = None
    _select_site = [x.name for x in models.Site.objects.all()]
    _index = 1
    for _p in P_algo:
        this_p_algo = all_warning.filter(algo__pid=_p)
        _algo = set([y[0]['id'] for y in [x.algo.all().values('id') for x in this_p_algo]])
        this_p_algo_count = len(_algo)
        for _a in _algo:
            _this = list()
            this_algo = all_warning.filter(algo=_a)
            this_algo_obj = models.Algo.objects.get(id=_a)
            this_algo_obj_name = this_algo_obj.name
            this_algo_parent_obj = models.Algo.objects.get(id=this_algo_obj.pid)
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
    _rMenu = r"""
    <div id="rMenu">
    <img src="/static/img/gallery/photo2.jpg" />
</div>
"""

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
                    'data_date': _date.strftime('%Y年%m月%d日'),
                    'data_title': str(_date.month) + '月' + str(_date.day) + '日8时 - ' + str(_date.month) + '月' + str(_date.day + 1) + '日8时',
                    'all_site': _select_site,
                    'current_site': _site,
                    'date_now': _date.strftime('%m/%d/%Y'),
                    'info': _info,
                }
            ),
        }
    )

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

        }
    )

def info_page(request):
    _date = datetime.now(tz=timezone(timedelta(hours=8))).strftime('%m/%d/%Y')
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
        }
    )

def test(request):
    _set = [x.name for x in models.Algo.objects.exclude(pid=0)]
    return render_to_response(
        'add_warning.html',
        {
            'algo_type':_set,
        }
    )

def warning_detail(request, _date, _site, _algo, _line, _err_type):
    _date = datetime.strptime(_date, '%Y年%m月%d日')
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
        _this.append('、'.join([x['name'] for x in w.reason.all().values('name')]))
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

def search_warning(request):
    _date = request.POST['r_date']
    _to_date = datetime.strptime(_date, '%m/%d/%Y')
    _site = request.POST['r_site']
    return get_data(_site, _to_date)

def add_info(request):
    _date = datetime.strptime(request.POST['r_date'], '%m/%d/%Y')
    _site = models.Site.objects.get(name=request.POST['r_site'])
    _sx_h_lie = int(request.POST['sx_h_lie']) if request.POST['sx_h_lie']!='' else 0;
    _sx_h_liang = int(request.POST['sx_h_liang']) if request.POST['sx_h_liang']!='' else 0;
    _sx_k_lie = int(request.POST['sx_k_lie']) if request.POST['sx_k_lie']!='' else 0;
    _sx_k_liang = int(request.POST['sx_k_liang']) if request.POST['sx_k_liang']!='' else 0;
    _xx_h_lie = int(request.POST['xx_h_lie']) if request.POST['xx_h_lie']!='' else 0;
    _xx_h_liang = int(request.POST['xx_h_liang']) if request.POST['xx_h_liang']!='' else 0;
    _xx_k_lie = int(request.POST['xx_k_lie']) if request.POST['xx_k_lie']!='' else 0;
    _xx_k_liang = int(request.POST['xx_k_liang']) if request.POST['xx_k_liang']!='' else 0;
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
    return info_page(request)

def add_warning(request):
    # if request.Method == 'POST':
    _date = request.POST['r_date']
    _to_date = datetime.strptime(_date, '%m/%d/%Y')
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
            _reasons = [models.Reason.objects.get(name=x) for x in request.POST.getlist('r_reason')]
            for r in _reasons:
                _add.reason.add(r)

    except Exception as e:
        logic.to_log('error', repr(e))
    finally:
        return warning_page(request)

def init(request):




    # _r1 = models.Reason(pid=0, name='图像质量')
    # _r2 = models.Reason(pid=0, name='截图不准')
    # _r3 = models.Reason(pid=0, name='TOEC服务')
    # _r4 = models.Reason(pid=0, name='算法本身')
    # _r5 = models.Reason(pid=0, name='其他')
    # _r1.save()
    # _r2.save()
    # _r3.save()
    # _r4.save()
    # _r5.save()
    #
    # _site1 = models.Site(name='杨柳青')
    # _site2 = models.Site(name='静海')
    # _site3 = models.Site(name='唐官屯')
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
    # _site1.save()
    # _site2.save()
    # _site3.save()
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
    # _kind1 = models.Kind(name='C（敞车）')
    # _kind2 = models.Kind(name='P（篷车）')
    # _kind3 = models.Kind(name='G（罐车）')
    # _kind4 = models.Kind(name='N、X（平车）')
    # _kind5 = models.Kind(name='W（毒品车）')
    # _kind6 = models.Kind(name='B（冷藏车）')
    # _kind1.save()
    # _kind2.save()
    # _kind3.save()
    # _kind4.save()
    # _kind5.save()
    # _kind6.save()
    #
    # _algo1 = models.Algo(pid=0, name='图像算法（线阵左右侧图像）')
    # _algo1.save()
    # _algo11 = models.Algo(pid=_algo1.id, name='货车车门开启')
    # _algo12 = models.Algo(pid=_algo1.id, name='客车车门开启')
    # _algo13 = models.Algo(pid=_algo1.id, name='悬挂异物（货车）')
    # _algo14 = models.Algo(pid=_algo1.id, name='货车尾管未吊起')
    # _algo15 = models.Algo(pid=_algo1.id, name='动车注水口开启')
    # _algo16 = models.Algo(pid=_algo1.id, name='车厢连接处异物')
    # _algo11.save()
    # _algo12.save()
    # _algo13.save()
    # _algo14.save()
    # _algo15.save()
    # _algo16.save()
    # _algo2 = models.Algo(pid=0, name='图像算法（线阵走形部图像）')
    # _algo2.save()
    # _algo21 = models.Algo(pid=_algo2.id, name='货车折角塞门关闭')
    # _algo22 = models.Algo(pid=_algo2.id, name='货车闸链拉紧')
    # _algo23 = models.Algo(pid=_algo2.id, name='货车风管连接异常')
    # _algo24 = models.Algo(pid=_algo2.id, name='客车电池盖开启')
    # _algo21.save()
    # _algo22.save()
    # _algo23.save()
    # _algo24.save()
    #
    # _algo3 = models.Algo(pid=0, name='轮温算法')
    # _algo3.save()
    # _algo31 = models.Algo(pid=_algo3.id, name='抱闸（热轮，轮温检测）')
    # _algo31.save()
    # _algo4 = models.Algo(pid=0, name='视频算法')
    # _algo4.save()
    # _algo5 = models.Algo(pid=0, name='声音算法')
    # _algo5.save()
