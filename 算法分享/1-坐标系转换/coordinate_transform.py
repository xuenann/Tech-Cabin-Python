"""
===============================================================================
  功能描述: 
      本脚本实现中国主流地图坐标系之间的完整互相转换，包括：
      - WGS84:全球 GPS 坐标             wgs84
      - GCJ02:火星坐标/国测局坐标        gcj02
      - BD09:百度坐标系                 bd09
      - MapBar:图吧私有加密坐标          mapbar
      - CGCS2000: 三度分带投影坐标       cgcs2000_3deg

  依赖库: pyproj (用于 CGCS2000 投影/反投影)
===============================================================================
  版权声明:
      本代码仅用于学习研究和内部系统开发，禁止用于违反国家测绘相关法律法规的用途。
      使用者需确保坐标转换的使用符合当地政策与地图服务商要求。
===============================================================================
"""

import math
from pyproj import CRS, Transformer   # 仅涉及CGCS2000坐标系时使用(pip install pyproj)

PI = math.pi
PIX = math.pi * 3000 / 180
EE = 0.00669342162296594323
A = 6378245.0


def bd09_to_gcj02(lng, lat):
    """BD09 -> GCJ02"""
    x, y =  lng - 0.0065, lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PIX)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PIX)
    lng, lat = z * math.cos(theta), z * math.sin(theta)
    return lng, lat


def gcj02_to_bd09(lng, lat):
    """GCJ02 -> BD09"""
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * PIX)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * PIX)
    lng, lat = z * math.cos(theta) + 0.0065, z * math.sin(theta) + 0.006
    return lng, lat


def gcj02_to_wgs84(lng, lat):
    """GCJ02 -> WGS84"""
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    lng, lat = lng - dlng, lat - dlat
    return lng, lat


def wgs84_to_gcj02(lng, lat):
    """WGS84 -> GCJ02"""
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    lng, lat = lng + dlng, lat + dlat
    return lng, lat


def mapbar_to_wgs84(lng, lat):
    """MapBar -> WGS84"""
    lng = lng * 100000.0 % 36000000
    lat = lat * 100000.0 % 36000000
    lng1 = int(lng - math.cos(lat / 100000.0) * lng / 18000.0 - math.sin(lng / 100000.0) * lat / 9000.0)
    lat1 = int(lat - math.sin(lat / 100000.0) * lng / 18000.0 - math.cos(lng / 100000.0) * lat / 9000.0)
    lng2 = int(lng - math.cos(lat1 / 100000.0) * lng1 / 18000.0 - math.sin(lng1 / 100000.0) * lat1 / 9000.0 + (1 if lng > 0 else -1))
    lat2 = int(lat - math.sin(lat1 / 100000.0) * lng1 / 18000.0 - math.cos(lng1 / 100000.0) * lat1 / 9000.0 + (1 if lat > 0 else -1))
    lng, lat = lng2 / 100000.0, lat2 / 100000.0
    return lng, lat


def wgs84_to_mapbar(lng_w, lat_w, max_iter=20, tol=1e-7):
    """
    反求 MapBar 坐标：WGS84 -> MapBar
    用迭代逼近 mapbar_to_wgs84 的反函数。
    """
    # 初值（一般 mapbar 坐标与 wgs   差不多）
    lng_m, lat_m = lng_w, lat_w

    for _ in range(max_iter):
        lng_calc, lat_calc = mapbar_to_wgs84(lng_m, lat_m)

        # 误差
        d_lng = lng_w - lng_calc
        d_lat = lat_w - lat_calc

        # 更新（一步步修正）
        lng_m += d_lng
        lat_m += d_lat

        # 收敛判定
        if abs(d_lng) < tol and abs(d_lat) < tol:
            break

    return lng_m, lat_m


def transform_lat(lng, lat):
    """GCJ02 latitude transformation"""
    ret = -100 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320.0 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng, lat):
    """GCJ02 longtitude transformation"""
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def bd09_to_wgs84(lng, lat):
    """BD09 -> WGS84"""
    lng, lat = bd09_to_gcj02(lng, lat)
    lng, lat = gcj02_to_wgs84(lng, lat)
    return lng, lat


def wgs84_to_bd09(lng, lat):
    """WGS84 -> BD09"""
    lng, lat = wgs84_to_gcj02(lng, lat)
    lng, lat = gcj02_to_bd09(lng, lat)
    return lng, lat


def mapbar_to_gcj02(lng, lat):
    """MapBar -> GCJ02"""
    lng, lat = mapbar_to_wgs84(lng, lat)
    lng, lat = wgs84_to_gcj02(lng, lat)
    return lng, lat


def gcj02_to_mapbar(lng, lat):
    """GCJ02 -> MapBar"""
    lng, lat = gcj02_to_wgs84(lng, lat)
    lng, lat = wgs84_to_mapbar(lng, lat)
    return lng, lat


def mapbar_to_bd09(lng, lat):
    """MapBar -> BD09"""
    lng, lat = mapbar_to_wgs84(lng, lat)
    lng, lat = wgs84_to_bd09(lng, lat)
    return lng, lat


