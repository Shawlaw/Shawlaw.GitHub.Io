# Git使用时遇到过的问题及解决方案集

问题：git push到Gerrit上时出现 error Missing tree 

解决方案：push时添加如下参数即可

```shell
git push --no-thin origin xxxxxx
```

参考：[git 出现 *error* *Missing* *tree* 的处理办法](http://www.baidu.com/link?url=hzzysUYhcAQoz7joYi6dKz9a7DjQie_B6RshkgbfrV0JRW_8s6n9WdsXnFfKvWu3R9ITb_UnbRflgMMuIsQAS4o0eC84NdDPwYdILksw06m)、[git unpack error on push to gerrit](https://stackoverflow.com/questions/16586642/git-unpack-error-on-push-to-gerrit)

----

问题：想修改提交历史里面的用户名及邮箱等信息

解决方案：

1. 最近的一个提交：

   ```shell
   git commit --amend --author="userName <userEmail>"
   ```

2. 批量修改：需要用到git filter-branch这个“核武器”

   详细命令如下：

   ```shell
    git filter-branch --commit-filter '
            if [ "$GIT_COMMITTER_EMAIL" = "旧邮箱地址" ];
            then
                    GIT_COMMITTER_NAME="新提交用户名";
                    GIT_COMMITTER_EMAIL="新提交邮箱";
                    GIT_AUTHOR_NAME="新提交用户名";
                    GIT_AUTHOR_EMAIL="新提交邮箱";
                    git commit-tree "$@";
            else
                    git commit-tree "$@";
            fi' HEAD
   ```

   批量修改后如果有误，由于git会默认生成一个备份，所以可以执行这句命令进行回退：

   ```shell
   git reset --hard refs/original/refs/heads/你操作的分支
   ```

   如果觉得没有问题，可以通过以下命令来删除这个备份，因为git的这个备份仅支持一份，所以在下一次的filter-branch操作前，需要先删掉之前的备份：

   ```shell
   git update-ref -d refs/original/refs/heads/你操作的分支
   ```

参考：

1. <https://www.jianshu.com/p/7def4f387e9f>
2. <https://git-scm.com/book/zh/v1/Git-%E5%B7%A5%E5%85%B7-%E9%87%8D%E5%86%99%E5%8E%86%E5%8F%B2>
3. <https://stackoverflow.com/questions/14542326/undo-git-filter-branch>
4. <https://stackoverflow.com/questions/6403601/purging-file-from-git-repo-failed-unable-to-create-new-backup>

----

