---
title: "控件语法"
---
# 控件语法

将代码块的语言标注成xaml并在开头写`<!-- pcl -->`。则直接作为控件代码显示。

````markdown
```xaml
<!-- pcl -->
<local:MyCard Margin="5">
    <StackPanel Margin="10">
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="这一段将不会作为代码块使用，而是作为控件插入到文档中"/>
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="此方式的代码也需要转义"/>
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="因为语法原因，此方式所创建的控件会有一层 &lt;StackPanel/&gt; 嵌套"/>
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
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="此方式的代码也需要转义"/>
        <TextBlock
            Margin="0,5"
            FontSize="13"
            Text="因为语法原因，此方式所创建的控件会有一层 &lt;StackPanel/&gt; 嵌套"/>
    </StackPanel>
</local:MyCard>
```