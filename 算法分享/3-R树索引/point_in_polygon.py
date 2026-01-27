from shapely.geometry import Point, Polygon
from shapely.geometry.collection import GeometryCollection
import time


class PolygonIndexWithBounds:
    """
    使用包围盒快速过滤的空间索引
    性能：中等（10-100x）
    """
    
    def __init__(self, polygons_dict):
        """初始化包围盒索引"""
        self.polygons = {}
        self.bounds_map = {}
        
        for name, coords in polygons_dict.items():
            polygon = Polygon(coords)
            self.polygons[name] = polygon
            self.bounds_map[name] = polygon.bounds
    
    def find_point_in_polygons(self, point_lon, point_lat):
        """查找点所在的多边形"""
        point = Point(point_lon, point_lat)
        result = []
        
        # 通过包围盒过滤
        candidates = []
        for name, bounds in self.bounds_map.items():
            minx, miny, maxx, maxy = bounds
            if minx <= point_lon <= maxx and miny <= point_lat <= maxy:
                candidates.append(name)
        
        # 精确检查
        for name in candidates:
            if self.polygons[name].contains(point):
                result.append(name)
        
        return result
    
    def find_points_in_polygons_batch(self, points_list):
        """批量查询"""
        results = []
        for lon, lat in points_list:
            polygons = self.find_point_in_polygons(lon, lat)
            results.append({"point": (lon, lat), "polygons": polygons})
        return results


class PolygonIndexWithRtree:
    """
    使用R树空间索引的多边形查询
    性能：最快（100-1000x）
    
    Rtree使用动态边界体积树，专门为空间查询优化
    """
    
    def __init__(self, polygons_dict):
        """初始化R树索引"""
        try:
            from shapely.strtree import STRtree
        except ImportError:
            print("⚠️ 需要 shapely >= 2.0，使用 pip install --upgrade shapely")
            raise
        
        self.polygons = {}
        self.geometry_list = []
        self.name_list = []
        
        # 构建几何体列表用于R树
        for name, coords in polygons_dict.items():
            polygon = Polygon(coords)
            self.polygons[name] = polygon
            self.geometry_list.append(polygon)
            self.name_list.append(name)
        
        # 创建R树索引
        self.tree = STRtree(self.geometry_list)
    
    def find_point_in_polygons(self, point_lon, point_lat):
        """
        使用R树查询点所在的多边形
        """
        point = Point(point_lon, point_lat)
        result = []
        
        # R树查询：获取可能包含该点的多边形索引
        candidates_idx = self.tree.query(point, predicate='intersects')
        
        # 精确检查（因为intersects只是粗略检查）
        for idx in candidates_idx:
            if self.geometry_list[idx].contains(point):
                result.append(self.name_list[idx])
        
        return result
    
    def find_points_in_polygons_batch(self, points_list):
        """批量查询"""
        results = []
        for lon, lat in points_list:
            polygons = self.find_point_in_polygons(lon, lat)
            results.append({"point": (lon, lat), "polygons": polygons})
        return results


def point_in_polygon(point_lon, point_lat, polygon_coords):
    """
    判断一个点是否在多边形内
    
    参数:
        point_lon: 点的经度（float）
        point_lat: 点的纬度（float）
        polygon_coords: 多边形顶点列表，格式为 [(lon1, lat1), (lon2, lat2), ...]
    
    返回:
        True: 点在多边形内
        False: 点不在多边形内
    """
    point = Point(point_lon, point_lat)
    polygon = Polygon(polygon_coords)
    return polygon.contains(point)


def find_point_in_polygons(point_lon, point_lat, polygons_dict):
    """
    查找点所在的多边形（不使用索引，适合小数据集）
    
    参数:
        point_lon: 点的经度
        point_lat: 点的纬度
        polygons_dict: 多边形字典
    
    返回:
        包含该点的多边形名称列表
    """
    point = Point(point_lon, point_lat)
    result = []
    
    for name, coords in polygons_dict.items():
        polygon = Polygon(coords)
        if polygon.contains(point):
            result.append(name)
    
    return result


