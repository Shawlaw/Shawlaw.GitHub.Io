# Shawlaw 的个人主页

[访问主页](https://shawlaw.github.io/) · [StudioKit](https://shawlaw.github.io/studiokit/)

本站收录开源作品、开发记录和技术笔记。历史文章仍存放在原来的 Markdown 目录。发现问题可在[本站仓库提交 Issue](https://github.com/Shawlaw/Shawlaw.GitHub.Io/issues)。

## 本地看首页

需要 Python 3.10 或更高版本，Windows 可把 `python` 换成 `py -3`。

```sh
python tools/homepage.py check
python tools/homepage.py build
python -m http.server 8000 --directory _site
```

访问 `http://localhost:8000/`。也可直接打开 `_site/index.html`。默认使用随仓库提供的项目快照，历史文章链接仍指向线上原地址。全站的 Markdown 构建由 GitHub Pages 工作流完成。

## 新增、修改和删除项目

项目清单是 `homepage/projects.json`，每条记录的 `id` 应保持稳定。同组按清单里的顺序显示。终端示例中的 `demo-tool` 需要换成实际存在的公开仓库。

```sh
python tools/homepage.py add --id demo-tool --repo Shawlaw/demo-tool --name "Demo Tool" --description "整理本地开发日志" --category "Windows · 开发工具"
python tools/homepage.py check
python tools/homepage.py build
python tools/homepage.py remove demo-tool
```

- `--group featured` 放进截图作品区，默认 `tools` 放进其他工具区。改顺序、名称或分类时编辑清单。
- `--icon icon.webp` 与 `--screenshot demo.webp` 可选。把同名文件放在 `homepage/assets/`。截图适合使用可公开展示的产品界面。
- `--description-source github` 可选，使用仓库 About 简介，缺失时使用清单里的简介。现有作品的首次展示使用清单中的中文简介。上游 About 和配置的初始值不同时，使用上游新简介。设为 `catalog` 可固定使用手写简介。
- `--screenshot-source main docs/demo.png upstream.png` 可选，表示从项目仓库指定 ref 和路径同步截图。最后一项是用于生成本地预览素材的**上游原图文件**，脚手架计算它的哈希。原图相同就使用本地素材，原图变更后自动用新版。`--screenshot-caption` 可为本地基准截图标注实际版本。新版截图只有配置了 `screenshot_source.caption` 才带图注。
- StudioKit 使用清单里的 `portal` 配置及其公开工具 JSON。子工具上线、下线、改名或更新版本后会跟随变动。
- 删除项目后，下一次构建会一起移除它的卡片和生成的开发记录。确认没有其他条目使用后，可以删除对应的本地素材。
- 新文章按原习惯写 Markdown。在 `homepage/articles.json` 加一条入口，填写链接、标题、分类和可选日期。既有链接保持原路径。

## 版本和截图自动同步

GitHub Pages 以 GitHub Actions 为发布来源。首页仓库推送后构建，定时任务每 15 分钟检查一次，数据和源提交未变化时跳过部署。Actions → **GitHub Pages** → **Run workflow** 可立即触发。全部时间显示按 UTC+8。

- GitHub 最新公开正式 Release 更新卡片的版本、链接和开发记录。只有 tag、草稿或预发行版时，卡片显示项目和仓库入口。
- StudioKit 以部署后的工具清单为准。启用截图同步的项目使用各自仓库维护的截图。下载失败时沿用上次已发布数据。缓存不可用且上游同步失败时，保留现有线上部署。
- 同步默认使用 Actions 的 GitHub Token。若运行日志持续出现跨仓权限或匿名限流问题，在首页仓库配置 `HOMEPAGE_SYNC_TOKEN`。它只需要读取所列公开仓库的 Metadata / Contents，无需写入权限。
- 浏览器直接读取生成结果，更新过程由 Actions 部署站点，不产生 Git 提交。检查周期受 GitHub Actions 调度和 Pages 部署耗时影响。
- 如需发版后主动刷新，来源项目的发布工作流可在发布成功后向本站发 `repository_dispatch` 事件，类型为 `homepage-sync`。StudioKit 应在站点和工具清单成功部署后发送。凭据只需对首页仓库拥有相应的 Contents 写权限，由发出方保存在 Actions Secrets 中。
- GitHub 可能暂停长期无仓库活动的公开仓库定时任务。此时可在 Actions 页面重新启用，项目主动触发和手动运行也可用于同步。

来源仓库的发版工作流可在发布成功后加上这一段。给来源仓库配置 `HOMEPAGE_DISPATCH_TOKEN`，GitHub CLI 在 GitHub 托管的 Ubuntu runner 上可用。

```yaml
- name: Refresh Shawlaw homepage
  env:
    GH_TOKEN: ${{ secrets.HOMEPAGE_DISPATCH_TOKEN }}
  run: gh api --method POST repos/Shawlaw/Shawlaw.GitHub.Io/dispatches -f event_type=homepage-sync
```

[GitHub Pages 构建说明](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) · [GitHub Actions 触发事件](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
