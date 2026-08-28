```xaml
<!-- pcl -->
<local:MyCard Margin="0,0,0,3">
    <StackPanel Margin="15">
        <StackPanel Orientation="Horizontal">
            <Border CornerRadius="17"
                    Width="34"
                    Height="34">
                <Border.Background>
                    <ImageBrush
                        ImageSource="https://avatars.githubusercontent.com/u/{{doctemplate!userid!0}}"
                        Stretch="UniformToFill"
                        AlignmentX="Center"
                        AlignmentY="Center"/>
                </Border.Background>
            </Border>
            <TextBlock Margin="10,3,3,3"
                       FontWeight="Bold"
                       FontSize="21"
                       VerticalAlignment="Center"
                       Foreground="{DynamicResource ColorBrush3}"
                       Text="{{doctemplate!repo!Unkown Repo}}"/>
        </StackPanel>
    </StackPanel>
    <TextBlock Margin="0,10,10,0"
               FontSize="13"
               Opacity="0.5"
               HorizontalAlignment="Right"
               VerticalAlignment="Top"
               TextAlignment="Right"
               Foreground="{DynamicResource ColorBrush1}"
               Text="Github Repo&#10;点击打开"/>
    <local:MyButton
        Opacity="0"
        EventType="打开网页"
        EventData="https://github.com/{{doctemplate!repo}}"/>
</local:MyCard>
```