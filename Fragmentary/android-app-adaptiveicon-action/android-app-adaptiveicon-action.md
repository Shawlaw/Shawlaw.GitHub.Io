更新时间：2021年6月2日



# Android应用 AdaptiveIcon 适配实战

Android 8.0开始，系统层新增了AdaptiveIcon这类应用图标，把原来一张图的应用图标资源拆成了前景图和背景图两层的应用图标资源，好处是在Launcher里可以做一些酷炫的动画，而且可以使得应用的图标都风格一致化。

具体的介绍可以参考：

https://developer.android.com/guide/practices/ui_guidelines/icon_design_adaptive

和

https://medium.com/google-design/designing-adaptive-icons-515af294c783



## 默认的AdaptiveIcon实现

直接使用Android Studio新建一个带有Empty Activity的项目运行，即可获得谷歌官方提供的AdaptiveIcon实现示例。

AndroidManifest中的图标配置如下：

![](.\manifest.png)

启动图标相关的资源文件结构如下：

![](.\res_pattern.png)

其中mipmap-mdpi/hdpi/xhdpi/xxhdpi/xxxhdpi里面的两个png资源是用于Android 8.0之前的系统上使用的，就依旧是之前的“一张图资源即可作为应用图标”的实现方式。

而mipmap-anydpi-v26则是Android 8.0及以上系统使用的，是“背景图和前景图组成应用图标”的实现方式。

我们来看一下这个AdaptiveIcon的资源文件内容

```xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
```

可以看到对应的背景图和前景图分别是drawable里的ic_launcher_background和ic_launcher_foreground资源。

而这两个资源是Vector矢量图资源，和我们绝大多数情形下的原应用图标的形式不太一样，所以可以先略过。

看完默认实现之后，我们就对AdaptiveIcon的资源组织结构方式有了一个认识，接下来，我们来基于一个已有应用图标的旧的App添加一个AadaptiveIcon。



## 新增AdaptiveIcon实战

先搬出官方博客的这张图

![](.\pattern_from_official_blog.png)

这整个图就是AdaptiveIcon前后景图层的完整尺寸，按目前最大的分辨率为xxxhdpi来算的话，那么前/后景图层的图像资源尺寸应为432x432，然后中间区域的288x288的矩形是用来放上原来的应用图标，中间区域之外的区域，常规来说应该是透明的。

同时需要注意应用图标最好能保证有效内容都在中间居中的264直径的圆（safe zone）里面，这样可以保证在各个Launcher里也能正常显示完整的有效内容。

从UI同学那边取得了两张432x432的图片资源之后，就可以参照上一节中的组织结构来实现AdaptiveIcon了。

1. 把两个432x432的图像资源放到mipmap-xxxhdpi文件夹下

2. 新建一个mipmap-anydpi-v26的文件夹

3. 在mipmap-anydpi-v26文件夹中新建一个和现有的应用图标资源名同名的xml的资源，我们暂且假设现有的资源名为ic_launcher.png，那么这里就是新建一个ic_launcher.xml文件，具体内容可以参考上一节里面的源码

4. 重新编译运行，在Android 8.0及以上的原生Launcher中可以看到对应的效果

假如背景图层没有特别要求，仅仅是纯色的话，那么背景图层的图像资源可以省略，直接在AdaptiveIcon中，把背景图层的引用指向一个color资源即可。



附件：

1. 在Android 8.1上的原生Launcher安装包，可用于查看适配了AdaptiveIcon后的应用图标效果。Ref：[Pixel Launcher 8.1.0-4429924 (READ NOTES) APK Download by Google LLC - APKMirror](https://www.apkmirror.com/apk/google-inc/pixel-launcher/pixel-launcher-8-1-0-4429924-release/) 

2. [AdaptiveIconPattern.psd](./AdaptiveIconPattern.psd)，按官方博客的示意图用Photoshop创建的AdaptiveIcon图层源文件，方便UI同学参考使用





