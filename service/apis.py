from aiohttp.web import Response, json_response, Application
from . import loop
from .mongoDB import db_setup

api = Application()
plat = loop.run_until_complete(db_setup())


async def init_plat(request):
    """
    初始化一个地点信息
    :param request:
    :return:
    data格式： name-->string, url-->[string]
    """
    data = await request.json()
    name = data.get('name')
    url = data.get('url')

    # 检查数据
    if name is None or url is None or type(name) != str or type(url) != list :
        return Response(body='{"msg" : "信息错误"}',
                        content_type='application/json', status=400)
    # 根据name查重
    res = await plat.find_one({'name':name})
    if res != None:
        return Response(body='{"msg" : "信息已存在"}',
                        content_type='application/json', status=403)
    # 插入信息
    data['points'] = [0.0]*2
    data['info'] = "等待添加"
    result = await plat.insert_one(data)
    return Response(body='{"msg" : "添加成功"}',
                    content_type='application/json', status=200)


async def update_plat(request):
    """
    修改地点信息
    :param request:
    :return:
    """
    data = await request.json()
    name = data.get('name')

    if name is None or type(name) != str:
        return Response(body='{"msg" : "信息错误"}',
                        content_type='application/json', status=400)

    # 根据name查重
    res = await plat.find_one({'name': name})
    if res is None:
        return Response(body='{"msg" : "信息不存在"}',
                        content_type='application/json', status=404)

    result = await plat.replace_one({'name':name},data)
    return Response(body='{"msg" : "更新成功"}',
                    content_type='application/json', status=200)


async def all_plat_names(request):
    """
    获取所有的地点的名字
    :param request:
    :return:
    """
    names = []
    res = plat.find()

    async for each in res:
        if each.get('name'):
            names.append(each['name'])
    result = {'names':names }

    return json_response(result)


async def delete_plat(request):
    """
    根据名称删除地点信息
    :param request:
    :return:
    """
    data = await request.json()
    name = data.get('name')

    if name is None:
        return Response(body='{"msg" : "信息错误"}',
                        content_type='application/json', status=400)

    # 根据name查重
    res = await plat.find_one({'name': name})
    if res is None:
        return Response(body='{"msg" : "信息不存在"}',
                        content_type='application/json', status=404)

    result = await plat.delete_one({'name':name})
    return json_response({'msg':'删除成功'})


async def detail_plat(request):
    """
    某个地点的详细信息
    :param request:
    :return:
    """
    args = request.rel_url.query_string
    name = args.split('=')[1]

    if name is None:
        return Response(body='{"msg" : "信息错误"}',
                        content_type='application/json', status=400)

    # 根据name查重
    res = await plat.find_one({'name': name})
    if res is None:
        return Response(body='{"msg" : "信息不存在"}',
                        content_type='application/json', status=404)
    res.pop('_id')
    return json_response({'plat':res})



async def match_plat(request):
    """
    根据name找出匹配的点
    :param request:
    :return:
    """
    points = []
    res = plat.find()
    args = request.rel_url.query_string
    name = args.split('=')[1]

    async for each in res:
        if name in each.get('name'):
            points.append({'name':each['name'],'points':each['points']})

    result = {'points': points}
    return json_response(result)


async def match_point(request):
    """
    根据经纬度返回名称
    :param request:
    :return:
    """
    args = (request.rel_url.query_string).split('&')
    p0 = float(args[0].split('=')[1])
    p1 = float(args[1].split('=')[1])
    res = plat.find()

    async for each in res:
        if each.get('points'):
            p = each['points']
            if p[0] == p0 and p[1] == p1:
                return json_response({'name' : each.get('name')})

    return Response(body='{"msg" : "不存在"}',
                        content_type='application/json', status=404)


api.router.add_route('POST','/plat/',init_plat,name='init_plat')
api.router.add_route('PUT','/plat/',update_plat,name='update_plat')
api.router.add_route('GET','/plat/names/',all_plat_names,name='all_plat_names')
api.router.add_route('DELETE','/plat/',delete_plat,name='delete_plat')
api.router.add_route('GET','/plat/detail/',detail_plat,name='detail_plat')
api.router.add_route('GET','/plat/match/',match_plat,name='match_plat')
api.router.add_route('GET','/plat/point/',match_point,name='match_point')



