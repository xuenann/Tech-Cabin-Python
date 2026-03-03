# python安装及虚拟环境管理

很多人觉得 Python 很简单，但真正做过多个项目后就会发现——环境才是最容易踩坑的地方。不同项目依赖不同版本的 Python，不同库之间存在兼容冲突，今天还能运行的代码，明天可能因为一个 pip install 就全部报错。尤其是在 Windows 下，**环境变量、版本共存、虚拟环境切换问题**更是让人头疼。

其实，Python 环境管理并不复杂，只要理解安装逻辑、PATH 机制和虚拟环境的隔离原理，就可以让多个版本优雅共存、项目依赖互不干扰。本文将系统梳理 **Python 的安装、环境变量配置、虚拟环境创建以及一键切换方案**，帮助你搭建一套清晰、稳定、可维护的开发环境。



# 一、Python 安装

**Python 官方下载地址：**

https://www.python.org/downloads/

你可以在这里下载任意历史版本

<img src="3-python安装及虚拟环境管理.assets\image-20260303104816111.png" alt="image-20260303104816111" width="70%" />

为了方便大家，我附上了各代版本中**推荐的最终完整安装包链接**，大家可以按需下载安装

https://wwbhl.lanzoum.com/b019vprhob
密码：9fms

## 安装流程示意

<img src="3-python安装及虚拟环境管理.assets\image-20260303113025287.png" alt="image-20260303113025287" width="60%" />

1. **选择 “Customize installation”以自定义安装位置**，上面的Install Now可以理解成默认路径安装。
2. **不要勾选 “Add to PATH”**，否则会在系统环境变量中自动添加python的环境路径

<img src="3-python安装及虚拟环境管理.assets\image-20260303113113249.png" alt="image-20260303113113249" width="60%" />

<img src="3-python安装及虚拟环境管理.assets\image-20260303113219259.png" alt="image-20260303113219259" width="60%" />

3. **设置自定义安装路径**（路径中不要带中文）

   - 建议将所有的python版本安装在一个文件夹中，以不同的文件夹命名，以统一管理，如：

     <img src="3-python安装及虚拟环境管理.assets\image-20260303114034401.png" alt="image-20260303114034401" width="60%" />

     

# 二、Python 环境变量配置

在 Windows 中，如果你希望在：**PowerShell、CMD、VSCode终端**等直接执行python，就必须正确配置环境变量。

> 在windows中打开各类终端的快捷方式
>
> - PowerShell：在任意文件夹空白处，按 **“Shift”+鼠标右键**，选择 **“在此处打开Powershell窗口”**
> - CMD：**”Win+R“**打开运行窗口，**输入”cmd”后按回车**
> - VSCode：**Ctrl+Shift+`**



## 1. 基础环境变量设置

1. 打开**设置**里的**系统信息**然后点击**高级系统设置**，再点击**环境变量**打开到对应环境配置界面

<img src="3-python安装及虚拟环境管理.assets\image-20260303115556495.png" alt="image-20260303115556495" width="80%" />

2. 在**系统变量**中双击Path

   <img src="3-python安装及虚拟环境管理.assets\image-20260303115755374.png" alt="image-20260303115755374" width="60%" />

3. 点击新建，然后输入Python的路径，再点击确定

   - 假设python的安装路径是：D:\APP_root\python\python3.9.13
   - 那么需要在系统环境变量 Path 中添加：**D:\APP_root\python\python3.9.13** 和 **D:\APP_root\python\python3.9.13\Scripts**

   <img src="3-python安装及虚拟环境管理.assets\image-20260303132840921.png" alt="image-20260303132840921" width="60%" />

   

## 2. 验证是否生效

```shell
# 在任意终端中，输入以下命令，如果输出正确路径，说明配置成功。

python --version
Python 3.9.13

