更新日期：2023年7月4日



# 自用的Git Alias配置

如果不知道Git Alias是什么，可以参考这里：[Git-基础-Git-别名](https://git-scm.com/book/zh/v2/Git-%E5%9F%BA%E7%A1%80-Git-%E5%88%AB%E5%90%8D)、[Git配置别名](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/001375234012342f90be1fc4d81446c967bbdc19e7c03d3000)

使用方法：把以下代码复制到.gitconfig文件内，保存即可。

```sh
[alias]
    st = !sh -c 'date && git status'
    podbase = !sh -c 'date && git push origin develop:$1' -
    pohbase = !sh -c 'date && git push origin HEAD:$1' -
    pocbasewithoutdate = !cb=$(git symbolic-ref --short -q HEAD) && git push origin HEAD:$cb
    pocbase = !sh -c 'date && git pocbasewithoutdate'
    pocbaseforcewithoutdate = !cb=$(git symbolic-ref --short -q HEAD) && git push -f origin HEAD:$cb
    pocbaseforce = !sh -c 'date && git pocbaseforcewithoutdate'
    rmob = !sh -c 'date && git push origin :$1' -
    fp = !sh -c 'date && git fetch --prune'
    mergeo = !sh -c 'date && git fetch && git merge --no-ff origin/$1' -
    dayupc = !sh -c 'git stash && git rboc && git small && git sp'
    dayupd = !sh -c 'git stash && git rbod && git small && git sp'
    #以下用于Gerrit
    pfm = !sh -c 'date && git push origin HEAD:refs/for/master'
    pdm = !sh -c 'date && git push origin HEAD:refs/drafts/master'
    pfcwithoutdate = !cb=$(git symbolic-ref --short -q HEAD) && git push origin HEAD:refs/for/$cb
    pfc = !sh -c 'date && git pfcwithoutdate'
    pfd = !sh -c 'date && git push origin HEAD:refs/for/develop'
    pntfd = !sh -c 'date && git push --no-thin origin HEAD:refs/for/develop'
    pdcwithoutdate = !cb=$(git symbolic-ref --short -q HEAD) && git push origin HEAD:refs/drafts/$cb
    pdc = !sh -c 'date && git pdcwithoutdate'
    pdd = !sh -c 'date && git push origin HEAD:refs/drafts/develop'
    pf = !sh -c 'date && git push origin HEAD:refs/for/$1' -
    pntf = !sh -c 'date && git push --no-thin origin HEAD:refs/for/$1' -
    pd = !sh -c 'date && git push origin HEAD:refs/drafts/$1' -
    #以上用于Gerrit
    cob = !sh -c 'date && git checkout -b $1' -
    co = !sh -c 'date && git checkout $1' -
    sl = !sh -c 'date && git stash list'
    pr = !sh -c 'date && git pull --rebase'
    rbc = !sh -c 'date && git rebase --continue'
    rbm = !sh -c 'date && git rebase master'
    rbom = !sh -c 'date && git fetch && git rebase origin/master'
    rbd = !sh -c 'date && git rebase develop'
    rbod = !sh -c 'date && git fetch origin develop && git rebase origin/develop'
    rbo = !sh -c 'date && git fetch && git rebase origin/$1' -
    cma = !sh -c 'date && git commit --amend'
    rbocwithoutdate = !cb=$(git symbolic-ref --short -q HEAD) && git rebase origin/$cb
    rboc = !sh -c 'date && git fetch && git rbocwithoutdate'
    cma = !sh -c 'date && git commit --amend'
    sp = !sh -c 'date && git stash pop'
    rc = !sh -c 'date && git rm --cached'
    smu = !sh -c 'date && git submodule update'
    small = !sh -c 'date && git submodule init && git submodule sync && git submodule update && date'
    #以下用于Gitlab
    pbf = !sh -c 'date && git push origin $1 --force' -
    #以上用于Gitlab
```

