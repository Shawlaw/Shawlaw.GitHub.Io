更新时间：2021年6月6日11:03:37



# 应用开发中涉及的开源许可证

大家在开发软件的时候，或多或少都会引用一些第三方的开源库，至少Android开发的话，AndroidX那一套库几乎是少不了的。

而如果有计划开发一个开源软件的话，那么开源许可证的选择也是有需要了解的。

根据阮一峰的博客 [如何选择开源许可证？](http://www.ruanyifeng.com/blog/2011/05/how_to_choose_free_software_licenses.html)  大家可以方便快捷地确定自己的开源软件所用的许可证。

![](./free_software_licenses.png)



而根据许多许可证的要求，在开发中使用到的话，是需要在开发的软件中添加说明文档，附上各开源软件的许可说明的，在应用内这个是一个独立的界面。

但可能引入开源库的同学不太了解这个，对于Java/Kotlin层的库的引入，可以使用谷歌提供的开源库说明库来方便地引入这个界面，具体的接入使用方式参考该库的说明页面：

[Include open source notices](https://developers.google.com/android/guides/opensource)



需要注意的是，这个库对于Native层的引入情况的扫描是不太完备的，Native层的OSS（OpenSourceSoftware）使用情况可以使用[fossology](https://www.fossology.org/)和[Protecode](https://en.wikipedia.org/wiki/Protecode)这两个工具来扫描apk获得。