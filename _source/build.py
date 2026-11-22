"""Regenerate the portfolio from its curated public content using Python 3."""
from html import escape
from json import dumps
from pathlib import Path
from urllib.parse import quote

from content import read_content

ROOT = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/3315531721/CS-lecture"

GROUPS = {
    "foundations": ("数学与通识", (
        ("cs-intro", "计算机导论", "Introduction to Computer Science", "数据表示、计算机分层与算法入门。", "把一个整数分别表示成二进制与十六进制，再说明两种写法如何互换。"),
        ("linear-algebra", "线性代数", "Linear Algebra", "向量、矩阵、线性变换与特征值。", "画出二维基向量经过矩阵变换后的方向，解释矩阵两列各代表什么。"),
        ("physics", "大学物理", "General Physics", "从物理模型出发，用量纲和数量级检查推导。", "对斜面上的物体画受力图，列出方程，并检查极端角度时的结果。"),
        ("english", "高级英语", "Advanced English", "技术阅读、摘要与英语听读。", "为一篇技术文章写英文摘要，保留问题、方法与主要结论。"),
    )),
    "programming": ("程序设计与实验", (
        ("c-programming", "C 语言程序设计", "C Programming", "数组、指针、结构体和文件处理。", "用结构体和文件读写做一个小型命令行程序，说明输入失败怎么处理。"),
        ("c-lab", "C 语言程序设计实验", "C Programming Lab", "从编译与调试到边界输入测试。", "为同一道题预先写好正常、边界和非法输入，再实际运行并核对输出。"),
        ("algorithms", "数据结构与算法", "Data Structures and Algorithms", "线性结构、树与图，以及排序和复杂度。", "实现图遍历，用邻接表解释每个顶点和边被访问的次数。"),
        ("android", "移动应用开发", "Mobile Application Development", "Activity、消息传递、广播和本地数据库。", "把新闻列表、详情和发布流程串起来，再测试关键词过滤和返回后的刷新。"),
    )),
    "systems": ("计算机系统与数据库", (
        ("digital", "数字电子技术", "Digital Electronic Technology", "逻辑门、组合逻辑与时序逻辑。", "列出半加器真值表，再用异或与与门写出输出表达式。"),
        ("os", "操作系统", "Operating Systems", "进程与地址空间、同步、虚拟化和持久化。", "比较进程与线程共享的资源，解释两个线程为什么仍然需要同步。"),
        ("databases", "数据库原理及应用 A", "Database Principles and Applications A", "关系建模、SQL、索引和事务。", "给一个课程管理场景建表，用唯一约束与外键处理重复数据。"),
    )),
    "ai-data": ("人工智能与数据", (
        ("ai", "人工智能导论", "Introduction to Artificial Intelligence", "状态空间搜索、知识表示与学习方法。", "在同一个小地图上比较广度优先搜索和启发式搜索的访问顺序。"),
        ("data-science", "数据科学", "Data Science", "数据审计、划分、建模与结果复核。", "检查样本标识、重复记录和训练集划分，再选择与任务匹配的评估指标。"),
        ("deep-learning", "深度学习", "Deep Learning", "用 PyTorch 对照 MLP、CNN 和自定义网络。", "固定数据划分和训练轮数后做结构对照，最后使用独立测试集报告结果。"),
    )),
}
COURSES = {row[0]: row[1:] for _, rows in GROUPS.values() for row in rows}
CONTENT = read_content(COURSES)

STATUS = {
    "english": "仓库含听读材料；网页展示学习任务。",
    "c-programming": "仓库含课程大纲；网页展示练习方向。",
    "c-lab": "仓库含源代码与本地调试配置；网页展示实验检查点。",
    "algorithms": "仓库含课程材料；网页展示复习要点。",
    "digital": "仓库含课程资料；网页展示基础练习。",
}
NJU = "https://jyywiki.cn/OS/2026/"
CMU = "https://15445.courses.cs.cmu.edu/"

