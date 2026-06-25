# QDM Finished Lot 良率看板需求模板

> 本模板从 `D.CHQ.QDM Yield Dashboard Requirement .docx` 解析并适配而来。  
> 原文里的图片已替换成文字说明，便于作为业务模板用于需求访谈、PRD 生成和结构化需求沉淀。

## 1. 基础文档信息

| 字段 | 内容 |
| --- | --- |
| 模板名称 | QDM Finished Lot 良率看板需求模板 |
| 文档名称 | D.CHQ.QDM Finish Yield Dashboard Requirement |
| 系统 / 模块 | FinishedLot |
| 发起部门 | QDM |
| 作者 / 提出人 | Ely Yi |
| 版本 | V1.0 |
| 创建日期 | 2026-05-21 |
| 业务领域 | Manufacturing quality / finished lot yield / QDM dashboard |
| 状态 | 草稿 / 评审中 / 已确认 / 开发中 / 已上线 |
| 目标版本 / 交付日期 | [YYYY-MM-DD] |

## 2. 背景与目标

### 2.1 背景

该看板用于从高层视角查看工厂内不同产品当前关键良率指标。看板应由自动化脚本定时更新，默认按日刷新；若数据负责人确认其他刷新频率，则以数据契约为准。

看板需要支持：

- 总体良率趋势，并按 segment / product 下钻。
- 主 bin 层级趋势和累计 bin 趋势。
- 基于 loss code 和 loss operation 的 Pareto 分析。
- 按根因或责任部门进行 loss attribution。

### 2.2 目标

- 看到更陡峭的良率改善曲线。
- 快速降低生产成本。
- 在基本不增加额外成本的情况下提升生产产出。
- 更快回收投资成本。

### 2.3 成功标准

- 业务负责人和数据负责人确认指标定义、筛选项、源表、刷新频率和验收规则。
- 用户可在首屏识别最新 finished lot 良率、产出、损失和主要缺陷贡献项。
- 用户可从良率趋势下钻到缺陷代码 loss 和责任部门明细。
- 相同筛选条件下，看板展示数据与已批准的源查询结果一致。

## 3. 页面 / 功能呈现

### 3.1 Finished Lot Performance Overview Trend

| 项目 | 需求 |
| --- | --- |
| 页面名称 | Finished Lot Performance Overview Trend |
| 页面目的 | 按时间范围展示 finished yield，并展示最新周的 Output、Yield、NSQM Loss。 |
| 顶部区域 | 使用第 4 节定义的统一查询条件。 |
| Y 轴数据区域 | 主图默认按周展示 finished product yield rate。右侧默认展示最新周详细数据。用户可点击左侧数据点或柱体切换不同明细视图。 |
| X 轴区域 | 主图默认展示 week 信息；明细图展示当前选中数据说明。 |

原截图的文字化说明：

- 页面头部为 `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`。
- 右上角包含周选择器，例如 `W 202621`，以及导出 / 下载按钮。
- 主区域是一张大图，标题为 `Weekly Finished Lot Performance Overview Trend`。
- 图表横轴展示 `202612` 到 `202621` 等周别。
- 图表组合使用柱状图和折线图：柱体展示周度数值，折线展示 target / output / yield 等对比趋势。
- 当前选中的周需要视觉高亮；图表提示文案说明点击 weekly yield bar 可更新下方 defect analysis。
- 右侧 KPI 卡片展示选中周的明细，包括 Yield / Target、Finished Count、NSQM 或 NSOM Output、NSQM 或 NSOM Loss。
- 源图中的示例值包括 Yield / Target `96.83%`、Target `94.81%`、Finished Count `159 Lots`、Output `1,335.57`、Loss `63.55`。
- 需要确认最终指标标签到底使用 `NSQM` 还是 `NSOM`，因为源文档和截图中存在疑似不一致。

### 3.2 Loss Ratio By Defect Code

