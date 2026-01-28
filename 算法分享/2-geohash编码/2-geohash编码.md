# 深入解析Geohash编码原理与应用

> 一串简短的字符wx4g0ec1，背后隐藏的是一整套将地球表面精细划分的空间编码智慧。

想象一下，你站在北京北海公园，拿出手机查看自己的位置，除了看到熟悉的经纬度数字，还可能遇到一串像“wx4g0ec1”这样的神秘代码。这串代码就是Geohash，一种巧妙地将二维经纬度转换为一维字符串的地理编码系统。

当你使用外卖软件查找附近餐厅、在社交应用中发现“附近的人”，或是简单地向朋友分享自己的大概位置时，Geohash很可能正在幕后默默工作。



## 1 Geohash是什么？

Geohash是一种地址编码方法，它能将地球上的任意位置（用经纬度表示）转换成一段字母数字混合的字符串。这种转换不是简单的替代，而是通过精妙的算法实现的。

它的核心价值在于：**将复杂的二维空间查询简化为一维字符串比较**，从而极大提升了地理位置相关应用的效率和性能。

北海公园的坐标（约39.93°N，116.39°E）经过Geohash编码后会变成“wx4g0ec1”。

这个字符串有几个重要特性：

1. **一个字符串同时代表 经度 + 纬度。**
2. **字符串越长 → 区域越小 → 精度越高。**
3. **相同前缀的 GeoHash 代表靠得更近的区域（前缀聚合）。**
4. **GeoHash 表达的是 一个矩形区域，不是唯一精确点。**

由于**具有相同前缀的Geohash码表示地理位置相近**。这一特性使得“附近搜索”变得异常高效——只需比较字符串前缀即可快速筛选出相邻区域的位置点。



## 2 Geohash编码算法：二分法的艺术

Geohash算法的精妙之处在于它对经纬度分别进行二分法处理，然后将结果交叉组合。这个过程可以分解为几个清晰的步骤。

以纬度编码为例：初始范围为[-90, 90]。对于北京约39.93°N的位置，首先判断它落在左区间[-90, 0)还是右区间[0, 90]。显然它在右区间，**记录编码“1”**。

接着将[0, 90]平分为[0, 45]和[45, 90]。39.93落在[0, 45]区间，**记录编码“0”**。如此循环，每次将区间二分并记录位置，直到达到所需精度。

经度编码过程类似，只是初始范围为[-180, 180]，针对116.39°E的位置进行同样的二分操作。最终，我们得到两串二进制编码：纬度编码和经度编码。

**关键一步来了**：将这两串编码按“**奇数位放纬度，偶数位放经度**”的规则交叉合并。假设纬度编码为10111，经度编码为11010，合并后就变成了1110011101...这样的新二进制串。

最后一步是Base32编码：将合并后的二进制串每5位一组，转换为32进制字符（使用0-9、b-z去掉a, i, l, o的32个字符）。这样，一长串二进制就变成了人类更易读写的字符串形式。

![img](2-geohash编码.assets\encode.png)

```python
# Geohash编码过程示意
纬度39.92324 → 二进制编码：10111000110001111001
经度116.3906 → 二进制编码：11010010110001000100
交叉合并 → 1110011101001000111100000011010101100001
Base32编码 → wx4g0ec1
```



## 3 空间填充曲线：Geohash的理论基石

要深入理解Geohash，需要了解其背后的数学原理——空间填充曲线。Geohash实际上是一种将二维空间映射到一维字符串的方法，这个映射过程遵循特定的空间填充曲线模式。

最常见的空间填充曲线是**皮亚诺曲线**（Peano曲线），它的特点是形如字母“Z”的递归结构。当我们将地理空间不断四等分时，Geohash编码实际上就是沿着这条曲线给每个小区域分配编号。

![img](2-geohash编码.assets\geohash-1.png)

皮亚诺曲线有一个显著特点：**大多数情况下，编码相近的位置实际距离也相近**。这正是Geohash能够支持高效邻近搜索的根本原因。

