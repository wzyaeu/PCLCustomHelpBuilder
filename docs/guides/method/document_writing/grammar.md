---
title: "支持的语法"
index: 0
---

# 支持的语法

## 支持语法

PCLCustomHelpBuilder 支持以下语法：

- 标题语法
- 段落语法
  - 换行语法
  - 强调语法
    - 粗体、斜体、斜粗体
  - 删除线语法
  - 代码语法
- 引用块语法
- 列表语法
- 表格语法
- 代码块语法
  - 语言标识
- 分隔线语法
- 链接语法
- 图片语法
- 转义字符语法

# 不支持语法

PCLCustomHelpBuilder 不支持以下语法写法：

- 语法高亮
- 链接图片
- 内嵌HTML
- 其他语法都会转为普通段落

# 扩展语法

PCLCustomHelpBuilder 含有一些扩展语法。

## 事件语法

创建一个可以调用 PCL [自定义事件](https://github.com/Meloong-Git/PCL/wiki/%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BA%8B%E4%BB%B6)的按钮。

```markdown
[打开一个弹窗](event!弹出窗口!标题|内容)
```
[打开一个弹窗](event!弹出窗口!标题|内容)

## 文档跳转语法

创建一个可以跳转至本项目其他文档的按钮。

```markdown
[打开介绍](jump!介绍)

[打开指南](/指南)
```
[打开介绍](jump!介绍)

[打开指南](/指南)

## 黑幕语法

创建一段黑幕文本。

```markdown
[在这里输入一段看不见的内容](hidden!)
```
[在这里输入一段看不见的内容](hidden!)

## 多类型引用块语法

创建除普通样式外其他颜色的引用块。

```markdown
> [warn]
> 警告

> [tip]
> 提示
```
> [warn]
> 警告

> [tip]
> 提示

## 控件扩展语法

显示一段xaml代码，直接作为控件显示。将代码块的语言标注成xaml并在开头写`<!-- pcl -->`即可。

````markdown
```xaml
<!-- pcl -->
<local:MyCard Margin="5">
    <StackPanel Margin="10">
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="这一段将不会作为代码块使用，而是作为控件插入到文档中"/>
    </StackPanel>
</local:MyCard>
```
````
```xaml
<!-- pcl -->
<local:MyCard Margin="5">
    <StackPanel Margin="10">
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="这一段将不会作为代码块使用，而是作为控件插入到文档中"/>
    </StackPanel>
</local:MyCard>
```

## 文档模板扩展语法

通过文档模板生成一个段落，参阅[文档模板](/指南/编写教程/文档模板)。

### 文档模板语法格式

使用类似：
````markdown
```template
{template_path}
{parameter1}={input1}
{parameter2}={input2}
...
```
````
的格式创建文档模板。

````markdown
```template
test
```
```template
test
p1=参数1
```
````
```template
test
```
```template
test
p1=参数1
```

---

````markdown
```template
github/repo
userid=74000668
repo=Meloong-Git/PCL
```
````
```template
github/repo
userid=74000668
repo=Meloong-Git/PCL
```