| 项目 | 需求 |
| --- | --- |
| 页面名称 | Loss Ratio By Defect Code |
| 页面目的 | 展示按 defect code 排名的 Top 10 到 Top 20 defect loss ratio，并展示 defect code 趋势。 |
| 顶部区域 | 使用第 4 节定义的统一查询条件。 |
| Y 轴数据区域 | 主图展示 Top 10 到 Top 20 defect loss ratio。右侧展示当前选中 defect code 的趋势和责任部门明细。 |
| X 轴区域 | 主图展示 defect code 信息；右侧饼图 / 环形图展示 department 信息。 |

原截图的文字化说明：

- 页面头部仍为 `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`。
- 上方横向周期选择条展示 `202612` 到 `202621` 等周别。
- 缺陷分析区域标题为 `Loss Ratio By Defect Code`。
- 页面提供 `Loss Ratio` 和 `Core Loss Ratio` 勾选开关。
- 主图为选定周期的横向排名柱状图，例如 `202621 Top 10 Loss Ratio By Defect Code`。
- 红色柱体表示 total loss ratio，蓝色柱体表示 core loss ratio。
- 源图可见的示例缺陷代码包括 `ED25 - Short in inner layer`、`ED21 - High resistance short`、`AP09 - Component tilting`、`BM31 - Base material dent`、`GE01 - Scratches`、`SM94 - Solder mask thickness`、`SM41 - Soldermask discoloration`、`ED55 - Short bridge die region`、`HO31 - Via not completely filled`。
- 用户选择某个 defect code 后，右侧明细卡片随之更新。
- 右侧趋势图示例为 `ED25 Weekly Overview Trend`，用于对比 core defect loss 和 defect loss ratio 随时间变化。
- 右侧环形图展示责任部门占比。源图示例包括 `Etching + AOI 59%`、`Assembly 23%`、`Final Check 11%`、`Material 7%`，中心值为 `26.26%`。

## 4. 查询条件与用户交互

### 4.1 筛选条件

原筛选区截图的文字化说明：

- 筛选区采用两行三列布局。
- 第一行包含 `Customer`、`Plant`、`Date Type`。
- 第二行包含 `Lot Type`、`Unit Type`、`Project Type`。
- 所有控件均为下拉选择框，并带有可见的下拉箭头。
- 源图默认值为 `Customer = All selected`、`Plant = All selected`、`Date Type = Weekly`、`Lot Type = HVM`、`Unit Type = NSQM`、`Project Type = Overall`。

| 筛选项 | 控件类型 | 默认值 | 作用范围 |
| --- | --- | --- | --- |
| Customer | Dropdown | All selected | 所有适用图表 |
| Plant | Dropdown | All selected | 所有适用图表 |
| Date Type | Dropdown | Weekly | 所有适用图表 |
| Lot Type | Dropdown | HVM | 所有适用图表 |
| Unit Type | Dropdown | NSQM | 所有适用图表 |
| Project Type | Dropdown | Overall | 所有适用图表 |

### 4.2 交互规则

- 筛选条件变化后，应在技术可行范围内更新所有受影响图表，无需整页刷新。
- 被选中的图表分组、柱体、趋势点或 segment 需要有明确选中态，并让当前生效筛选对用户可见。
- 桌面端 tooltip 需要清晰可读；触屏设备上应使用更适合点击 / 轻触的详情行为替代。
- 如果图例可交互，则图例必须支持键盘访问。
- 导出动作必须遵循数据权限规则，并尽量带上当前筛选上下文。

## 5. 数据说明与数据契约

### 5.1 数据来源

| Source ID | 表 / 视图 / API | 业务说明 | 数据粒度 | 刷新频率 | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryData_Internal]` | 计算 finished lot yield 的主数据源。 | Weekly / Quarterly / Monthly | Weekly 或待确认频率 | QDM |
| DS-02 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryDefectData_Internal]` | 支持 defect code 对比和明细图表的数据集。 | Weekly / Quarterly / Monthly | Weekly 或待确认频率 | QDM |

### 5.2 必要数据字段