SOURCE_CODE = {
    "deep-learning": ('Python · MNIST 模型定义', """def make_cnn():
    return nn.Sequential(
        nn.Conv2d(1, 8, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(8 * 14 * 14, 10),
    )"""),
    "android": ('Java · Room 按标题查询', """@Query("SELECT * FROM news WHERE instr(title, :keyword) > 0 OR :keyword = '' "
        + "ORDER BY publishedAt DESC, id DESC")
List<News> search(String keyword);"""),
    "data-science": ('Python · 信号文件与标签的一致性校验', """labels = pd.read_csv(data_dir / "REFERENCE.csv").set_index("Recording")
signals = sorted(data_dir.glob("*.mat"))
assert {signal.stem for signal in signals} == set(labels.index), (
    "MAT/label ID mismatch"
)"""),
    "studyflow": ('Kotlin · 作业筛选与排序节选', """return tasks.asSequence()
    .filter { task ->
        term.isEmpty() || task.title.contains(term, ignoreCase = true) ||
            (courseNames[task.courseId] ?: "").contains(term, ignoreCase = true)
    }
    .filter { task ->
        when (filter) {
            TaskFilter.ALL -> true
            TaskFilter.URGENT -> task.status != TaskStatus.DONE_LOCAL &&
                !task.dueAt.isAfter(now.plusDays(3))
            TaskFilter.INCOMPLETE -> task.status != TaskStatus.DONE_LOCAL
            TaskFilter.DONE -> task.status == TaskStatus.DONE_LOCAL
        }
    }
    .sortedWith(compareBy<HomeworkTask> { it.status == TaskStatus.DONE_LOCAL }.thenBy { it.dueAt })
    .toList()"""),
}
PLAN = [
    ("基础", ("cs-intro", "c-programming", "c-lab", "linear-algebra"), "先把指针与数组、向量与矩阵练熟。留下一个可编译的小程序和一页推导笔记。"),
    ("系统", ("algorithms", "digital", "os", "databases"), "从复杂度、逻辑电路走到进程和数据存储。完成一次图遍历、一道进程题和一组 SQL 查询。"),
    ("应用", ("android", "ai", "data-science"), "从应用开发和数据分析各做一个小闭环，记录关键设计、输入输出和复现步骤。"),
    ("实验", ("deep-learning",), "先复现 MNIST 的结构对照，再选一个模型改动做单变量实验。并行整理 Transformer 阅读笔记。"),
]


def section(title, content, id_name=""):
    anchor = f' id="{id_name}"' if id_name else ""
    return f'<section class="section"{anchor}><h2 class="mb-3">{title}</h2>{content}</section>'


def card(title, description, href):
    return f"""<div class="col"><article class="card feature-card h-100"><div class="card-body">
      <h3><a href="{href}">{title} <span aria-hidden="true">↗</span></a></h3>
      <p class="minor">{description}</p>
    </div></article></div>"""


def cards(items):
    return '<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3 cards">' + ''.join(items) + '</div>'


def code_box(key, context):
    label, code = SOURCE_CODE[key]
    return f"""<div class="prose"><p>{context}</p>
      <details open><summary>{label}</summary><pre><code>{escape(code)}</code></pre></details></div>"""


def page_intro(title, description, parent=None):
    trail = (f'<nav aria-label="面包屑"><ol class="breadcrumb mb-3"><li class="breadcrumb-item"><a href="{parent[1]}">{parent[0]}</a></li><li class="breadcrumb-item active" aria-current="page">{title}</li></ol></nav>' if parent else "")
    return f'<header class="page-intro"><div class="container">{trail}<h1>{title}</h1><p>{description}</p></div></header>'


def write(path, title, description, active, body, masthead):
    rel = "../" if "/" in path else "./"
    home_class = ' class="iro-home"' if path == "index.html" else ""
    nav_items = (("首页", "index.html"), ("课程档案", "courses.html"), ("课程规划", "plan.html"), ("项目", "projects.html"), ("论文笔记", "notes.html"))
    nav = []
    for name, target in nav_items:
        current = ' aria-current="page"' if path == target else ''
        if active == target and path != target:
            current = ' aria-current="true"'
        url = rel if target == "index.html" else rel + target
        nav.append(f'<a class="nav-link" href="{url}"{current}>{name}</a>')
    nav_markup = "\n".join(nav)
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="theme-color" content="#f5eef2">
  <title>{title} · X-ING</title>
  <link rel="stylesheet" href="{rel}assets/bootstrap.min.css">
  <link rel="stylesheet" href="{rel}assets/portfolio.css">
  <script src="{rel}assets/search-index.js" defer></script>
  <script src="{rel}assets/portfolio.js" defer></script>
