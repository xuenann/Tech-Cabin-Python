# uv：Python 新一代包管理工具

随着 Python 生态的不断发展，项目依赖管理、虚拟环境管理和包安装速度逐渐成为开发者关注的重点。传统的 `pip + virtualenv` 组合虽然稳定，但在速度、依赖解析和项目管理方面仍有一定局限。

**uv** 的出现，试图用一个工具解决大多数 Python 项目在「速度、环境、依赖、项目管理」上的痛点。它由 Rust 编写，目标非常明确：**快、统一、遵循标准**。

这篇文章将系统性地介绍 uv 的核心能力，以及它在实际项目中的使用方式。

项目地址：https://github.com/astral-sh/uv

中文文档：https://uv.doczh.com/



# 一、uv 是什么？

**uv** 是一个现代化的 Python 包管理工具，目标是统一并替代以下工具：

| 功能 | 传统工具 |
|---|---|
| 包安装 | pip |
| 虚拟环境 | virtualenv / venv |
| 依赖锁定 | pip-tools |
| Python版本管理 | pyenv |
| 项目管理 | poetry / pipenv |

uv 提供的核心能力：

- 🚀 一个工具替代 `pip`、`pip-tools`、`pipx`、`poetry`、`pyenv`、`twine`、`virtualenv` 等
- ⚡️ 比 `pip` [快 10-100 倍](https://github.com/astral-sh/uv/blob/main/BENCHMARKS.md)
- 🗂️ 提供[全面的项目管理功能](https://uv.doczh.com/#projects)，包含[通用锁文件](https://uv.doczh.com/concepts/projects/layout/#the-lockfile)
- ❇️ [运行脚本](https://uv.doczh.com/#scripts)，支持[内联依赖元数据](https://uv.doczh.com/guides/scripts/#declaring-script-dependencies)
- 🐍 [安装和管理](https://uv.doczh.com/#python-versions) Python 版本
- 🛠️ [运行和安装](https://uv.doczh.com/#tools) 以 Python 包形式发布的工具
- 🔩 包含 [pip 兼容接口](https://uv.doczh.com/#the-pip-interface)，在熟悉 CLI 的同时获得性能提升
- 🏢 支持 Cargo 风格的[工作区](https://uv.doczh.com/concepts/projects/workspaces/)用于可扩展项目
- 💾 磁盘空间高效，通过[全局缓存](https://uv.doczh.com/concepts/cache/)实现依赖去重
- ⏬ 无需 Rust 或 Python 即可通过 `curl` 或 `pip` 安装
- 🖥️ 支持 macOS、Linux 和 Windows



# 二、安装 uv

##### 方式一：独立安装程序

- macOS和Linux

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # 或
  wget -qO- https://astral.sh/uv/install.sh | sh
  # 通过在 URL 中包含版本号来请求特定版本：
  curl -LsSf https://astral.sh/uv/0.7.4/install.sh | sh
  ```

- Windows

  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  # 通过在 URL 中包含版本号来请求特定版本：
  irm https://astral.sh/uv/0.7.4/install.ps1 | iex
  ```

##### 方式二：PyPI

- 如果从 PyPI 安装，建议将 uv 安装到隔离环境中

  ```bash
  pipx install uv
  # 或
  pip install uv
  ```

##### 方式三：Cargo

- uv 可通过 Cargo 安装，但由于依赖未发布的 crate，必须从 Git 仓库构建而非 [crates.io](https://crates.io/)。

  ```bash
  cargo install --git https://github.com/astral-sh/uv uv
  ```

##### 方式四：Homebrew

- macOS

  ```bash
  brew install uv
  ```

##### 方式五：WinGet

- Windows

  ```powershell
  winget install --id=astral-sh.uv  -e
  ```



> 安装完成后，验证安装是否成功
>
> ```powershell
> uv --version
> # 输出类似以下内容，表明安装成功
> uv 0.10.8 (c021be36a 2026-03-03)
> ```



# 三、管理python版本

uv 可以轻松管理多个 Python 版本，无需额外安装 pyenv 等工具。

查看可用的 Python 版本：

```powershell
uv python list

# 输出结果类似如下：
cpython-3.15.0a6-windows-x86_64-none                 <download available>
cpython-3.15.0a6+freethreaded-windows-x86_64-none    <download available>
cpython-3.14.3-windows-x86_64-none                   <download available>
cpython-3.14.3+freethreaded-windows-x86_64-none      <download available>
cpython-3.13.12-windows-x86_64-none                  <download available>
cpython-3.13.12-windows-x86_64-none                  <download available>
cpython-3.13.12+freethreaded-windows-x86_64-none     <download available>
cpython-3.12.13-windows-x86_64-none                  <download available>
cpython-3.12.10-windows-x86_64-none                  <download available>
cpython-3.11.15-windows-x86_64-none                  <download available>
cpython-3.11.9-windows-x86_64-none                   <download available>
cpython-3.10.20-windows-x86_64-none                  <download available>
cpython-3.10.11-windows-x86_64-none                  <download available>
cpython-3.9.25-windows-x86_64-none                   <download available>
cpython-3.9.13-windows-x86_64-none                   <download available>
cpython-3.8.20-windows-x86_64-none                   <download available>
cpython-3.8.10-windows-x86_64-none                   <download available>
cpython-3.7.9-windows-x86_64-none                    <download available>
pypy-3.11.13-windows-x86_64-none                     <download available>
pypy-3.10.16-windows-x86_64-none                     <download available>
pypy-3.9.19-windows-x86_64-none                      <download available>
pypy-3.8.16-windows-x86_64-none                      <download available>
graalpy-3.12.0-windows-x86_64-none                   <download available>
graalpy-3.11.0-windows-x86_64-none                   <download available>
graalpy-3.10.0-windows-x86_64-none                   <download available>
```

```powershell
# 安装特定版本
uv python install 3.11.6

# 安装 PyPy 版本
uv python install pypy3.10

# 设置全局默认 Python 版本
uv python default 3.12
```



# 四、管理虚拟环境

Python 项目通常需要隔离依赖，uv 内置了虚拟环境管理能力。

```powershell
# 创建名为 .venv 的虚拟环境（默认）
uv venv
# 你也可以指定 Python 版本：
uv venv --python 3.11

# 激活环境（macOS/Linux）
source .venv/bin/activate

# 激活环境（Windows）
.venv\Scripts\activate

# 在虚拟环境中安装依赖
uv pip install fastapi

# 为当前项目固定 Python 3.11
uv python pin 3.11
# 这会创建 .python-version 文件，标识项目所需的 Python 版本。
```

**使用 uv run 直接运行**

```powershell
uv run python main.py
```

它会自动：

1. 创建虚拟环境
2. 安装依赖
3. 运行代码



# 五、包管理

uv 也支持现代 Python 项目的依赖管理方式。

```powershell
# 添加依赖
uv add requests

# 移除依赖
uv remove requests

# 查看项目依赖树
uv tree

# 当你拉取项目代码后，可以一键同步依赖：
uv sync
# 它会根据 `pyproject.toml` 和 `uv.lock` 安装依赖。

# 锁定依赖
uv lock
# 会生成uv.lock文件
# 类似：
#   - poetry.lock
#   - package-lock.json
# 保证团队成员使用完全一致的依赖版本。
```



# 六、项目管理

uv 支持 pyproject.toml 格式的项目管理，这是现代 Python 项目的标准配置文件。

```powershell
# 创建项目
uv init my_project
# 项目结构：
# my_project
#  ├── pyproject.toml
#  ├── README.md
#  ├── main.py
#  ├── .gitignore
#  └── .python-version
```

- pyproject.toml：它记录了项目的元数据（名字、版本、作者）以及**项目依赖**。当你运行 `uv add pillow` 时，`uv` 会自动把 `pillow` 写进这个文件里。以后你把项目发给别人，别人只需要运行 `uv sync`，`uv` 就会根据这个文件里的清单，把所有的包原封不动地装好。
- README.md：用来写项目的自我介绍。
- .gitignore：用 Git 来管理代码，这个文件会告诉 Git：“**哪些东西不要上传**”。`uv` 自动帮你写好了规则。它会忽略 `.venv`（虚拟环境文件夹）。因为虚拟环境很大且因人而异，我们通常只分享代码和配置文件（如 `pyproject.toml`），让别人在自己电脑上重新生成环境。
- .python-version：它里面只写了一个版本号（比如 `3.12`）。当你在这个文件夹下运行 `uv run` 时，`uv` 会先看一眼这个文件。如果它发现你系统里没装 3.12，它会**自动**帮你下载一个纯净的 3.12 放在缓存里，确保你的项目永远运行在正确的 Python 版本上。



# 七、项目迁移

uv 可以非常方便地迁移已有项目。

```
# 从 pip 项目迁移
uv venv
uv pip install -r requirements.txt
uv lock

# 从 Poetry 项目迁移
# Poetry 项目一般包含pyproject.toml 和 poetry.lock
uv sync
# uv 会自动解析依赖。
```



# 八、uv 与其他工具对比

| 工具       | 速度     | 虚拟环境 | 项目管理 | Python版本管理 |
| ---------- | -------- | -------- | -------- | -------------- |
| pip        | 慢       | ❌        | ❌        | ❌              |
| pip + venv | 中       | ✔        | ❌        | ❌              |
| pipenv     | 中       | ✔        | ✔        | ❌              |
| poetry     | 中       | ✔        | ✔        | ❌              |
| conda      | 中       | ✔        | ✔        | ✔              |
| **uv**     | **极快** | ✔        | ✔        | ✔              |



# 结语

随着 Python 项目规模不断扩大，传统的 `pip + venv` 工作流逐渐显得笨重。**uv 通过 Rust 的高性能实现，为 Python 开发者提供了一套更快、更现代的工具链。**

如果你正在寻找：

- **更快的包安装速度**
- **更统一的环境管理方式**
- **更现代的 Python 项目管理**

那么 **uv 非常值得尝试**。

未来，uv 很可能成为 Python 生态中的 **下一代标准工具**。





## 📬 关注我 · 获取更多内容

### **📌 南墨的技术小栈**

<img src="4-uv.assets\qrcode_for_gh_8be4598ab15d_1280.jpg" alt="qrcode_for_gh_8be4598ab15d_1280" width="30%" />

这里是我的个人知识分享空间。我会定期整理和分享工作与学习中积累的经验与资源，内容涵盖：

- 算法分享 —— 深入讲解算法原理、实现思路与代码示例。
- 工具分享 —— 推荐实用工具与脚本，包括我个人开发的小工具和精选开源工具。
- 开源项目 —— 精选 GitHub 上高星项目，拆解原理、使用方法和最佳实践。
- 数据分享 —— 工作学习中收集整理的数据资源。

无论你是技术爱好者、算法研究者，还是对数据与开源感兴趣的朋友，这里都希望能成为你学习、探索和实践的参考空间。

若在阅读或使用过程中有任何疑问，欢迎在公众号私信我，我会尽快与您交流。