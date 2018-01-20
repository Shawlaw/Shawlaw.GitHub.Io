注：本文中附带的源码均为Android 8.0(26)的源码。

# ViewGroup中MotionEvent事件的分发流程

阅读View和ViewGroup的源码可以得出以下分析

1. dispatchTouchEvent 【ViewGroup.dispatchTouchEvent】
   1. onInterceptTouchEvent，如果没消费，继续下一步
   2. 遍历调用child的dispatchTouchEvent，如果没消费，继续下一步
   3. super.dispatchTouchEvent 【View.dispatchTouchEvent】
      1. onTouchListener.onTouch，如果没消费，继续下一步
      2. onTouchEvent



# 对于整个Activity的MotionEvent事件的分发流程

断点 + 阅读相关源码可以得出以下分析

1. MessageQueue.next

   1. nativePollOnce

      1. epoll[【Linux IO模式说明】](https://segmentfault.com/a/1190000003063859)收到屏幕的点击事件

      2. native层直接分发到Java层的ViewRootImpl中的WindowInputEventReceiver

      3. WindowInputEventReceiver对事件进行分发

         1. mView.dispatchPointerEvent 【即DecorView.dispatchPointerEvent】

            1. 根据事件类型，调进DecorView.dispatchTouchEvent

               1. 如果Activity未销毁，调到Activity.dispatchTouchEvent

                  1. PhoneWindow.superDispatchTouchEvent

                     1. DecorView.superDispatchTouchEvent

                        1. FrameLayout.dispatchTouchEvent

                           即，走进 **ViewGroup中点击事件的分发流程**

                  2. 如果第1步中没有消费，那么继续分发到Activity.onTouchEvent

               2. 如果Activity已经销毁，调到FrameLayout.dispatchTouchEvent

                  即，走进 **ViewGroup中点击事件的分发流程**

2. 现在回过头来看下Looper.loop的源码

   ```java
   /**
    * Run the message queue in this thread. Be sure to call
    * {@link #quit()} to end the loop.
    */
   public static void loop() {
     
   	...一些这次分析不关心的代码...
         
   	for (;;) {
   		Message msg = queue.next(); // might block
   		if (msg == null) {
   			// No message indicates that the message queue is quitting.
   			return;
   		}

   		// This must be in a local variable, in case a UI event sets the logger
   		final Printer logging = me.mLogging;
   		if (logging != null) {
   			logging.println(">>>>> Dispatching to " + msg.target + " " +
   					msg.callback + ": " + msg.what);
   		}

   		...一些这次分析不关心的代码...
             
   		try {
   			msg.target.dispatchMessage(msg);
   			end = (slowDispatchThresholdMs == 0) ? 0 : SystemClock.uptimeMillis();
   		} finally {
   			...一些这次分析不关心的代码...
   		}
   		...一些这次分析不关心的代码...

   		if (logging != null) {
   			logging.println("<<<<< Finished to " + msg.target + " " + msg.callback);
   		}

   		...一些这次分析不关心的代码...

   		msg.recycleUnchecked();
   	}
   }

   ```

   很明显上文中的分发的路径是从第10行调用进去的，在logging.println开始之前的，但假如我们设置了logging而且在View的OnClickListener添加打log逻辑的话，会发现onClick回调却是在第26行调到的。

   这感觉和第1步里分析的流程不太一样啊。

   再看下View源码里调OnClick方法的地方，发现了onTouchEvent里有这么个逻辑

   ```java
   /**
    * Implement this method to handle touch screen motion events.
    * <p>
    * If this method is used to detect click actions, it is recommended that
    * the actions be performed by implementing and calling
    * {@link #performClick()}. This will ensure consistent system behavior,
    * including:
    * <ul>
    * <li>obeying click sound preferences
    * <li>dispatching OnClickListener calls
    * <li>handling {@link AccessibilityNodeInfo#ACTION_CLICK ACTION_CLICK} when
    * accessibility features are enabled
    * </ul>
    *
    * @param event The motion event.
    * @return True if the event was handled, false otherwise.
    */
   public boolean onTouchEvent(MotionEvent event) {
   	final float x = event.getX();
   	final float y = event.getY();
   	final int viewFlags = mViewFlags;
   	final int action = event.getAction();

   	final boolean clickable = ((viewFlags & CLICKABLE) == CLICKABLE
   			|| (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE)
   			|| (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;

   	...一些这次分析中不关心的代码...

   	if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
   		switch (action) {
   			case MotionEvent.ACTION_UP:
               
   				...一些这次分析中不关心的代码...
                     
   				boolean prepressed = (mPrivateFlags & PFLAG_PREPRESSED) != 0;
   				if ((mPrivateFlags & PFLAG_PRESSED) != 0 || prepressed) {
   					// take focus if we don't have it already and we should in
   					// touch mode.
   					boolean focusTaken = false;
   					if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
   						focusTaken = requestFocus();
   					}

   					if (prepressed) {
   						// The button is being released before we actually
   						// showed it as pressed.  Make it show the pressed
   						// state now (before scheduling the click) to ensure
   						// the user sees it.
   						setPressed(true, x, y);
   					}

   					if (!mHasPerformedLongPress && !mIgnoreNextUpEvent) {
   						// This is a tap, so remove the longpress check
   						removeLongPressCallback();

   						// Only perform take click actions if we were in the pressed state
   						if (!focusTaken) {
   							// Use a Runnable and post this rather than calling
   							// performClick directly. This lets other visual state
   							// of the view update before click actions start.
   							if (mPerformClick == null) {
   								mPerformClick = new PerformClick();
   							}
   							if (!post(mPerformClick)) {
   								performClick();
   							}
   						}
   					}
                     
   				...一些这次分析中不关心的代码...
                     
   				}
               
   				...一些这次分析中不关心的代码...
                     
   				break;
               
   			...一些这次分析中不关心的代码...
                 
   		}

   		return true;
   	}

   	return false;
   }

   /**
    * Call this view's OnClickListener, if it is defined.  Performs all normal
    * actions associated with clicking: reporting accessibility event, playing
    * a sound, etc.
    *
    * @return True there was an assigned OnClickListener that was called, false
    *         otherwise is returned.
    */
   public boolean performClick() {
   	final boolean result;
   	final ListenerInfo li = mListenerInfo;
   	if (li != null && li.mOnClickListener != null) {
   		playSoundEffect(SoundEffectConstants.CLICK);
   		li.mOnClickListener.onClick(this);
   		result = true;
   	} else {
   		result = false;
   	}

     	...一些这次分析中不关心的代码...

   	return result;
   }

   private final class PerformClick implements Runnable {
   	@Override
   	public void run() {
   		performClick();
   	}
   }
   ```

   在ACTION_UP的时候，实际上并不是直接调performClick去触发，而是把performClick裹成一个Runnable然后post到主线程的MessageQueue里，所以自然这个onClick的回调会是在loop源码里的26行那里进行执行的。

   ​

   ### 彩蛋

   看回上文中View部分的源码，会发现onTouchEvent的时候调用onClick事件时有个判断的标志位是focusTaken【第40行】，按字面意思和后面的注释理解，应该是标明当前View的焦点是否被别的View抢走了。

   **true为被抢走了，那么就不触发onClick回调；false为没被抢走，那么就可以触发onClick回调。**

   初始化的默认值是false，就是认为当前View拥有着焦点。

   然后在41到43行的时候根据逻辑判断，有可能把focusTaken的值置为View.requestFocus方法的返回值。

   看下requestFocus的源码和JavaDoc

   ```java
   /**
    * Call this to try to give focus to a specific view or to one of its
    * descendants.
    *
    * A view will not actually take focus if it is not focusable ({@link #isFocusable} returns
    * false), or if it is focusable and it is not focusable in touch mode
    * ({@link #isFocusableInTouchMode}) while the device is in touch mode.
    *
    * See also {@link #focusSearch(int)}, which is what you call to say that you
    * have focus, and you want your parent to look for the next one.
    *
    * This is equivalent to calling {@link #requestFocus(int, Rect)} with arguments
    * {@link #FOCUS_DOWN} and <code>null</code>.
    *
    * @return Whether this view or one of its descendants actually took focus.
    */
   public final boolean requestFocus() {
   	return requestFocus(View.FOCUS_DOWN);
   }
   ```

   具体的实现逻辑，这里就不分析了，毕竟只是彩蛋部分，我们直接看JavaDoc中对这个方法的返回值的说明

   > @return Whether this view or one of its descendants actually took focus.

   **true为当前View/子View成功获取焦点，false为当前View/子View没能成功获取焦点。**

   咦？？？

   我们再看focusTaken的意义：

   **true为被抢走了，即当前View没有焦点；false为没被抢走，即当前View有焦点。**

   嗯。

   requestFocus的返回值的意义和focusTaken的意义正好是相反的。

   这样就会导致focusable且focusableInTouchMode的View，在用户的第一次点击时，并不会回调到OnClickListener。

   根据Android 4.0.3(15)和Android 8.0(26)的View的源码来看，这个逻辑一直没改动。所以这应该是Android系统中一直存在的一个Bug。然后估计由于时间太久远而且这个逻辑位置比较核心，所以不适合进行修复，所以就一直留着。

   栗子：EditText。上网一搜“EditText OnClickListener 无效”，都能找到[大量的文章](https://www.baidu.com/s?w=EditText%20OnClickListener%20%E6%97%A0%E6%95%88)说遇到这个问题。

   解决方案：使用onTouchListener，在ACTION_UP事件时调用原来onClick事件时做的逻辑，并且复写的onTouch方法一直返回false，让事件可以正常分发。