但皮亚诺曲线也有明显缺陷——存在“突变”现象。有些编码相邻的位置实际距离却很远，比如**0111与1000**在编码上是相邻的，但在地理位置上可能分别位于区域的两个对角。

实际上，希尔伯特空间填充曲线在这方面表现更好，**突变更少，空间连续性更强**。但Geohash标准最终选择了皮亚诺曲线，主要是因为它实现简单，计算效率高。

![img](2-geohash编码.assets\geohash-2.jpg)



## 4 精度与误差：选择合适长度的Geohash

Geohash的长度直接决定了它表示的区域大小和精度。不同的业务场景需要不同精度的Geohash编码。

| 编码长度 | 单元格宽度 (约) | 单元格高度 (约) | 典型误差半径 | 适用场景                   |
| :------- | :-------------- | :-------------- | :----------- | :------------------------- |
| 1        | 5,000 km        | 5,000 km        | ±2,500 km    | 全球大陆、海洋板块划分     |
| 2        | 1,250 km        | 625 km          | ±625 km      | 大型国家、区域范围         |
| 3        | 156 km          | 156 km          | ±78 km       | 国家、大型省份范围         |
| 4        | 39.1 km         | 19.5 km         | ±20 km       | 省份、大城市范围           |
| 5        | 4.89 km         | 4.89 km         | ±2.5 km      | 城市、城镇、区县范围       |
| 6        | 1.22 km         | 0.61 km         | ±0.61 km     | 乡镇、街道、社区范围       |
| 7        | 153 m           | 153 m           | ±76 m        | 街区、大型园区、景区       |
| 8        | 38.2 m          | 19.1 m          | ±19 m        | 街道、住宅小区、大型建筑   |
| 9        | 4.77 m          | 4.77 m          | ±2.4 m       | 建筑物、精确地址点         |
| 10       | 1.19 m          | 0.596 m         | ±0.6 m       | 独立店铺、树木、精细地物   |
| 11       | 0.149 m         | 0.149 m         | ±0.07 m      | 高精度测绘、室内定位       |
| 12       | 0.037 m         | 0.019 m         | ±0.02 m      | 极高精度应用、特殊工业场景 |

误差控制是Geohash应用中的重要考虑。理论上，Geohash是通过无限二分逼近真实坐标的近似算法。实际应用中，**选择适当的编码长度**可以在精度和效率之间找到平衡点。

以纬度计算为例，N次二分后的误差约为90/2^N。当N=20（编码长度为8）时，最大误差仅为0.00009度，约合10米，这已经能满足绝大多数民用定位需求。



## 5 边界问题与解决方案

Geohash有一个著名的问题：边界效应。两个地理位置可能非常接近，但如果它们恰好处在不同Geohash区域的边界两侧，**它们的编码可能完全不同**。

想象一条街道正好是两个Geohash区域的分界线，街道对面的两家店铺可能拥有完全不相关的Geohash编码。如果只按编码前缀匹配，它们就不会出现在彼此的“附近”搜索结果中。

例如在图中的红点虽然和上方的白点离的很近，可是它们的 geohash 值一定有差别，因为他们所属子块并不同；虽然在视野上红点和黑点离的很远，但 他们因为同属一个子块，事实上 geohash 值相同。如果只按编码前缀匹配，红点和白点就不会出现在彼此的“附近”搜索结果中。

<img src="2-geohash编码.assets\image-20251212100018968.png" alt="image-20251212100018968" width="30%" />

解决这个问题的标准方法是**九宫格搜索法**：不仅搜索目标点所在的Geohash区域，同时搜索其周围8个相邻区域。

这种方法能确保覆盖所有可能邻近的点，即使它们位于边界另一侧。在实际应用中，数据库查询条件会扩展为包括中心区域及其所有相邻区域的Geohash前缀。



## 6 Python中的Geohash工具实践

对于开发者而言，有多种Python库可以实现Geohash编码解码。以下是几个常用库的对比：

