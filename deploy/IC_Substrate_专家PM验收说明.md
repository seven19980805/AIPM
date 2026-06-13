# IC Substrate 专家 AI PM 验收说明

这份清单用于判断当前系统是否达到可交付试用状态，重点覆盖 IC Substrate 场景下的 Production、Quality、TDI 专家链路，以及最终 PRD/下载输出。

## 1. 必跑验收命令

在项目根目录执行：

```bash
python3 scripts/verify-ic-substrate-expert-contracts.py
```

覆盖静态合同：

- 前端只暴露 `Production / Quality / TDI` 三个 IC Substrate 入口，其他部门归入 General。
- API、前端、后端均传递 `starter_department`。
- 四语言输出锁定 `en / de / zh / ms`。
- 内部模型 JSON 修复、A/B/C fallback、专家 prompt、PRD 证据附录、coding handoff 证据包没有被删。

在安装后端依赖后执行：

```bash
python3 scripts/verify-ic-substrate-runtime-contracts.py
```

覆盖运行时合同：

- `Production / Quality / TDI` 开局后，结构化模型会保留对应部门。
- 下一问 prompt 会优先出现该部门的专家证据缺口。
- 内部模型缺少 `requesting_department` 时，不会把专家轨道冲掉。
- `/api/sessions` 和 `/api/sessions/<id>/messages` 首轮 API 链路保持专家轨道。
- PRD 生成会保留 Markdown，同时追加 IC Substrate 专家证据附录。
- PRD 下载支持 `?format=docx`，返回 Word MIME 和 `.docx` 文件名。

## 2. 人工冒烟路径

本地或内网部署后，在浏览器打开前端：

1. 点击 `New Chat`。
2. 选择 `IC Substrate professional chain`。
3. 分别从 `Production`、`Quality`、`TDI` 开局创建会话。
4. 输入一句很短的需求，例如：
   - Production：`我想做一个排产和WIP看板`
   - Quality：`我想做一个缺陷看板`
   - TDI：`我想做一个TDI工单跟踪系统`
5. 检查 AI PM 第一轮追问是否围绕该部门专业口径，而不是泛泛问“目标用户是谁”。
6. 检查右侧结构化需求模型和进度卡是否稳定，不应大幅跳动或丢失部门。
7. 信息足够后生成 PRD，确认文档末尾包含 `IC Substrate 专家证据附录`。
8. 下载文档时验证 Markdown 可用于 coding handoff，`?format=docx` 可得到 Word 文件。

## 3. 内网部署后最小检查

进入部署目录后：

```bash
podman ps
podman logs aipm_api --tail 100
podman logs aipm_web --tail 100
curl -s http://127.0.0.1:3102/api/templates >/tmp/aipm_templates.json
```

浏览器访问前端端口后，至少完成一次 `Quality -> 缺陷看板 -> 生成 PRD -> 下载 docx` 的闭环。

## 4. 判定标准

可试用状态至少满足：

- 三个 IC Substrate 入口都能进入对应专家轨道。
- AI PM 追问能落到业务动作、对象粒度、状态/公式/数据源、验收证据，而不是只问通用产品问题。
- Mimo/OpenAI-compatible 内部模型即使输出 JSON 不稳定，也不会丢专家部门。
- 最终 PRD 能明确区分已确认事实、待确认项、专家证据附录。
- Markdown 继续服务 coding handoff，docx 继续服务业务评审下载。