| 字段名 | 来源 | 类型 | 必填 | 业务定义 / 逻辑 |
| --- | --- | --- | --- | --- |
| `ATSDate` | DS-01 | Date / period | 是 | 用于趋势、周期对比和日期筛选。 |
| `DateType` | DS-01 | Date / period | 是 | 定义看板使用 weekly、monthly 或 quarterly 粒度。 |
| `LotType` | DS-01 | String / code | 是 | 用户按 lot type 筛选或对比时使用。 |
| `Project Type` | DS-01 | String / code | 是 | 用户按 project type 筛选或对比时使用。 |
| `Yield` | DS-01 | Number / percent | 是 | 核心 finished yield 指标。 |
| `Output_NSQM` | DS-01 | Number | 是 | 核心 output 指标。 |
| `DefectCode` | DS-02 | String / code | 是 | 用于 defect code 排名和下钻。 |
| `DefectQty` | DS-02 | Number | 是 | 核心 defect quantity 或 loss value。 |
| `Department` | DS-02 | String / code | 是 | 用于按部门归因 loss。 |

### 5.3 待确认数据规则

- 确认看板刷新频率是 weekly、daily，还是两者都有。源文档背景提到 daily automation，但数据源表格写的是 weekly cadence。
- 确认最终周期粒度和 `DateType` 的可选值。
- 确认 `Customer`、`Plant`、`LotType`、`UnitType`、`ProjectType` 是直接来自 DS-01 / DS-02，还是需要关联维表。
- 确认 output 和 loss 指标使用 NSQM、lots、units，还是支持多单位模式。
- 定义空值处理、分母为 0 时的处理、四舍五入精度和百分比展示格式。
- 定义 customer、plant、product 和可导出明细数据的权限范围。

## 6. 良率计算逻辑

### 6.1 Finished Yield 定义

Finished Yield，也称 Product Yield，表示某个 lot 或某个 week 中成功通过完整制造流程并作为成品出货的单位占比。它反映生产线整体综合良率表现。

核心计算逻辑：基于各关键工序 Output/Input 比例的连乘，也就是各单站点工序良率的乘积。

### 6.2 原公式图片的文字版本

| 公式 | 文字版本 |
| --- | --- |
| Lot Product Yield | `Lot Product Yield = (PAOI Output / PAOI Input) x (E-test Output / E-test Input) x (CCAOI Output / CCAOI Input) x (Bump AOI Output / Bump AOI Input) x (FVI Output / FVI Input)` |
| Weekly Product Yield | `Weekly Product Yield = 各工序 weekly shipped output/input ratio 的乘积`，例如 `(Total Weekly Shipped PAOI Output / Total Weekly Shipped PAOI Input) x (Total Weekly Shipped E-test Output / Total Weekly Shipped E-test Input) x ...` |
| 扩展规则 | 如果已确认的工艺路径包含 `Inline`、`Others` 或其他检测站点，则需要把对应站点良率继续乘入公式。 |

### 6.3 计算步骤与示例

计算原则为：`Output / Input = Process Yield`，然后把各工序良率顺序连乘。

原计算示例图片的文字化表格如下：

| Process | Input | Output | Losses | Yield |
| --- | ---: | ---: | ---: | ---: |
| PAOI | 50000 | 49700 | 300 | 99.4% |
| E-test | 49700 | 49500 | 200 | 99.5% |
| CCAOI | 49250 | 48900 | 350 | 99.29% |
| Bump | 48600 | 48300 | 300 | 99.38% |
| FVI | 48300 | 47900 | 400 | 99.17% |
| Inline | 49500 | 49250 | 250 | 99.49% |
| Others | 48900 | 48600 | 300 | 99.39% |

源文档中的 GTY 示例表达式：

`GTY = 99.4% x 99.5% x 99.29% x 99.38% x 99.17% x 99.49% x 99.39%`

## 7. 页面 / 功能布局

页面应根据业务优先级、数据密度和屏幕尺寸选择合适布局。分析型页面推荐默认采用 Primary-Detail / Hero Layout；监控型看板可使用 Uniform Grid 作为备选。

| 布局选项 | 描述 | 适用场景 | 建议 |
| --- | --- | --- | --- |
| Primary-Detail / Hero | 一个大尺寸主图占据核心区域，KPI 卡片和辅助图表位于侧边或下方。 | 有一个主导趋势或核心业务问题的分析页。 | 默认推荐，除非业务负责人确认其他方案。 |
| Nested / Drill-down | 选择一个图表后更新或筛选另一个图表。 | 探索式分析、类别下钻、缺陷归因。 | 仅在图表关系清晰时使用。 |
| Uniform Grid | 多个图表使用一致卡片尺寸，视觉优先级相近。 | 多指标监控型看板。 | 当没有单一主图时作为备选。 |

