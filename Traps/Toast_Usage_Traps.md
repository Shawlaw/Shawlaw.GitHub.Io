# Toast在使用上的一些坑

想起要记录这个主要是之前在开发时遇到的，在Android 7.1.1上面直接使用系统的Toast在主线程被阻塞的情形下会出现BadTokenException崩溃，现在项目里用的都是已经封装了一层的Toast工具类。

具体原因和解决方案可以参见美团技术团队的这篇文章里的第二点：

[Toast与Snackbar的那点事](https://tech.meituan.com/toast_snackbar_replace.html)

[Toast与Snackbar的那点事【WebArchive备份版】](https://web.archive.org/web/20180412164812/https://tech.meituan.com/toast_snackbar_replace.html)

[Toast与Snackbar的那点事【网页截图备份版】](./Toast_snackbar_replace.png)

