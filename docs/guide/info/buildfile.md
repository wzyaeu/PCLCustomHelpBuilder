---
title: "构建指南"
---

# 构建指南

将文档内容构建成 PCL 可访问的文档页面。

## 构建指令

运行`python main.py`即可构建文档页面。文档页面位于`output/`中。

## 部署

部署文档页面供用户访问。可以使用自己的方式部署，本指南将介绍以下开发环境的部署方式：

### 使用`http.server`部署文档页面

1. 修改`config.json`的`output_url`键为`http://localhost:8888/`。
2. 运行：`python main.py`。
3. 运行：`cd ./output`。
4. 运行：`python -m http.server 8888`。
5. 将`http://localhost:8888/Custom.xaml`作为联网主页下载地址。

### 使用 vscode 的`Live Server`部署文档页面

1. 通过 vscode 打开你的项目目录。
2. 安装`Live Server`插件（插件ID `ritwickdey.LiveServer`）
3. 修改`config.json`的`output_url`键为`http://localhost:5050/`（端口为`Live Server`默认开启的端口）。
4. 运行：`python main.py`。
5. 点击下部状态栏的`Go Live`。
6. 开启后将`http://localhost:5050/Custom.xaml`作为联网主页下载地址。