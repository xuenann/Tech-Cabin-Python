import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.font_manager import FontProperties

# 设置中文字体 - Windows系统
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

# 如果上面的字体都不行，尝试使用字体文件
try:
    font_path = 'C:/Windows/Fonts/msyh.ttc'  # 微软雅黑
    font_prop = FontProperties(fname=font_path)
    use_font_prop = True
except:
    use_font_prop = False

# 创建画布
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
if use_font_prop:
    fig.suptitle('多边形包围盒（Bounding Box）', fontsize=16, fontweight='bold', fontproperties=font_prop)
else:
    fig.suptitle('多边形包围盒（Bounding Box）', fontsize=16, fontweight='bold')

# 定义一个不规则多边形（长方形，长>高）
polygon = np.array([
    [2, 3],
    [6, 1],
    [12, 2],
    [16, 4],
    [14, 7],
    [10, 9],
    [4, 8],
    [1, 6]
])

# 计算包围盒
min_x = np.min(polygon[:, 0])
max_x = np.max(polygon[:, 0])
min_y = np.min(polygon[:, 1])
max_y = np.max(polygon[:, 1])

# 包围盒的四个角点
bbox_corners = np.array([
    [min_x, min_y],  # 左下
    [max_x, min_y],  # 右下
    [max_x, max_y],  # 右上
    [min_x, max_y]   # 左上
])

# 绘制包围盒（虚线）
bbox_patch = patches.Polygon(bbox_corners, closed=True, fill=False, 
                              edgecolor='red', linewidth=3, 
                              linestyle='--', label='包围盒')
ax.add_patch(bbox_patch)

# 绘制多边形
poly_patch = patches.Polygon(polygon, closed=True, fill=True, 
                              facecolor='lightblue', edgecolor='blue', 
                              linewidth=2, alpha=0.6, label='多边形')
ax.add_patch(poly_patch)

# 绘制多边形顶点
for i, (x, y) in enumerate(polygon):
    ax.plot(x, y, 'bo', markersize=10, zorder=5)
    if use_font_prop:
        ax.text(x, y + 0.3, f'P{i+1}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold', fontproperties=font_prop)
    else:
        ax.text(x, y + 0.3, f'P{i+1}', ha='center', va='bottom', 
                fontsize=14, fontweight='bold')

# 绘制包围盒的四个角点
bbox_labels = ['左下', '右下', '右上', '左上']
for i, (x, y) in enumerate(bbox_corners):
    ax.plot(x, y, 'r^', markersize=12, zorder=5)
    if use_font_prop:
        ax.text(x, y - 0.4, bbox_labels[i], ha='center', va='top', 
                fontsize=14, fontweight='bold', color='red', fontproperties=font_prop)
    else:
        ax.text(x, y - 0.4, bbox_labels[i], ha='center', va='top', 
                fontsize=14, fontweight='bold', color='red')

# 标注包围盒的边界线
ax.annotate('', xy=(max_x, min_y), xytext=(min_x, min_y),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2))
if use_font_prop:
    ax.text((min_x + max_x) / 2, min_y - 0.6, 
            f'宽度 = {max_x - min_x:.2f}', 
            ha='center', va='top', fontsize=14, color='red', fontweight='bold', fontproperties=font_prop)
else:
    ax.text((min_x + max_x) / 2, min_y - 0.6, 
            f'宽度 = {max_x - min_x:.2f}', 
            ha='center', va='top', fontsize=14, color='red', fontweight='bold')

ax.annotate('', xy=(min_x, max_y), xytext=(min_x, min_y),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2))
if use_font_prop:
    ax.text(min_x - 0.8, (min_y + max_y) / 2, 
            f'高度\n= {max_y - min_y:.2f}', 
            ha='right', va='center', fontsize=14, color='red', fontweight='bold', fontproperties=font_prop)
else:
    ax.text(min_x - 0.8, (min_y + max_y) / 2, 
            f'高度\n= {max_y - min_y:.2f}', 
            ha='right', va='center', fontsize=14, color='red', fontweight='bold')

# 标注包围盒坐标
ax.text(min_x, max_y + 0.5, f'({min_x:.1f}, {max_y:.1f})', 
        ha='left', va='bottom', fontsize=10, color='red', fontweight='bold')
ax.text(max_x, max_y + 0.5, f'({max_x:.1f}, {max_y:.1f})', 
        ha='right', va='bottom', fontsize=10, color='red', fontweight='bold')
ax.text(min_x, min_y - 1.2, f'({min_x:.1f}, {min_y:.1f})', 
        ha='left', va='top', fontsize=10, color='red', fontweight='bold')
ax.text(max_x, min_y - 1.2, f'({max_x:.1f}, {min_y:.1f})', 
        ha='right', va='top', fontsize=10, color='red', fontweight='bold')

# 设置坐标轴范围
ax.set_xlim(min_x - 2, max_x + 2)
ax.set_ylim(min_y - 2, max_y + 2)
if use_font_prop:
    ax.set_xlabel('X 坐标', fontsize=14, fontproperties=font_prop)
    ax.set_ylabel('Y 坐标', fontsize=14, fontproperties=font_prop)
else:
    ax.set_xlabel('X 坐标', fontsize=14)
    ax.set_ylabel('Y 坐标', fontsize=14)
ax.grid(True, alpha=0.3)
if use_font_prop:
    ax.legend(loc='upper right', fontsize=14, prop=font_prop)
else:
    ax.legend(loc='upper right', fontsize=14)
ax.set_aspect('equal')

# 添加说明文本
info_text = f"""
包围盒计算公式：
  min_x = min(所有顶点的x坐标) = {min_x:.2f}
  max_x = max(所有顶点的x坐标) = {max_x:.2f}
  min_y = min(所有顶点的y坐标) = {min_y:.2f}
  max_y = max(所有顶点的y坐标) = {max_y:.2f}

包围盒面积 = {(max_x - min_x) * (max_y - min_y):.2f}
"""

if use_font_prop:
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            ha='left', va='top', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            family='monospace', fontproperties=font_prop)
else:
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            ha='left', va='top', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            family='monospace')

plt.tight_layout()
plt.savefig('bounding_box.png', dpi=300, bbox_inches='tight')
plt.show()

print("包围盒可视化图已生成并保存为 'bounding_box.png'")
print("\n包围盒信息：")
print(f"左下角坐标: ({min_x:.2f}, {min_y:.2f})")
print(f"右上角坐标: ({max_x:.2f}, {max_y:.2f})")
print(f"宽度: {max_x - min_x:.2f}")
print(f"高度: {max_y - min_y:.2f}")
print(f"面积: {(max_x - min_x) * (max_y - min_y):.2f}")
