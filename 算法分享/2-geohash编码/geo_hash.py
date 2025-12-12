from __future__ import division
from collections import namedtuple
from builtins import range
import decimal
import math

base32 = '0123456789bcdefghjkmnpqrstuvwxyz'


def _indexes(geohash):
    if not geohash:
        raise ValueError('Invalid geohash')

    for char in geohash:
        try:
            yield base32.index(char)
        except ValueError:
            raise ValueError('Invalid geohash')


def _fixedpoint(num, bound_max, bound_min):
    """
    返回给定的num，精度为2-log10（范围）

    Params
    ------
    num：一个数字
    bound_max：最大界限，例如地理哈希单元（NE）的最大纬度
    bound_min：最小界限，例如地理哈希单元（SW）的最小纬度

    Returns
    -------
    小数
    """
    try:
        decimal.getcontext().prec = math.floor(2 - math.log10(bound_max
                                                              - bound_min))
    except ValueError:
        decimal.getcontext().prec = 12
    return decimal.Decimal(num)


def bounds(geohash):
    """
    返回指定地理哈希的SW/NE纬度/经度边界：

            |      .| NE
            |    .  |
            |  .    |
         SW |.      |

    :param geohash: string, 需要边界的单元格

    :returns: a named tuple of namedtuples Bounds(sw(lat, lon), ne(lat, lon)).

    # >>> bounds = geo_hash.bounds('ezs42')
    # >>> bounds
    # >>> ((42.583, -5.625), (42.627, -5.58)))
    # >>> bounds.sw.lat
    # >>> 42.583

    """
    geohash = geohash.lower()

    even_bit = True
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180

    # 5 bits for a char. So divide the decimal by power of 2, then AND 1
    # to get the binary bit - fast modulo operation.
    for index in _indexes(geohash):
        for n in range(4, -1, -1):
            bit = (index >> n) & 1
            if even_bit:
                # longitude
                lon_mid = (lon_min + lon_max) / 2
                if bit == 1:
                    lon_min = lon_mid
                else:
                    lon_max = lon_mid
            else:
                # latitude
                lat_mid = (lat_min + lat_max) / 2
                if bit == 1:
                    lat_min = lat_mid
                else:
                    lat_max = lat_mid
            even_bit = not even_bit

    SouthWest = namedtuple('SouthWest', ['lat', 'lon'])
    NorthEast = namedtuple('NorthEast', ['lat', 'lon'])
    sw = SouthWest(lat_min, lon_min)
    ne = NorthEast(lat_max, lon_max)
    Bounds = namedtuple('Bounds', ['sw', 'ne'])
    return Bounds(sw, ne)


def bbox(geohash):
    '''
    获取边界框

    :param geohash: geohash块
    :return: {'s', 'w', 'n', 'e'}
    '''
    sw, ne = bounds(geohash)
    return {'s': sw.lat, 'w': sw.lon, 'n': ne.lat, 'e': ne.lon}


def decode(geohash):
    """
    将geohash解码为纬度/经度。位置是单元的大致中心，具有合理的精度。

    :param geohash: string, 需要边界的单元格

    :returns: 具有十进制lat和lon作为属性的Namedtuple。

    # >>> geo_hash.decode('gkkpfve')
    # >>> (70.2995, -27.9993)
    """
    (lat_min, lon_min), (lat_max, lon_max) = bounds(geohash)

    lat = (lat_min + lat_max) / 2
    lon = (lon_min + lon_max) / 2

    lat = _fixedpoint(lat, lat_max, lat_min)
    lon = _fixedpoint(lon, lon_max, lon_min)
    Point = namedtuple('Point', ['lat', 'lon'])
    return Point(lat, lon)


def decode_exactly(geohash):
    """
    将geohash解码为纬度/经度。位置是单元的大致中心，具有合理的精度。
    
    :param geohash: string, 需要边界的单元格
    :returns: 具有十进制lat和lon作为属性的Namedtuple。
    """
    (lat_min, lon_min), (lat_max, lon_max) = bounds(geohash)

    lat = (lat_min + lat_max) / 2
    lon = (lon_min + lon_max) / 2

    lat = _fixedpoint(lat, lat_max, lat_min)
    lon = _fixedpoint(lon, lon_max, lon_min)

    return lat, lon, (lat_max - lat_min)/2, (lon_max - lon_min)/2