## 8. 图表清单与配置

开发前应明确每张图表的配置。

| Chart ID | 图表名称 | 类型 | 主指标 | 维度 / 分组 | 数据源 | 交互 |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Finished Overall Trend | 折线 + 柱状组合图 | Yield / target / output | Weekly / Quarterly / Monthly | DS-01 | Hover tooltip；点击周度柱体或点位筛选明细表和缺陷分析。 |
| CH-02 | Defect Loss Ratio | 堆叠或分组横向柱状图 | Defect loss ratio / core loss ratio | Top 10 到 Top 20 defect codes | DS-02 | 图例开关；点击 defect code 更新相关趋势和部门归因。 |
| CH-03 | 右侧明细图表 | 表格 / 折线 / 饼图或环图 | 基于左侧选中数据展示明细 | 当前周期、选中 defect、选中筛选条件 | DS-01 + DS-02 | 分页、排序、tooltip、选中态联动、导出。 |

## 9. 责任方与干系人

| 角色 | 姓名 / 团队 | 职责 | 是否必须签核 |
| --- | --- | --- | --- |
| Business Owner | Yield team | 确认业务目的、优先级和图表含义验收。 | 是 |
| Product Owner / BA | QDM | 维护需求、澄清范围问题、协调评审。 | 是 |
| Data Owner | Yield team | 确认源表、字段定义、刷新频率和数据质量规则。 | 是 |
| UI/UX Reviewer | Yield team | 检查 AITC 视觉一致性、布局行为和响应式体验。 | 建议 |
| Frontend Developer | QDM | 实现看板、图表组件、交互和响应式行为。 | 否 |
| QA Tester | Yield team | 执行功能、数据、兼容性、可访问性和回归测试。 | 是 |

## 10. UI 与视觉设计要求

实现应遵循 AITC 企业 UI 风格：干净、运营化、可信赖、信息密度高但易读，并以中性色表面和蓝色主操作色为基础。

| UI 区域 | 要求 |
| --- | --- |
| 色彩系统 | 使用背景 `#f6f8fb` / `#f3f5f7`，面板 `#ffffff`，主蓝 `#2563eb`，hover `#1d4ed8`，边框 `#d9e1e7`，文字 `#111315` / `#17202a`。不要把绿色或紫色作为主品牌色。 |
| 字体 | 优先使用 Arial Nova，其次 Plus Jakarta Sans、Arial 和中文 fallback 字体。避免过重字重和负字距。 |
| 间距与圆角 | 使用 8px 间距节奏，通用圆角 8px，密集控件圆角 6px。 |
| 卡片 / 面板 | 使用白色图表面板、清晰标题、一致 padding，仅在必要时使用轻微阴影。 |
| 响应式布局 | 桌面优先支持对比；平板保持图表可读；移动端纵向堆叠图表，仅真实表格允许横向滚动。 |
| 状态 | 定义 loading、empty、error、disabled、active、hover、focus、selected 等状态。 |

## 11. 技术规格

| 分类 | 要求 |
| --- | --- |
| 前端栈 | HTML + Bootstrap + JavaScript/jQuery。代码应清晰、结构化、必要处有注释，并便于二次开发。 |
| 图表库 | 使用已批准的轻量图表库或现有项目标准。除非架构评审批准，避免复杂插件。 |
| 响应式 | 支持桌面、平板和移动端断点。使用原生响应式网格，避免固定宽度导致溢出。 |
| 性能 | 页面 shell 应快速渲染；图表尽量异步加载。普通数据量下图表刷新目标为 3 秒内，具体受 API 性能约束。 |
| 浏览器支持 | 支持企业已批准的当前 Chrome 和 Edge 版本。其他浏览器要求待确认。 |
| 可维护性 | 分离数据映射、图表配置和渲染逻辑，使后续图表尽量可通过配置扩展。 |
| 安全 | 遵守基于角色的数据访问规则。防止未授权导出受限数据，避免在客户端暴露敏感原始字段。 |

