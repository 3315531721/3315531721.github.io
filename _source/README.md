# X-ING 内容管理

在站点目录运行 `python3 -B _source/admin.py`，然后打开 http://127.0.0.1:57821/。可以编辑封面标题和签名、课程简介与笔记、四个阶段的学习目标，以及项目和论文笔记中的补充记录。

保存草稿会更新 `_source/content.json` 并重建本地页面。预览显示已保存的版本。点「发布到 GitHub Pages」会使用本机现有 Git 凭据，把内容和生成的页面提交到站点仓库的 `main` 分支。HTTPS 公网站点由 GitHub Pages 继续提供。本地后台只监听回环地址，公网无法访问。

发布前会核对远端模板与内容版本。如果有其他人更新了仓库，请先同步和合并本地草稿。只有可公开的内容应通过后台发布，课程原始资料仍由私有仓库管理。

封面和书桌插画由 ImageGen 生成。视觉设计参考 [Sakurairo](https://github.com/mirai-mamori/Sakurairo)。Bootstrap 的许可见 `assets/bootstrap-LICENSE.txt`。
