

def polygon_area(points):
    """
    计算任意简单多边形面积（鞋带公式）
    
    :param points: [(x1,y1), (x2,y2), ..., (xn,yn)]
    :return: 面积（非负）
    """
    n = len(points)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0


import numpy as np

def polygon_area_np(points):
    """
    NumPy向量化版本
    """
    points = np.asarray(points)
    
    if len(points) < 3:
        return 0.0

    x = points[:, 0]
    y = points[:, 1]

    area = np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))

    return abs(area) / 2.0



def spherical_polygon_area(coords, unit="m2", radius=6378137.0):
    """
    计算经纬度多边形面积（球面模型）
    
    :param coords: [(lat, lon), ...]  单位：度
    :param unit: 输出单位
        "m2"  平方米
        "km2" 平方千米
        "ha"  公顷
        "acre" 英亩
    :param radius: 地球半径（默认WGS84）
    """

    if len(coords) < 3:
        return 0.0

    coords = np.radians(coords)

    if not np.allclose(coords[0], coords[-1]):
        coords = np.vstack([coords, coords[0]])

    lat = coords[:, 0]
    lon = coords[:, 1]

    area = 0.0

    for i in range(len(coords) - 1):
        lat1 = lat[i]
        lat2 = lat[i + 1]
        lon1 = lon[i]
        lon2 = lon[i + 1]

        dlon = lon2 - lon1

        # 经度归一化到 [-pi, pi]
        if dlon > np.pi:
            dlon -= 2 * np.pi
        elif dlon < -np.pi:
            dlon += 2 * np.pi

        area += dlon * (np.sin(lat1) + np.sin(lat2))

    area = abs(area) * radius**2 / 2.0

    # 单位转换
    if unit == "km2":
        area /= 1e6
    elif unit == "ha":
        area /= 10000
    elif unit == "acre":
        area /= 4046.8564224

    return area



from pyproj import Geod

def ellipsoid_polygon_area(coords, unit="m2"):
    """
    计算经纬度多边形面积（椭球模型）
    
    :param coords: [(lat, lon), ...]  单位：度
    :param unit: 输出单位
        "m2"  平方米
        "km2" 平方千米
        "ha"  公顷
        "acre" 英亩
    """
    geod = Geod(ellps="WGS84")

    lons = [lon for lat, lon in coords]
    lats = [lat for lat, lon in coords]

    area, _ = geod.polygon_area_perimeter(lons, lats)
    area = abs(area)

    if unit == "km2":
        area /= 1e6
    elif unit == "ha":
        area /= 10000
    elif unit == "acre":
        area /= 4046.8564224

    return area



from geographiclib.geodesic import Geodesic

def geographiclib_polygon_area(coords, unit="m2"):
    """
    使用 GeographicLib 计算椭球多边形面积

    :param coords: [(lat, lon), ...]  单位：度
    :param unit: 输出单位
        "m2"  平方米
        "km2" 平方千米
        "ha"  公顷
        "acre" 英亩
    """

    if len(coords) < 3:
        return 0.0

    geod = Geodesic.WGS84
    poly = geod.Polygon()

    for lat, lon in coords:
        poly.AddPoint(lat, lon)

    num, perimeter, area = poly.Compute()

    area = abs(area)

    if unit == "km2":
        area /= 1e6
    elif unit == "ha":
        area /= 10000
    elif unit == "acre":
        area /= 4046.8564224
    elif unit != "m2":
        raise ValueError("Unsupported unit")

    return area



if __name__ == "__main__":
    polygon = [(0, 0), (4, 0), (4, 3), (0, 3)]
    print(polygon_area(polygon))
    print(polygon_area_np(polygon))

    polygon = [
    (0.0, 0.0),
    (0.0, 0.01),
    (0.01, 0.01),
    (0.01, 0.0)
    ]

    print(spherical_polygon_area(polygon, unit="km2"))
    print(ellipsoid_polygon_area(polygon, unit="km2"))
    print(geographiclib_polygon_area(polygon, unit="km2"))