def encode(lat, lon, precision):
    """
    将纬度、经度编码为地理哈希。

    :param lat: latitude, 纬度，一个可以转换为十进制的数字或字符串。理想情况下，传递一个字符串以避免浮点不确定性。它将被转换为十进制。
    :param lon: longitude, 经度，一个可以转换为十进制的数字或字符串。理想情况下，传递一个字符串以避免浮点不确定性。它将被转换为十进制。
    :param precision: integer, 整数，1到12表示地理哈希级别，最高12。

    :returns: geohash as string.

    # >>> geo_hash.encode('70.2995', '-27.9993', 7)
    # >>> gkkpfve
    """
    lat = decimal.Decimal(lat)
    lon = decimal.Decimal(lon)

    index = 0  # index into base32 map
    bit = 0  # each char holds 5 bits
    even_bit = True
    lat_min = -90
    lat_max = 90
    lon_min = -180
    lon_max = 180
    ghash = []

    while (len(ghash) < precision):
        if even_bit:
            # bisect E-W longitude
            lon_mid = (lon_min + lon_max) / 2
            if lon >= lon_mid:
                index = index * 2 + 1
                lon_min = lon_mid
            else:
                index = index * 2
                lon_max = lon_mid
        else:
            # bisect N-S latitude
            lat_mid = (lat_min + lat_max) / 2
            if lat >= lat_mid:
                index = index * 2 + 1
                lat_min = lat_mid
            else:
                index = index * 2
                lat_max = lat_mid
        even_bit = not even_bit

        bit += 1
        if bit == 5:
            # 5 bits gives a char in geohash. Start over
            ghash.append(base32[index])
            bit = 0
            index = 0

    return ''.join(ghash)


def adjacent(geohash, direction):
    """
    确定给定方向上的相邻单元格。

    :param geohash: 需要相邻单元格的单元格
    :param direction: geohash的方向，字符串，n、s、e、w之一

    :returns: 相邻单元格的geohash

    # >>> geo_hash.adjacent('gcpuyph', 'n')
    # >>> gcpuypk
    """
    if not geohash:
        raise ValueError('Invalid geohash')
    if direction not in ('nsew'):
        raise ValueError('Invalid direction')

    neighbour = {
        'n': ['p0r21436x8zb9dcf5h7kjnmqesgutwvy',
              'bc01fg45238967deuvhjyznpkmstqrwx'],
        's': ['14365h7k9dcfesgujnmqp0r2twvyx8zb',
              '238967debc01fg45kmstqrwxuvhjyznp'],
        'e': ['bc01fg45238967deuvhjyznpkmstqrwx',
              'p0r21436x8zb9dcf5h7kjnmqesgutwvy'],
        'w': ['238967debc01fg45kmstqrwxuvhjyznp',
              '14365h7k9dcfesgujnmqp0r2twvyx8zb'],
    }

    border = {
        'n': ['prxz', 'bcfguvyz'],
        's': ['028b', '0145hjnp'],
        'e': ['bcfguvyz', 'prxz'],
        'w': ['0145hjnp', '028b'],
    }

    last_char = geohash[-1]
    parent = geohash[:-1]  # parent is hash without last char

    typ = len(geohash) % 2

    # check for edge-cases which don't share common prefix
    if last_char in border[direction][typ] and parent:
        parent = adjacent(parent, direction)

    index = neighbour[direction][typ].index(last_char)
    return parent + base32[index]


def neighbours(geohash):
    """
    返回指定地理哈希的所有8个相邻单元格::

        | nw | n | ne |
        |  w | * | e  |
        | sw | s | se |

    :param geohash: string, geohash neighbours are required of

    :returns: 邻居作为具有属性n、ne、e、se、s、sw、w、nw的地理哈希的namedtuple列表。

    # >>> neighbours = geo_hash.neighbours('gcpuyph')
    # >>> neighbours
    # >>> ('gcpuypk', 'gcpuypm', 'gcpuypj', 'gcpuynv', 'gcpuynu', 'gcpuyng', 'gcpuyp5', 'gcpuyp7')
    # >>> neighbours.ne
    # >>> gcpuypm
    """
    n = adjacent(geohash, 'n')
    ne = adjacent(n, 'e')
    e = adjacent(geohash, 'e')
    s = adjacent(geohash, 's')
    se = adjacent(s, 'e')
    w = adjacent(geohash, 'w')
    sw = adjacent(s, 'w')
    nw = adjacent(n, 'w')
    Neighbours = namedtuple('Neighbours',
                            ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'])
    #return Neighbours(n, ne, e, se, s, sw, w, nw)
    return [n, ne, e, se, s, sw, w, nw]


def expanding(geohash,num):
    '''
    搜索指定geohash周围num圈的geohash块

    :param geohash: geohash块
    :param num: 扩展圈数
    :return: 结构列表
    '''
    if num==1:
        return [geohash]
    geo_list={geohash}

    for _ in range(num-1):
        for geo in list(geo_list):
            tmp=neighbours(geo)
            for t in tmp:
                geo_list.add(t)

    return list(geo_list)





