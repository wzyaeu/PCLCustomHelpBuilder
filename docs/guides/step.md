---
title: "使用流程"
index: 0
---

# 使用流程

通过一系列步骤构建页面并发布。

## 构建页面

### 1. 编写文档

参阅[编写教程](/指南/编写教程)，或先跳过此步骤，通过默认文档构建。

### 2. 编写配置文件

1. 创建`config.json`在项目根目录。
2. 填写内容
    ```json
    {
        "name": "PCLCustomHelpBuilder", 
        "output_url": ""
    }
    ```
3. 格式参阅[配置文件](/指南/编写教程/配置文件)。

### 3. 构建页面

1. 安装依赖：`pip install -r requirements.txt`。
2. 运行：`python main.py`，将在产出目录生成xaml页面。

---

## 扩展内容

### ex1. 个性化定制

- 自定义项目名：修改`config.json`的`name`键，将改变页面的标题。
- 配置页脚：参阅[页脚](/指南/编写教程/页脚)

### ex2. 本地预览

#### 使用`http.server`共享产出目录

1. 修改`config.json`的`output_url`键为`http://localhost:8888/`。
2. 运行：`python main.py`。
3. 运行：`cd ./output`。
4. 运行：`python -m http.server 8888`。
5. 将`http://localhost:8888/Custom.xaml`作为联网主页下载地址。

#### 使用 vscode 的`Live Server`共享产出目录

1. 通过 vscode 打开你的项目目录。
2. 安装`Live Server`插件（插件ID `ritwickdey.LiveServer`）
3. 修改`config.json`的`output_url`键为`http://localhost:5050/`（端口为`Live Server`默认开启的端口）。
4. 运行：`python main.py`。
5. 点击下部状态栏的`Go Live`。
6. 开启后将`http://localhost:5050/Custom.xaml`作为联网主页下载地址。