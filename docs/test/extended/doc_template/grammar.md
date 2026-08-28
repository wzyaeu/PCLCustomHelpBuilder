---
title: "文档模板语法"
index: 1
---

# 文档模板语法

## 动态替换语法

动态替换语法是文档模板的特殊语法，可以替换传入的各类数据。

```markdown
[](doctemplate!...)
```

### 参数替换

获取引用文档模板时传入的参数。

格式：
```markdown
[](doctemplate!{attr})
[](doctemplate!{attr}!{default})
[](doctemplate!{attr1}!{attr2}!...!{default})
```

`[](doctemplate!{attr})`格式用于获取参数，例如引用方式
````markdown
```template
/test.md
p1=参数1
```
````
使用`[](doctemplate!p1)`即可替换成`参数1`。格式为纯文本。

---

`[](doctemplate!{attr}!{default})`格式用于获取参数并指定默认文本，例如引用方式
````markdown
```template
/test.md
p1=参数1
```
````
使用`[](doctemplate!p2!defaultp2)`即可替换成默认文本`defaultp2`。

---

`[](post!{attr1}!{attr2}!...!{default})`格式用于参数更复杂的获取，根据顺序依次获取。例如引用方式
````markdown
```template
/test.md
p1=参数1
p2=参数2
```
````
使用`[](doctemplate!p1!p2!d)`，按照顺序最终获取到`p1`的`参数1`。

使用`[](doctemplate!p2!p1!d)`，按照顺序最终获取到`p2`的`参数2`。

### 特例：在代码块里使用参数替换

如默认文档模板`文档目录/.template/github/repo.md`中，在代码块以`{{doctemplate!xxx}}`文本替换。在 代码块里的参数替换 与 普通的链接参数替换 语法基本一样，但 代码块里的参数替换 使用双大括号包裹。[但是没办法和其他使用链接的扩展语法使用相同的逻辑（悲）](hidden!)