if __name__ == "__main__":
    # 示例 1：单个多边形判断
    print("=" * 50)
    print("示例 1: 判断点是否在单个多边形内")
    print("=" * 50)
    
    # 定义一个矩形多边形（北京四环附近的一个区域）
    polygon_coords = [
        (116.3, 39.9),   # 左下
        (116.5, 39.9),   # 右下
        (116.5, 40.0),   # 右上
        (116.3, 40.0),   # 左上
    ]
    
    # 测试点1：在多边形内
    point1_lon, point1_lat = 116.4, 39.95
    result1 = point_in_polygon(point1_lon, point1_lat, polygon_coords)
    print(f"点 ({point1_lon}, {point1_lat}) 在多边形内: {result1}")
    
    # 测试点2：不在多边形内
    point2_lon, point2_lat = 116.6, 39.95
    result2 = point_in_polygon(point2_lon, point2_lat, polygon_coords)
    print(f"点 ({point2_lon}, {point2_lat}) 在多边形内: {result2}")
    
    # 示例 2：使用空间索引加速查询
    print("\n" + "=" * 50)
    print("示例 2: 使用空间索引（推荐用于大数据集）")
    print("=" * 50)
    
    # 定义多个区域多边形
    areas = {
        "朝阳区": [
            (116.4, 39.9),
            (116.6, 39.9),
            (116.6, 40.0),
            (116.4, 40.0),
        ],
        "海淀区": [
            (116.2, 39.95),
            (116.4, 39.95),
            (116.4, 40.1),
            (116.2, 40.1),
        ],
        "东城区": [
            (116.35, 39.85),
            (116.55, 39.85),
            (116.55, 39.95),
            (116.35, 39.95),
        ],
        "西城区": [
            (116.25, 39.9),
            (116.35, 39.9),
            (116.35, 40.0),
            (116.25, 40.0),
        ],
    }
    
    # 示例 3：性能对比
    print("\n" + "=" * 70)
    print("示例 3: 性能对比（无索引 vs 包围盒索引 vs R树索引）")
    print("=" * 70)
    
    # 生成大量测试多边形和点
    print("生成 1000 个随机多边形和 500 个查询点...")
    import random
    random.seed(42)
    
    large_polygons = {}
    for i in range(1000):
        x = random.uniform(116.0, 117.0)
        y = random.uniform(39.5, 40.5)
        size = random.uniform(0.01, 0.05)
        coords = [
            (x, y),
            (x + size, y),
            (x + size, y + size),
            (x, y + size),
        ]
        large_polygons[f"area_{i}"] = coords
    
    test_points = [
        (random.uniform(116.0, 117.0), random.uniform(39.5, 40.5))
        for _ in range(500)
    ]
    
    # 方法1：不使用索引（直接遍历）
    print(f"\n[方法1] 直接遍历 - {len(large_polygons)} 个多边形，{len(test_points)} 个查询点")
    start_time = time.time()
    for lon, lat in test_points:
        find_point_in_polygons(lon, lat, large_polygons)
    time_no_index = time.time() - start_time
    print(f"  ⏱️  耗时: {time_no_index:.3f} 秒")
    
    # 方法2：包围盒索引
    print(f"\n[方法2] 包围盒索引 - {len(large_polygons)} 个多边形，{len(test_points)} 个查询点")
    start_time = time.time()
    index_bounds = PolygonIndexWithBounds(large_polygons)
    time_bounds_build = time.time() - start_time
    print(f"  索引构建: {time_bounds_build:.3f} 秒")
    
    start_time = time.time()
    for lon, lat in test_points:
        index_bounds.find_point_in_polygons(lon, lat)
    time_bounds_query = time.time() - start_time
    print(f"  查询耗时: {time_bounds_query:.3f} 秒")
    print(f"  总耗时:  {time_bounds_build + time_bounds_query:.3f} 秒")
    
    # 方法3：R树索引
    print(f"\n[方法3] R树索引 - {len(large_polygons)} 个多边形，{len(test_points)} 个查询点")
    start_time = time.time()
    index_rtree = PolygonIndexWithRtree(large_polygons)
    time_rtree_build = time.time() - start_time
    print(f"  索引构建: {time_rtree_build:.3f} 秒")
    
    start_time = time.time()
    for lon, lat in test_points:
        index_rtree.find_point_in_polygons(lon, lat)
    time_rtree_query = time.time() - start_time
    print(f"  查询耗时: {time_rtree_query:.3f} 秒")
    print(f"  总耗时:  {time_rtree_build + time_rtree_query:.3f} 秒")
    
    # 性能对比
    print("\n" + "=" * 70)
    print("性能对比总结:")
    print("=" * 70)
    
    total_bounds = time_bounds_build + time_bounds_query
    total_rtree = time_rtree_build + time_rtree_query
    
    speedup_bounds = time_no_index / total_bounds
    speedup_rtree = time_no_index / total_rtree
    rtree_vs_bounds = total_bounds / total_rtree
    
    print(f"直接遍历:        {time_no_index:.3f}s  (基准)")
    print(f"包围盒索引:      {total_bounds:.3f}s  (快 {speedup_bounds:.1f}x)")
    print(f"R树索引:         {total_rtree:.3f}s  (快 {speedup_rtree:.1f}x)")
    print(f"\nR树 vs 包围盒:   快 {rtree_vs_bounds:.1f}x")
    print(f"节省时间:       {total_bounds - total_rtree:.3f}s")
    
    # 示例4：推荐使用方案
    print("\n" + "=" * 70)
    print("推荐方案:")
    print("=" * 70)
    print("""
    ✓ 多边形 < 100 个：       用简单方法（find_point_in_polygons）
    ✓ 多边形 100-1000 个：    用包围盒索引（PolygonIndexWithBounds）
    ✓ 多边形 > 1000 个：      用R树索引（PolygonIndexWithRtree）【强烈推荐】
    
    使用R树的优势：
    - 查询速度最快（10-1000倍快于直接遍历）
    - 多边形越多优势越明显
    - 适合实时查询场景
    """)
    
