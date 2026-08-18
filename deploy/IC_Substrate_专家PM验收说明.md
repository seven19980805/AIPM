# IC Substrate 专家 AI PM 验收说明

这份清单用于判断当前系统是否达到可交付试用状态，重点覆盖 IC Substrate 场景下的 Production、Quality、TDI 专家链路，以及最终 PRD/下载输出。

## 1. 必跑验收命令

在项目根目录执行后端单元测试：

```bash
python3 -m unittest discover -s tests
```

并运行 PM 方法论契约脚本：

```bash
python3 scripts/verify-pm-methodology-contracts.py
```

覆盖范围：

- “新建对话”的 IC Substrate 专家入口只暴露 `Production / Quality / TDI` 三条业务路线。
- 模板库同时暴露全部 14 个启用的业务模板；非 IC Substrate 模板可直接启动模板采访，不强制映射到上述三条路线。
- API、前端、后端均传递 `starter_department`。
- 四语言输出锁定 `en / de / zh / ms`。
- 部门识别由 `data/ic_substrate/domain_pack.json` 驱动，而不是硬编码关键词。
- LLM 调用失败时主对话和 PRD 接口直接返回错误，不再回退到本地伪造内容。
- PRD 生成会保留 Markdown，同时追加 PRD V0 handoff 脚手架。
- PRD 下载支持 `?format=docx`，返回 Word MIME 和 `.docx` 文件名。

> 注：早期 `verify-ic-substrate-*-contracts.py` 与 `verify-fast-prd-v0-browser.mjs` 校验的是已退役的本地演示链路与硬编码匹配器；上线改造时一并移除。

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
9. 打开模板库，确认显示 14 个模板；从财务管理等非 IC Substrate 模板启动采访时，不应出现业务路线校验错误。

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
- 14 个启用模板均可启动采访；普通业务模板不会错误显示 Production / Quality / TDI 作为模板场景选项。
- AI PM 追问能落到业务动作、对象粒度、状态/公式/数据源、验收证据，而不是只问通用产品问题。
- Mimo/OpenAI-compatible 内部模型即使输出 JSON 不稳定，也不会丢专家部门。
- 最终 PRD 能明确区分已确认事实、待确认项、专家证据附录。
- Markdown 继续服务 coding handoff，docx 继续服务业务评审下载。
