更新时间：2021年6月11日



## Android JNI开发相关



### CMake和ndk-build选哪一个

新引入的都建议用CMake，全平台适用的编译方式

现有项目的话，如无必要，直接沿用即可。

附一个StackOverflow上的问答以供参考 [Difference between CMake and NDK-build in android studio project](https://stackoverflow.com/questions/39589427/difference-between-cmake-and-ndk-build-in-android-studio-project/39601122#39601122)



### so库的加载方式

1. System.load(文件路径名)
2. System.loadLibrary(so文件去除lib前缀和so后缀之后的文件名)，例如libmarsxlog.so，在加载时则是调用 System.loadLibrary("marsxlog")



### 在打包时排除特定so库

对于要仅保留特定CPU架构的so库的case，直接调整gradle脚本中的如下内容即可

````groovy
android {
	defaultConfig {
		ndk {
			abiFilters "armeabi-v7a"
		}
	}
}
````

而如果确定要打包时排除特定的so库的话，则是在gradle脚本中加入如下内容，注意需要完整的相对路径，包括对应的cpu架构

````groovy
android {
	packagingOptions {
		exclude 'lib/armeabi-v7a/libmarsxlog.so'
	}
}
````



### 确定so库的引入的依赖链

有时候我们中途接手一个项目，对于项目的依赖关系并不是我们一步步地加上的，所以我们并不是那么清楚项目中的so库都是怎么加进来的。

直接在lib目录下的so库还好说，直接看git log就可以，但对于通过gradle依赖/aar包来引入的so库，就没有那么容易确定了。

这个目前的猜想是从gradle的编译task实现细节来入手，还在研究中。