</head>
<body id="top"{home_class}>
  <a class="visually-hidden-focusable" href="#main">跳到正文</a>
  <header class="site-header">
    <a class="brand" href="{rel}" aria-label="X-ING 学习作品集首页">X‑ING</a>
    <div class="nav-pod">
      <button class="nav-toggle" type="button" aria-controls="site-navigation" aria-expanded="false">导航</button>
      <nav id="site-navigation" class="nav site-nav" aria-label="主导航">{nav_markup}</nav>
      <button class="search-trigger" type="button" data-search aria-label="站内搜索"><span class="search-icon" aria-hidden="true"></span></button>
    </div>
    <button class="theme-toggle" type="button" aria-label="切换深色模式" aria-pressed="false">☾</button>
  </header>
  <main id="main">
{masthead}
    <div class="container site-content">
{body}
    </div>
  </main>
  <a class="back-top" href="#top" aria-label="返回顶部">↑</a>
  <footer class="site-footer">
    <div class="container">
      <p><strong>X‑ING</strong> · <a href="{GITHUB}">GitHub 私有仓库 ↗</a></p>
      <p class="small minor">主题设计参考 <a href="https://github.com/mirai-mamori/Sakurairo">Sakurairo</a></p>
    </div>
  </footer>
  <dialog class="search-dialog" aria-labelledby="search-title">
    <form method="dialog" class="search-head"><h2 id="search-title">站内搜索</h2><button type="submit" aria-label="关闭搜索">×</button></form>
    <label class="visually-hidden" for="site-search">查找课程、项目或笔记</label>
    <input id="site-search" type="search" placeholder="查找课程、项目或笔记" autocomplete="off">
    <p class="search-status minor" aria-live="polite"></p>
    <ul class="search-results"></ul>
  </dialog>