def bd09_to_mapbar(lng, lat):
    """BD09 -> MapBar"""
    lng, lat = bd09_to_wgs84(lng, lat)
    lng, lat = wgs84_to_mapbar(lng, lat)
    return lng, lat


def lon_to_3deg_zone(lon):
    """
    确定三度带号（适用于中国经度范围）
    常用做法：zone = int((lon + 1.5) / 3)
    """
    return int((lon + 1.5) / 3)

def wgs84_to_cgcs2000_3deg(lon, lat):
    """
    把 WGS84 lon/lat (degrees) 投影到 CGCS2000 的对应 3°带（返回 x(easting), y(northing)）
    说明：
      - 假设 WGS84 与 CGCS2000 在工程精度下可视为同一基准（常用做法）
      - 使用参数：k=1.0, false_easting=500000, a=6378137.0, rf=298.257222101（CGCS2000椭球）
    """
    zone = lon_to_3deg_zone(lon)
    lon0 = zone * 3.0  # 中央经线（度）
    # 构建目标投影（Transverse Mercator / Gauss-Kruger, 三度带）
    proj4 = (
        f"+proj=tmerc +lat_0=0 +lon_0={lon0} +k=1.0 "
        f"+x_0=500000 +y_0=0 +a=6378137.0 +rf=298.257222101 +units=m +no_defs"
    )
    crs_src = CRS.from_epsg(4326)       # WGS84 geographic
    crs_tgt = CRS.from_proj4(proj4)     # CGCS2000-like 3deg zone
    transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
    x, y = transformer.transform(lon, lat)
    # 注意：有的工程会采用 x = zone*1e6 + easting 的方式返回全区东距，如需此格式可以如下：
    # x = zone * 1_000_000 + x
    return x, y, zone


def cgcs2000_3deg_to_wgs84(x, y, zone, has_zone_million=False):
    """
    将 CGCS2000 三度带投影 XY 反算到经纬度（WGS84）
    参数:
      - x, y: 平面坐标（若 has_zone_million=True，x 需先减去 zone*1e6）
      - zone: 带号
    返回: lon, lat
    """
    if has_zone_million:
        x = x - zone * 1_000_000

    lon0 = zone * 3.0
    proj4 = (
        f"+proj=tmerc +lat_0=0 +lon_0={lon0} +k=1.0 "
        f"+x_0=500000 +y_0=0 +a=6378137.0 +rf=298.257222101 +units=m +no_defs"
    )
    crs_src = CRS.from_proj4(proj4)
    crs_tgt = CRS.from_epsg(4326)   # WGS84
    transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat


def cgcs2000_3deg_to_gcj02(x, y, zone, has_zone_million=False):
    """
    将 CGCS2000 三度带投影 XY 反算到 GCJ02
    参数:
      - x, y: 平面坐标（若 has_zone_million=True，x 需先减去 zone*1e6）
      - zone: 带号

    """
    lon, lat = cgcs2000_3deg_to_wgs84(x, y, zone, has_zone_million)
    lon, lat = wgs84_to_gcj02(lon, lat)
    return lon, lat


def gcj02_to_cgcs2000_3deg(lon, lat):
    """
    将 GCJ02 经纬度反算到 CGCS2000 三度带投影 XY
    """
    lon, lat = gcj02_to_wgs84(lon, lat)
    x, y, zone = wgs84_to_cgcs2000_3deg(lon, lat)
    return x, y, zone


def cgcs2000_3deg_to_bd09(x, y, zone, has_zone_million=False):
    """
    将 CGCS2000 三度带投影 XY 反算到 BD09
    参数:
      - x, y: 平面坐标（若 has_zone_million=True，x 需先减去 zone*1e6）
      - zone: 带号
    """
    lon, lat = cgcs2000_3deg_to_wgs84(x, y, zone, has_zone_million)
    lon, lat = wgs84_to_bd09(lon, lat)
    return lon, lat


def bd09_to_cgcs2000_3deg(lon, lat):
    """
    将 BD09 经纬度反算到 CGCS2000 三度带投影 XY
    """
    lon, lat = bd09_to_wgs84(lon, lat)
    x, y, zone = wgs84_to_cgcs2000_3deg(lon, lat)
    return x, y, zone


def cgcs2000_3deg_to_mapbar(x, y, zone, has_zone_million=False):
    """
    将 CGCS2000 三度带投影 XY 反算到 MapBar
    参数:
      - x, y: 平面坐标（若 has_zone_million=True，x 需先减去 zone*1e6）
      - zone: 带号
    """
    lon, lat = cgcs2000_3deg_to_wgs84(x, y, zone, has_zone_million)
    lon, lat = wgs84_to_mapbar(lon, lat)
    return lon, lat


def mapbar_to_cgcs2000_3deg(lon, lat):
    """
    将 MapBar 经纬度反算到 CGCS2000 三度带投影 XY
    """
    lon, lat = mapbar_to_wgs84(lon, lat)
    x, y, zone = wgs84_to_cgcs2000_3deg(lon, lat)
    return x, y, zone