where python
D:\APP_root\python\python3.9.13\python.exe
```



## 3. 多版本 Python 切换

通过上面的设置，可以在任意终端使用 “python” 执行脚本，但是如果安装了多个python版本，把每个python版本的路径都添加到环境变量中，执行python时只会执行Path里排在最前面的哪个版本，那么如何快速使用其他的python版本执行脚本呢？

我们可以创建一些启动不同python版本的bat文件，然后放在同一个目录下，并添加到系统的环境变量中。

1. **创建启动不同python版本的bat文件**，例如python3.10.bat

   - `D:\APP_root\python\python3.10.11\python.exe`：为不同python版本的安装路径
   - `%*` ：会把所有参数传给真实的 Python
   - bat文件下载地址：

   ```bat
   @echo off
   "D:\APP_root\python\python3.10.11\python.exe" %*
   ```

   <img src="3-python安装及虚拟环境管理.assets\image-20260303135011768.png" alt="image-20260303135011768" width="60%" />

2. 把这些bat文件的**绝对路径**添加到系统的环境变量中

<img src="3-python安装及虚拟环境管理.assets\image-20260303135218892.png" alt="image-20260303135218892" width="40%" />

3. 这样就可以在终端中通过**输入不同的python命令**实现调用不同的python版本

<img src="3-python安装及虚拟环境管理.assets\image-20260303140203505.png" alt="image-20260303140203505" width="60%" />

- 注：

  - 由于在系统变量中添加的是python3.9的路径，所以输入python会默认启动python3.9.13的版本

  - 如果想直接在指定python版本安装包，可以在pip前加 “python3.x -m“ 命令，如：

    ```
    python3.8 -m pip install django
    ```

    



# 三、Python 虚拟环境

即便你有多个 Python 版本，也无法解决：**不同项目依赖不同库版本**，解决方案就是 —— 虚拟环境。

如果你需要每个项目单独创建一个虚拟环境来执行，可以使用例如：**pipenv、conda、poetry、uv等工具为每个项目创建独立环境**，实现完全隔离。

但是如果每一个小项目都单独维护一个虚拟环境，管理和切换成本会逐渐增加。因此，通常会按照项目类型划分一些 **“公共虚拟环境”**，例如 *Web 开发环境、数据分析环境、深度学习环境*等，**在保证依赖隔离的同时降低管理复杂度**。下面将介绍这种公共虚拟环境的创建及高效切换方案。

## 1. 创建虚拟环境

```
python -m venv project_venv
```

- 建议统一管理目录，把所有公共的虚拟环境放在一个目录下，例如：

<img src="3-python安装及虚拟环境管理.assets\image-20260303142914139.png" alt="image-20260303142914139" width="60%" />



## 2. 激活虚拟环境

```bash
# Windows CMD
虚拟环境目录\venv\Scripts\activate.bat

# Windows PowerShell
虚拟环境目录\venv\Scripts\Activate.ps1

# macOS / Linux (Bash / Zsh)
source 虚拟环境目录/venv/bin/activate

# 成功后前面会出现
(project_venv)
# 或执行下面命令，输出的是虚拟环境目录，说明成功
python -c "import sys; print(sys.executable)"

# 输入 deactivate 可退出当前虚拟环境
deactivate
```



## 3. 环境依赖的相关操作

```bash
# 1. 安装依赖：激活虚拟环境后，使用pip命令安装
pip install tqdm

# 2. 查看当前环境下有哪些依赖
pip list

# 3. 导出依赖
pip freeze > requirements.txt

# 4. 恢复依赖
pip install -r requirements.txt
```



# 四、一键切换虚拟环境脚本

当虚拟环境多了以后，每次手动 cd + activate 非常麻烦。

于是我写了一个一键切换虚拟环境的脚本 `switch_env.bat`，代码链接：

主要功能包括：

- **自动识别指定目录下的所有虚拟环境**
- **自动读取 Python 版本**
- **生成菜单**
- **输入数字自动进入**

将脚本放在前面切换不同python版本bat目录下，可实现在任意终端输入：**`switch_env`** 命令，选择切换到不同的python环境

<img src="3-python安装及虚拟环境管理.assets\image-20260303145344576.png" alt="image-20260303145344576" width="80%" />

<img src="3-python安装及虚拟环境管理.assets\image-20260303145412880.png" alt="image-20260303145412880" width="80%" />

核心原理：

- 遍历文件夹
- 检测 Scripts\python.exe
- 执行 `python --version`
- 动态生成菜单
- call activate.bat



# 结语

Python 强大，但环境管理是门技术活。只要理清安装路径、理解 PATH 的查找机制，并善用虚拟环境进行依赖隔离，多版本共存和项目切换都可以变得清晰而可控。当环境不再成为负担，你就能把更多精力放在真正有价值的事情上——写代码、做项目、解决问题。这也是良好工程习惯带来的长期收益。希望这篇文章能帮你建立一套属于自己的 Python 环境管理体系。







## 📬 关注我 · 获取更多内容

### **📌 南墨的技术小栈**

<img src="3-python安装及虚拟环境管理.assets\qrcode_for_gh_8be4598ab15d_1280.jpg" alt="qrcode_for_gh_8be4598ab15d_1280" width="30%" />

这里是我的个人知识分享空间。我会定期整理和分享工作与学习中积累的经验与资源，内容涵盖：

- 算法分享 —— 深入讲解算法原理、实现思路与代码示例。
- 工具分享 —— 推荐实用工具与脚本，包括我个人开发的小工具和精选开源工具。
- 开源项目 —— 精选 GitHub 上高星项目，拆解原理、使用方法和最佳实践。
- 数据分享 —— 工作学习中收集整理的数据资源。

无论你是技术爱好者、算法研究者，还是对数据与开源感兴趣的朋友，这里都希望能成为你学习、探索和实践的参考空间。

若在阅读或使用过程中有任何疑问，欢迎在公众号私信我，我会尽快与您交流。
