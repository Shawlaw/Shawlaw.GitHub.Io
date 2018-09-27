# 升级gradle脚本中的各依赖的版本号后却红色波浪线提示”All com.android.support libraries must use the exact same version specification (mixing versions can lead to runtime crashes). “

原因是部分依赖的第三方库会依赖了不同版本的support库，然后就出现了这个问题。

解决方案是在本App的依赖配置里面，显式地把旧版的support库都添加进来，并使用最新的版本号。

具体参见以下图片。

![原网页截图快照](./All_com_android_support_libraries_must_use_the_exact_same_version_specification_ref_screen_shot.png)

来源是：[All com.android.support libraries must use the exact same version specification](https://stackoverflow.com/questions/42374151/all-com-android-support-libraries-must-use-the-exact-same-version-specification)