## 12. 非功能需求

| 需求类型 | 目标 / 规则 | 验证方式 |
| --- | --- | --- |
| 数据准确性 | 相同筛选条件下展示值必须与已批准源查询结果一致。 | QA 抽样比对源查询或已验证报表。 |
| 性能 | 普通筛选或图表刷新应满足约定 SLA，标准数据量下目标 3 秒。 | 浏览器计时和 API 日志审查。 |
| 可访问性 | 控件可键盘访问、焦点状态可见、对比度足够、状态不只依赖颜色表达。 | 手动键盘测试和对比度检查。 |
| 可靠性 | 单个图表失败不应导致整页不可用，应展示图表级错误状态。 | 模拟 API 失败测试。 |
| 兼容性 | 在已批准桌面、平板和移动宽度下布局保持可读。 | 响应式浏览器验证。 |
| 可审计性 | 最近刷新时间和已应用筛选上下文应可见，或在导出元数据中可追踪。 | 功能测试和导出内容检查。 |

## 13. 验收标准

1. Business owner 确认图表清单、指标定义、筛选列表、默认视图和布局模式。
2. Data owner 确认源表 / 视图 / API、字段映射、刷新频率、关联逻辑和计算规则。
3. 所有图表在默认筛选和至少三组代表性筛选组合下正确渲染。
4. Loading、empty、error、active、hover、focus、disabled 等状态实现完整且视觉一致。
5. 页面在桌面、平板和移动宽度下响应式正常，无文字裁切、控件重叠或图表标签不可读。
6. 导出行为符合已批准的数据权限规则，并在适用时包含筛选上下文。
7. QA 根据源查询或已批准参考报表验证数据准确性。
8. 最终页面遵循已批准色彩系统，不引入未批准主色或过重装饰风格。

## 14. 待确认问题与决策

| ID | 问题 / 决策 | Owner | 目标日期 | 状态 |
| --- | --- | --- | --- | --- |
| Q-01 | 默认布局采用 Primary-Detail / Hero、Uniform Grid、Tabbed，还是其他模式？ | Business Owner / Product Owner | 待确认 | Open |
| Q-02 | 最终源表 / 视图 / API 和关联键是什么？ | Data Owner | 待确认 | Open |
| Q-03 | 首发版本哪些图表必须交付，哪些可选？ | Business Owner | 待确认 | Open |
| Q-04 | 哪些角色可以导出图表图片或底层数据？ | Security / Business Owner | 待确认 | Open |
| Q-05 | 已批准的数据刷新频率和数据可用性 SLA 是什么？ | Data Owner | 待确认 | Open |
| Q-06 | Output / Loss KPI 卡片最终标签应使用 NSQM 还是 NSOM？ | Business Owner / Data Owner | 待确认 | Open |
| Q-07 | Product Yield 公式是否除 PAOI、E-test、CCAOI、Bump AOI、FVI 外，还需要包含 Inline 和 Others？ | Data Owner | 待确认 | Open |

## 15. 附录 A. 色彩系统

| Token | 值 / 规则 |
| --- | --- |
| Background | `#f6f8fb` / `#f3f5f7` |
| Panel | `#ffffff` |
| Hover Surface | `#eef2f4` |
| Soft Blue Panel | `#f0f6ff` |
| Primary Text | `#111315` |
| KMS Text | `#17202a` |
| Secondary Text | `#424a55` / `#647280` |
| Border | `#d9e1e7` / `rgba(17,19,21,0.17)` |
| Active Border | `rgba(17,19,21,0.28)` |
| Primary Blue | `#2563eb` |
| Primary Hover | `#1d4ed8` |
| Primary Soft Background | `#e8f1ff` |
| Accent Blue | `#60a5fa` |
| Accent Soft Background | `rgba(96,165,250,0.17)` |
| Danger / Error / Warning | `#c2413b` / `#b43636` / `#a56313` |
| Shadow | `0 14px 34px rgba(38, 55, 70, 0.1)`，仅使用轻量阴影 |