### 6.1 geo_hash

geo_hash是我基于多个geohash实现工具，汇总了他们相关功能的纯python脚本

- 代码链接：[点击查看](https://github.com/xuenann/Tech-Cabin-Python/blob/main/%E7%AE%97%E6%B3%95%E5%88%86%E4%BA%AB/2-geohash%E7%BC%96%E7%A0%81/geo_hash.py)

```python
import geo_hash

# 编码
gh = geo_hash.encode(30.723514, 104.123245, precision=5)	# "wm6nc"

# 解码为Point对象
point = geo_hash.decode("wm6nc")  # Point(lat=Decimal('30.73974609375'), lon=Decimal('104.12841796875'))

# 解码为中心及偏差
center = geo_hash.decode_exactly("wm6nc")	# (30.73974609375, 104.12841796875,0.02197265625, 0.02197265625)

# 		geohash块各方向名称
#		| nw | n | ne |
#       |  w | * | e  |
#       | sw | s | se |
# 获取指定方向邻居区域
adjacent_n = geo_hash.adjacent("wm6nc", 'n') # wm6p1

# 获取左下角和右上角经纬度
bounds = geo_hash.bounds("wm6nc")
# Bounds(sw=SouthWest(lat=30.7177734375, lon=104.1064453125), ne=NorthEast(lat=30.76171875, lon=104.150390625))

# 获取八个方向的邻居
neighbours = geo_hash.neighbours("wm6nc")
# Neighbours(n='wm6p1',ne='wm6p4',e='wm6nf',se='wm6nd',s='wm6n9',sw='wm6n8',w='wm6nb',nw='wm6p0')

# 对指定geohash扩num圈的所有geohash块
geohash_list = geo_hash.expanding("wm6nc",2)  
# ['wm6nc', 'wm6p1', 'wm6p4', 'wm6nf', 'wm6nd', 'wm6n9', 'wm6n8', 'wm6nb', 'wm6p0']
```

### 6.2 python-geohash 

**python-geohash** 是最直接的实现之一，提供完整的编码解码功能，但python-geohash 需要编译 C 扩展，需要Windows 环境有 Microsoft Visual C++ 14.0 以上的编译器工具链：

- https://github.com/hkwi/python-geohash
- https://pypi.org/project/python-geohash/
- 安装命令：`pip install python-geohash`

```python
import geohash

# 编码
gh = geohash.encode(30.723514, 104.123245, precision=5)  # 返回 'wm6nc'

# 解码为中心点坐标
center = geohash.decode("wm6nc")  # (30.73974609375, 104.12841796875)

# 解码为中心及偏差
center = geohash.decode("wm6nc",delta=True)  # (30.73974609375, 104.12841796875,0.02197265625, 0.02197265625)
center = geohash.decode_exactly("wm6nc")

# 获取边界框
bbox = geohash.bbox("wm6nc")  
# {'s': 30.7177734375, 'w': 104.1064453125, 'n': 30.76171875, 'e': 104.150390625}

# 获取八个邻居区域
neighbors = geohash.neighbors("wm6nc")
# ['wm6nb', 'wm6nf', 'wm6n9', 'wm6n8', 'wm6nd', 'wm6p1', 'wm6p0', 'wm6p4']
```

### 6.3 geolib

**geolib** 提供了更面向对象的接口，代码更加清晰：

- https://github.com/joyanujoy/geolib
- https://pypi.org/project/geolib/
- 安装命令：`pip install geolib`

```python
from geolib import geohash

# 编码
gh = geohash.encode(30.723514, 104.123245, precision=5)

# 解码为Point对象
point = geohash.decode("wm6nc")  
# Point(lat=Decimal('30.73974609375'), lon=Decimal('104.12841796875'))

# 获取左下角和右上角经纬度
bounds = geohash.bounds("wm6nc")
# Bounds(sw=SouthWest(lat=30.7177734375, lon=104.1064453125), ne=NorthEast(lat=30.76171875, lon=104.150390625))

# 获取指定方向邻居区域
adjacent_n = geohash.adjacent("wm6nc", 'n') # wm6p1

# 获取八个方向的邻居
neighbours = geohash.neighbours("wm6nc")
# Neighbours(n='wm6p1',ne='wm6p4',e='wm6nf',se='wm6nd',s='wm6n9',sw='wm6n8',w='wm6nb',nw='wm6p0')
```

### 6.4 geohash2

**geohash2** 是另一个选择，但需要注意其decode方法返回的是简化精度的字符串：

- https://github.com/dbarthe/geohash/
- https://pypi.org/project/geohash2/
- 安装命令：`pip install geohash2`

```python
import geohash2

# 编码
gh = geohash2.encode(30.723514, 104.123245, precision=5)  # 'wm6nc'

# 解码（返回简化精度）
lat, lon = geohash2.decode("wm6nc")  # ('30.7', '104.1')

# 精确解码
lat, lon, lat_err, lon_err = geohash2.decode_exactly("wm6nc")
# (30.73974609375, 104.12841796875, 0.02197265625, 0.02197265625)
```

### 6.5 Geohash

**Geohash**是纯python实现

- https://github.com/vinsci/geohash
- https://pypi.org/project/Geohash/
- 安装命令：`pip install Geohash`

```python
import Geohash

# 编码
gh = Geohash.encode(30.723514, 104.123245, precision=5)  # 返回 'wm6nc'

# 解码为中心点坐标
center = Geohash.decode("wm6nc")  # (30.73974609375, 104.12841796875)

# 解码为中心及偏差
center = Geohash.decode("wm6nc",delta=True)  # (30.73974609375, 104.12841796875,0.02197265625, 0.02197265625)
center = Geohash.decode_exactly("wm6nc")
```



## 7 geohash可视化

1. https://rawgit.com/rzanato/geohashgrid/master/geohashgrid.html

   - 可以通过鼠标缩放查看全球地图的geohash块

   <img src="2-geohash编码.assets\image-20251212152713412.png" alt="image-20251212100018968" width="50%" />

2. https://www.movable-type.co.uk/scripts/geohash.html

   - 可输入经纬度及精度，生成对应的geohash编码，并在地图上查看

   <img src="2-geohash编码.assets\image-20251212153159911.png" alt="image-20251212153159911" width="40%" />

3. https://ryan-miao.github.io/geohash_tool/
   - 基于百度地图，可以通过鼠标点击查看对应精度的geohash块

<img src="2-geohash编码.assets\image-20251212153532785.png" alt="image-20251212153532785" width="50%"  />



## 8 总结

GeoHash 是一种 **简单、高效、可排序的空间编码方式**。它把经纬度转成字符串，在：

✔ 数据库索引
✔ 空间搜索
✔ 轨迹聚合
✔ 多面数据合并

等场景中都非常好用。

一句话总结：

**GeoHash 是用“字符串”来表达“空间”，让地理问题变成文本问题。**



## 📬 关注我 · 获取更多内容

### **📌 南墨的技术小栈**

<img src="2-geohash编码.assets\qrcode_for_gh_8be4598ab15d_1280.jpg" alt="qrcode_for_gh_8be4598ab15d_1280" width="30%" />

这里是我的个人知识分享空间。我会定期整理和分享工作与学习中积累的经验与资源，内容涵盖：

- 算法分享 —— 深入讲解算法原理、实现思路与代码示例。
- 工具分享 —— 推荐实用工具与脚本，包括我个人开发的小工具和精选开源工具。
- 开源项目 —— 精选 GitHub 上高星项目，拆解原理、使用方法和最佳实践。
- 数据分享 —— 工作学习中收集整理的数据资源。

无论你是技术爱好者、算法研究者，还是对数据与开源感兴趣的朋友，这里都希望能成为你学习、探索和实践的参考空间。

若在阅读或使用过程中有任何疑问，欢迎在公众号私信我，我会尽快与您交流。









