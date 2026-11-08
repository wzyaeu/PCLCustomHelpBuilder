---
title: "文档模板扩展语法"
index: 5
---

# 文档模板扩展语法

通过文档模板生成一个段落，参阅[文档模板](/指南/项目定制/文档模板)。

## 引用文档模板语法

使用此种格式创建：
````markdown
```template
{template_path}
{parameter1}={input1}
{parameter2}={input2}
...
```
````

其中`{template_path}`是模板名，`{parameter1}={input1}`是变量。

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