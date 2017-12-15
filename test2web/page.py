from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template.loader import get_template
from django.forms import *
from . import logic
from . import models
import datetime



def warning_page(request):
    _set = [x.name for x in models.Algo.objects.exclude(pid=0)]
    _js = r"""<script src="/static/js/my/warning.js"></script>"""
    k = test(request).content.decode('utf8')
    return render_to_response(
        'base.html',
        {
            'box_content': k,
            'body_script': _js,
            'algo_type':_set,
        }
    )

def stat_page(request):
    c = get_template('stat.html')
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
            'box_content': c.template.source,
            'body_script': _js,
            'body_style': _css,
            'body_root_content': _rMenu,
        }
    )

def dict_page(request):
    c = get_template('dict.html')
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
            'box_content': c.template.source,
            'body_script': _js,
            'body_style': _css,
            'body_root_content': _rMenu,
        }
    )

def test(request):
    _set = [x.name for x in models.Algo.objects.exclude(pid=0)]
    return render_to_response(
        'warning.html',
        {
            'algo_type':_set,
        }
    )
def add_warning(request):
    # if request.Method == 'POST':
    _date = request.POST['r_date']
    _to_date = datetime.datetime.strptime(_date, '%m/%d/%Y')
    _site = models.Site.objects.get(name=request.POST['r_site'])
    _kind = models.Kind.objects.get(name=request.POST['r_kind'])
    _side = request.POST['r_side']
    _line = request.POST['r_line']
    _pic = request.FILES['r_pic']
    _type = request.POST['r_type']
    try:
        _add = models.Warning(
            date=_to_date,
            site=_site,
            side=_side,
            line=_line,
            kind=_kind,
            pic=_pic,
        )
        _add.save()
        if _type != '真实':
            _reasons = [models.Reason.objects.get(name=x) for x in request.POST.getlist('r_reason')]
            for r in _reasons:
                _add.reason.add(r)
    except Exception as e:
        logic.to_log('error', repr(e))
    finally:
        c = get_template('warning.html')
        _js = r"""<script src="/static/js/my/warning.js"></script>"""
        return render_to_response(
            'base.html',
            {
                'box_content': c.template.source,
                'body_script': _js,
            }
        )
def init(request):
    _algo1 = models.Algo(pid=0, name='图像算法（线阵左右侧图像）')
    _algo1.save()
    _algo11 = models.Algo(pid=_algo1.id, name='货车车门开启')
    _algo12 = models.Algo(pid=_algo1.id, name='客车车门开启')
    _algo13 = models.Algo(pid=_algo1.id, name='悬挂异物（货车）')
    _algo14 = models.Algo(pid=_algo1.id, name='货车尾管未吊起')
    _algo15 = models.Algo(pid=_algo1.id, name='动车注水口开启')
    _algo16 = models.Algo(pid=_algo1.id, name='车厢连接处异物')
    _algo11.save()
    _algo12.save()
    _algo13.save()
    _algo14.save()
    _algo15.save()
    _algo16.save()
    _algo2 = models.Algo(pid=0, name='图像算法（线阵走形部图像）')
    _algo2.save()
    _algo21 = models.Algo(pid=_algo2.id, name='货车折角塞门关闭')
    _algo22 = models.Algo(pid=_algo2.id, name='货车闸链拉紧')
    _algo23 = models.Algo(pid=_algo2.id, name='货车风管连接异常')
    _algo24 = models.Algo(pid=_algo2.id, name='客车电池盖开启')
    _algo21.save()
    _algo22.save()
    _algo23.save()
    _algo24.save()

    _algo3 = models.Algo(pid=0, name='轮温算法')
    _algo3.save()
    _algo31 = models.Algo(pid=_algo3.id, name='抱闸（热轮，轮温检测）')
    _algo31.save()
    _algo4 = models.Algo(pid=0, name='视频算法')
    _algo4.save()
    _algo5 = models.Algo(pid=0, name='声音算法')
    _algo5.save()