</body>
</html>
"""
    destination = ROOT / path
    destination.parent.mkdir(exist_ok=True, parents=True)
    destination.write_text(html, encoding="utf-8")


def course_url(slug):
    return f"courses/{slug}.html"


def course_link(slug):
    return f'<a href="{course_url(slug)}">{COURSES[slug][0]}</a>'


def course_text(slug, field, default):
    return CONTENT["courses"].get(slug, {}).get(field) or default


def additions(category):
    entries = [entry for entry in CONTENT["entries"] if entry["category"] == category]
    if not entries:
        return ""
    items = "".join(
        f'<article><h3>{escape(entry["title"])}</h3>'
        + "".join(f'<p>{escape(paragraph.strip())}</p>' for paragraph in entry["body"].splitlines() if paragraph.strip())
        + '</article>'
        for entry in entries
    )
    return section("补充记录", f'<div class="prose">{items}</div>', "more")


def build_home():
    cover = f"""
    <section class="home-cover" id="about" aria-labelledby="home-title">
      <div class="cover-intro">
        <div class="cover-avatar" aria-hidden="true">X</div>
        <h1 id="home-title">{escape(CONTENT["cover_title"])}</h1>
        <div class="cover-signature">
          <p>{escape(CONTENT["signature"])}</p>
          <div class="cover-links"><a href="courses.html">课程档案</a><a href="plan.html">课程规划</a><a href="{GITHUB}">GitHub</a></div>
        </div>
      </div>
      <a class="cover-down" href="#courses" aria-label="向下浏览课程与作品"><span aria-hidden="true"></span></a>
      <div class="cover-wave" aria-hidden="true"></div>
    </section>"""
    showcases = [
        ("课程档案", "14 门计算机课程", "courses.html", "course"),
        ("课程规划", "基础 · 系统 · 应用 · 实验", "plan.html", "plan"),
        ("项目", "StudyFlow 与数据分析", "projects.html", "project"),
    ]
    display = "".join(
        f'<a class="showcase-card art-{art}" href="{url}"><div><strong>{title}</strong><span>{subtitle}</span></div></a>'
        for title, subtitle, url, art in showcases
    )
    work = [
        ("MNIST 手写数字识别", "深度学习 · Python", "对照 MLP、CNN 与自定义网络。自定义 CNN 的测试准确率为 98.50%。", "courses/deep-learning.html#work", "mnist"),
        ("用 Room 查询本地新闻", "移动应用开发 · Java", "标题搜索、发布时间排序，以及列表到详情的衔接。", "courses/android.html#work", "android"),
        ("CPCS2018 数据审计", "数据科学 · Python", "从信号文件与标签的对齐出发，检查异常和重复记录。", "courses/data-science.html#work", "data"),
        ("Transformer 及其变体", "论文笔记", "从长序列注意力读到 FlashAttention 与 GQA，整理三种常见的计算瓶颈。", "notes.html", "notes"),
    ]
    articles = "".join(
        f'<article class="iro-post"><a class="post-art art-{art}" href="{url}" aria-label="{title}">'
        + ('<img src="assets/mnist-samples.png" width="542" height="102" alt="">' if art == "mnist" else "")
        + f'</a><div class="post-copy"><p class="post-meta">{kind}</p><h3><a href="{url}">{title}</a></h3>'
        + f'<p class="minor">{summary}</p><a class="post-more" href="{url}" aria-label="阅读{title}">阅读全文 →</a></div></article>'
        for title, kind, summary, url, art in work
    )
    catalog = section("学习导航", f'<div class="showcase">{display}</div>', "courses")
    related = section("学习记录", f'<div class="post-list">{articles}</div>', "posts")
    plan = section("学习路线", '<div class="plan-link"><p>从 C 语言和线性代数起步，经过系统与应用课，再用模型实验和论文阅读串联。</p><a href="plan.html">查看课程规划 →</a></div>', "plan")
    write("index.html", "学习作品集", "X-ING 的课程成果、项目、论文笔记与课程规划。", "", catalog + related + plan, cover)


def build_catalog():
    blocks = []
    for key, (name, rows) in GROUPS.items():
        tiles = ''.join(
            f'<div class="col"><article class="course-row"><h3><a href="{course_url(slug)}">{title} →</a></h3><p>{escape(course_text(slug, "intro", intro))}</p></article></div>'
            for slug, title, _, intro, _ in rows
        )
        blocks.append(section(name, f'<div class="row row-cols-1 row-cols-md-2 g-3">{tiles}</div>', key))
    directory = '<div id="regular" class="pb-4 d-flex flex-wrap gap-3">' + ''.join(
        f'<a href="#{key}">{name}</a>' for key, (name, _) in GROUPS.items()
    ) + '</div>'
    extra = section("课外拓展", cards((
        card("南京大学 · 操作系统原理", "蒋炎岩 · 进程、并发与文件系统。", NJU),
        card("CMU 15-445/645 · 数据库系统", "存储、索引、查询执行和事务恢复。", CMU),
    )), "extra")
    write("courses.html", "课程档案", "14 门课程的独立页面，包含学习要点、可浏览成果和对应的课程仓库。",
          "courses.html", directory + ''.join(blocks) + extra,
          page_intro("课程档案", "查看 14 门课程。实验代码和摘要可以直接阅读，完整资料由 GitHub 管理。"))


def build_courses():
    exhibit = {
        "os": '<div class="prose"><p>课外学习按进程与地址空间、并发、持久化三个主题展开。先追踪系统调用如何改变程序能观察到的状态，再把这个视角用到同步与文件读写上。</p><a href="' + NJU + '">南京大学《操作系统原理》讲义与实验 ↗</a></div>',
        "databases": '<div class="prose"><p>课外用 CMU 的课程补上数据库执行层。从记录的存储形式追到索引访问，再比较不同查询计划需要读多少数据。</p><a href="' + CMU + '">CMU 15-445/645 课程资料 ↗</a></div>',
        "android": code_box("android", "移动开发课程包含 Activity 间传参和广播实验。本地 Room 新闻练习另外展示标题查找、按发布时间排序以及列表与详情的衔接。"),
        "data-science": code_box("data-science", "CPCS2018 信号数据分析先按样本标识核对文件与标签，再检查波形长度、缺失、异常和重复记录。下面把数据审计中的对齐检查整理成一段可读示例。"),
        "deep-learning": """
        <figure class="prose mnist-figure"><img src="../assets/mnist-samples.png" width="542" height="102" alt="MNIST 样本中手写的 7、2、1、0、4">
        <figcaption><a href="https://keras.io/api/datasets/mnist/">MNIST，LeCun 与 Cortes</a> · 已着色 · <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a></figcaption></figure>"""
        + code_box("deep-learning", "本地 MNIST 实验中，单层卷积提取局部特征，2×2 池化把特征图从 28×28 缩成 14×14，分类层输出 10 个分数。") + """
        <div class="prose"><h3>一次对照实验的结果</h3>
        <p>三个模型使用同一训练、验证和测试划分。下面是本地实验记录中的第 5 轮结果。</p>
        <div class="table-responsive"><table class="table table-sm align-middle">
          <thead><tr><th scope="col">模型</th><th scope="col">参数量</th><th scope="col">验证准确率</th><th scope="col">测试准确率</th></tr></thead>
          <tbody>
            <tr><th scope="row">MLP</th><td>101,770</td><td>96.50%</td><td>97.05%</td></tr>
            <tr><th scope="row">CNN</th><td>15,770</td><td>97.02%</td><td>97.52%</td></tr>
            <tr><th scope="row">自定义 CNN</th><td>105,866</td><td>98.53%</td><td>98.50%</td></tr>
          </tbody>
        </table></div></div>""",
    }
    for slug, (title, directory, intro, task) in COURSES.items():
        intro = course_text(slug, "intro", intro)
        task = course_text(slug, "task", task)
        masthead = page_intro(title, escape(intro), ("课程档案", "../courses.html"))
        overview = ""
        work = exhibit.get(slug)
        if work:
            overview += section("成果与笔记", work, "work")
        else:
            overview += section("学习记录", '<p class="prose">' + STATUS.get(slug, "仓库已建课程目录。这里先列出学习主题和自测任务，公开成果待整理。") + '</p>')
        note = course_text(slug, "note", "")
        if note:
            overview += section("补充笔记", '<div class="prose">' + "".join(f'<p>{escape(line.strip())}</p>' for line in note.splitlines() if line.strip()) + '</div>')
        overview += section("自测任务", f'<p class="prose">{escape(task)}</p>')
        source = f'<p><a href="{GITHUB}/tree/main/{quote(directory)}">查看 GitHub 对应目录 ↗</a></p><p class="minor mb-0">完整资料按私有仓库的访问权限提供。</p>'
        overview += section("课程资料", source)
        write(course_url(slug), title, intro, "courses.html", overview, masthead)


def build_plan():
    stage_items = ''.join(
        '<li><h3 class="h5">' + title + '</h3><div class="d-flex gap-2 flex-wrap">' +
        ' <span aria-hidden="true">·</span> '.join(course_link(s) for s in keys) + f'</div><p>{escape(CONTENT["plan"].get(title, desc))}</p></li>'
        for title, keys, desc in PLAN
    )
    masthead = page_intro("课程规划", "按现有课程目录整理的学习路线。每个阶段都配一个可以检查的成果。")
    body = section("学习顺序", f'<ol class="plan-list prose">{stage_items}</ol>')
    body += section("并行复习", '<p class="prose">大学物理、数字电子与高级英语可以随课堂进度安排。等程序设计与系统课打好基础后，再系统学习南大操作系统与 CMU 数据库公开课。</p><a href="courses.html#extra">查看公开课 →</a>')
    write("plan.html", "课程规划", "X-ING 的分阶段课程学习路线与阶段成果。", "plan.html", body, masthead)


def build_projects():
    masthead = page_intro("项目", "记录现有原型、实现片段和可复核的实验过程。")
    body = section("学程 StudyFlow", """
      <div class="prose"><p class="eyebrow">Android · 阶段一原型</p>
      <p>用 Kotlin、Jetpack Compose 和 StateFlow 做学习管理原型。作业、练习、考试和设置四个页面使用本地样例数据。</p>
      <p>下一步把内存中的作业状态迁移到 Room，并补上编辑、删除和错题记录。</p></div>
    """ + code_box("studyflow", "作业筛选支持按标题或课程名搜索。排序把已完成作业放在后面，再按截止时间排列。"), "studyflow")
    body += section("CPCS2018 数据分析", """
      <div class="prose"><p class="eyebrow">数据科学 · 课程项目</p>
      <p>将信号读取、标签对齐、数据质检与模型对照串成一条流程。重点是让数据划分和结果能被人复核。</p>
      <a href="courses/data-science.html#work">查看数据审计与代码 →</a></div>
    """, "data-project")
    write("projects.html", "项目", "StudyFlow 学习管理原型和 CPCS2018 数据分析。", "projects.html", body + additions("项目"), masthead)


def build_notes():
    masthead = page_intro("论文笔记", "把读过的内容按研究问题、方法和适用条件整理。这组笔记来自《Transformer 及其变体》课程报告。")
    body = section("Transformer 的结构与长序列", """
      <div class="prose">
      <p><strong>问题。</strong>自注意力让不同位置直接交互，也让训练更容易并行；标准全局注意力的交互量随序列长度平方增长。</p>
      <p><strong>读到的区别。</strong>Transformer‑XL 在片段间保留历史状态。Longformer 限制大多数位置只看附近窗口，并保留少量全局位置。这两种方案分别改变可用的历史和允许发生的交互。</p>
      <p><strong>复核点。</strong>比较不同方案时，记录有效上下文、任务质量和实测运行时间。</p>
      <ul class="link-rows">
        <li><a href="https://arxiv.org/abs/1706.03762">Attention Is All You Need ↗</a></li>
        <li><a href="https://aclanthology.org/P19-1285/">Transformer-XL ↗</a></li>
        <li><a href="https://arxiv.org/abs/2004.05150">Longformer ↗</a></li>
      </ul></div>
    """, "transformer")
    body += section("FlashAttention 与 GQA 解决什么", """
      <div class="prose">
      <p><strong>FlashAttention。</strong>用分块和在线 Softmax 减少中间矩阵的显存往返。密集注意力依然会计算所有位置对。</p>
      <p><strong>GQA。</strong>一组查询头共享键值头，减少自回归解码需要保存和读取的 KV 缓存。端到端收益还受批量、序列长度和硬件制约。</p>
      <p><strong>复核点。</strong>分别记录提示处理和逐词解码的延迟、吞吐量与显存峰值，再对照任务质量。</p>
      <ul class="link-rows">
        <li><a href="https://arxiv.org/abs/2205.14135">FlashAttention ↗</a></li>
        <li><a href="https://arxiv.org/abs/2305.13245">GQA ↗</a></li>
      </ul></div>
    """, "efficient-attention")
    write("notes.html", "论文笔记", "Transformer、长序列注意力、FlashAttention 与 GQA 的阅读记录。", "notes.html", body + additions("论文笔记"), masthead)


def build_search():
    records = [(name, course_text(slug, "intro", intro), course_url(slug)) for slug, (name, _, intro, _) in COURSES.items()]
    records.extend([
        ("课程档案", "计算机课程与课外拓展", "courses.html"),
        ("课程规划", "基础、系统、应用与实验", "plan.html"),
        ("学程 StudyFlow", "Android 学习管理原型", "projects.html#studyflow"),
        ("CPCS2018 数据分析", "数据审计、建模与复核", "projects.html#data-project"),
        ("MNIST 手写数字识别", "PyTorch · MLP 与 CNN 模型对照", "courses/deep-learning.html#work"),
        ("Transformer 与长序列", "论文笔记", "notes.html#transformer"),
        ("FlashAttention 与 GQA", "显存访问、推理与 KV 缓存", "notes.html#efficient-attention"),
    ])
    for entry in CONTENT["entries"]:
        href = "projects.html#more" if entry["category"] == "项目" else "notes.html#more"
        records.append((entry["title"], entry["category"], href))
    (ROOT / "assets/search-index.js").write_text("window.xingSearchIndex = " + dumps(records, ensure_ascii=False) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    build_home()
    build_catalog()
    build_courses()
    build_plan()
    build_projects()
    build_notes()
    build_search()
