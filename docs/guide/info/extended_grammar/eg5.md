---
title: "扩展语法"
index: 4
---

# 控件扩展语法

显示一段xaml代码，直接作为控件显示。将代码块的语言标注成xaml并在开头写`<!-- pcl -->`即可。

格式：将代码块的语言标注成xaml并在开头写`<!-- pcl -->`。

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