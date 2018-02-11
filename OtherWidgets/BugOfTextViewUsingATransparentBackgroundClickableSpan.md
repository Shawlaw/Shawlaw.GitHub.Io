## TextView使用ClickableSpan时想去除点击时背景色的坑

问题起源是，TextView里面要用ClickableSpan做个点击，但是呢，点击时不能有背景色，然后上网搜了一下。

发现是设置TextView的highLightColor为透明就能解决问题。

然后我去xml里面给这个TextView设置上了。

> android:textColorHighlight="#00000000"
>

但一运行起来，诶，怎么不生效？点击了还是有背景色。

然后断点一看，奇了怪了，TextView的highLightColor竟然不是0。

然后再运行时用代码把highLightColor设置成0，再运行，好了，点击的时候没有背景色了。

？？？我一脸懵逼，xml的设置竟然和代码里的设置生效情形不一样？？？

然后就跑去翻TextView的源码（Android 26），看到下面这些相关的：
```java
    int mHighlightColor = 0x6633B5E5;

    public TextView(
    		Context context, @Nullable AttributeSet attrs, int defStyleAttr, int defStyleRes) {
    	//别的不在意的代码
    	int textHightlight = 0;
    	textColorHighlight = appearance.getColor(com.android.internal.R.styleable.TextAppearance_textColorHighlight, textColorHighlight);
        //竟然特判了非0！！！！！！！
    	if (textColorHighlight != 0) {
    		setHighlightColor(textColorHighlight);
    	}
    	//别的不在意的代码
    }
    
    @Deprecated
    public void setTextAppearance(Context context, @StyleRes int resId) {
    	final TypedArray ta = context.obtainStyledAttributes(resId, R.styleable.TextAppearance);
    
    	final int textColorHighlight = ta.getColor(
    			R.styleable.TextAppearance_textColorHighlight, 0);
        //竟然特判了非0！！！！！！！
    	if (textColorHighlight != 0) {
    		setHighlightColor(textColorHighlight);
    	}
    	//别的不在意的代码
    }
    
    public void setHighlightColor(@ColorInt int color) {
    	if (mHighlightColor != color) {
    		mHighlightColor = color;
    		invalidate();
    	}
    }
```

两个从xml属性读取highLightColor的地方，在置值之前，竟然都特判了非零才置值。

真是一口老血都喷出来了。竟然有这么一个坑。

再打开Android 15的TextView的源码搜了下，发现也是一样的逻辑。

所以这是一直没变过的逻辑，真是活久见。

所以最后的解决方案只能是在代码里设置这个高亮色为透明。

> aTextView.setHighlightColor(Color.TRANSPARENT);



### 附：ClickableSpan的使用

```java
    SpannableString str = new SpannableString(mActivity.getString(R.string.your_str));
    str.setSpan(new ClickableSpan() {
        @Override
        public void onClick(View widget) {
            //你的点击事件
        }

        @Override
        public void updateDrawState(TextPaint ds) {
            ds.setUnderlineText(false); //去除下划线
            ds.setColor(Color.parseColor("#颜色值")); //设置文字颜色
            ds.bgColor = Color.TRANSPARENT; //文字绘制时的背景，默认已经是透明
        }
    }, 1 /* 文字开始index */, 7 /* 文字结束index + 1 */, Spanned.SPAN_INCLUSIVE_INCLUSIVE);
    TextView tv;
    tv.setText(str);
    tv.setMovementMethod(LinkMovementMethod.getInstance());
```

