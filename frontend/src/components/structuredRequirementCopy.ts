import type { LanguageCode } from '../types/session'

export const structuredRequirementPanelCopy = {
  en: {
    requirementTitle: 'Structured Requirement Model',
    progressTitle: 'Requirement Progress',
    methodologyTitle: 'PM Methodology',
    icEvidenceTitle: 'IC Substrate Evidence',
    loading: 'Updating the current structured requirement model...',
    syncing: 'Syncing...',
    generateDocuments: 'Generate Documents',
    generatingDocuments: 'Generating documents...',
    prdV0Ready: 'Documents ready',
    prdV0ReadyHelp: 'Enough requirement information has been collected. Generate documents first; Go Coding sends the finished handoff to Vibe Coding.',
    fastPath: {
      title: 'Readiness path',
      help: 'Send a seed, answer focused expert questions, then generate documents before the Vibe Coding handoff.',
      done: 'Done',
      current: 'Now',
      pending: 'Next',
      questionBudgetLabel: 'Question budget',
      questionBudgetHelp: 'One focused question at a time.',
      exitRuleTitle: 'Exit rule',
      exitRuleHelp: 'Stop asking new questions once the core requirement is ready; otherwise ask only the highest-value missing point.',
      v0StatusTitle: 'Readiness status',
      v0StatusKnown: 'Known',
      v0StatusAssumed: 'Assumed',
      v0StatusMissing: 'Missing',
      v0StatusConflict: 'Conflict',
      handoffPacketTitle: 'Handoff packet',
      handoffPacketItems: [
        'Requirement document for IT review',
        'ASSUMPTIONS.md for open gaps',
        'mock-data.json before UI work',
        'IT Review Decision Sheet',
        'Vibe Coding Start Here',
        'No production writeback',
      ],
      firstBuildSlice: {
        title: 'First build slice',
        firstPageLabel: 'First page',
        firstApiLabel: 'First API',
        mockDataLabel: 'Mock data',
        smokeTestLabel: 'Smoke test',
        guardrailLabel: 'Guardrail',
        defaultPage: 'First requirement page',
        defaultApi: 'GET mock data API',
        defaultMockData: 'Mock record',
        defaultSmokeTest: 'Open the first page with mock data and verify the main action.',
        guardrail: 'No writeback or workflow automation',
      },
      acceptanceEvidence: {
        title: 'Acceptance evidence',
        proofTargetLabel: 'Proof target',
        artifactsLabel: 'Evidence artifacts',
        sourceLabel: 'Source to confirm',
        ownerLabel: 'Owner to confirm',
        blockedActionLabel: 'Blocked action check',
        defaultArtifacts: 'screenshot / mock_data_export / smoke_test_result',
        defaultSource: 'source of truth',
        defaultOwner: 'business owner',
        blockedActionCheck: 'Verify writeback and workflow automation remain disabled.',
      },
      criticalDecisions: {
        title: 'Critical decisions',
        status: 'Pending confirmation',
        businessActionLabel: 'Business action',
        ownerLabel: 'Primary user / owner',
        sourceLabel: 'Source of truth',
        writebackLabel: 'Writeback boundary',
        acceptanceLabel: 'Acceptance evidence',
        defaultBusinessAction: 'latest user seed',
        defaultOwner: 'business owner',
        defaultSource: 'source of truth',
        defaultWriteback: 'read-only or mock-only',
        defaultAcceptance: 'Smoke test evidence',
      },
      reviewDecision: {
        title: 'IT Review Decision',
        recommendedLabel: 'Recommended',
        recommendedDecision: 'Conditional approval',
        allowedScopeLabel: 'Allowed start scope',
        allowedScope: 'UI/API shell and mock data only',
        approve: 'Approve handoff',
        conditional: 'Conditional approval',
        blocked: 'Blocked',
        guardrail: 'No production writeback',
      },
      steps: {
        seed: {
          label: 'One sentence',
          help: 'Idea, pain point, or first action.',
        },
        prdV0: {
          label: 'Complete readiness',
          help: 'Close the remaining critical requirement gap.',
        },
        handoff: {
          label: 'Go Coding',
          help: 'Vibe Coding receives the generated documents and handoff checklist; status does not return automatically.',
        },
      },
    },
    goCoding: 'Go Coding',
    openingGoCoding: 'Opening Coding Workspace...',
    notCaptured: 'TBD',
    status: {
      missing: 'Missing',
      captured: 'Captured',
      pendingConfirmation: 'Pending',
      confirmed: 'Confirmed',
      conflict: 'Conflict',
    },
    rows: {
      objective: 'Business Goal',
      scope: 'Scope',
      users: 'Target Users',
      scenarios: 'Core Scenarios',
      features: 'Functional Requirements',
      pages: 'Pages',
      rules: 'Business Rules',
      integrations: 'Integration Systems',
      acceptance: 'Acceptance Criteria',
      ownership: 'Business / Acceptance Owners',
    },
    scopeLabels: {
      in: 'In',
      out: 'Out',
    },
    progressLabels: {
      readiness: 'Final readiness',
      finalReadiness: 'Final readiness',
      prdV0ReadinessTitle: 'Go Coding readiness',
      prdV0Deliverable: 'IT-reviewable requirement',
      factBaseline: 'Fact baseline',
      itReviewPacket: 'IT review packet',
      assumptionsExplicit: 'Assumptions explicit',
      vibeCodingHandoff: 'Vibe Coding handoff',
      handoffAfterPrd: 'Generated before handoff',
      finalPrdConfirmations: 'Final PRD confirmations',
      prdV0Handoff: 'Go Coding handoff',
      readyForItReview: 'Ready for IT review',
      coverage: 'Collection Coverage',
      confirmationRate: 'Confirmation Progress',
      pendingConfirmation: 'Pending',
      blockingQuestions: 'Blocking questions',
      conflict: 'Conflict',
    },
    methodologyLabels: {
      score: 'Method Evidence',
      ready: 'Ready',
      missing: 'Gaps',
      nextQuestion: 'Next PM question',
    },
    icEvidenceLabels: {
      score: 'Domain Evidence',
      ready: 'Ready',
      context: 'Department',
      shape: 'Shape',
      objects: 'Objects',
      grain: 'Grain',
      source: 'Source',
      nextQuestion: 'Next IC question',
    },
    methodologyStatus: {
      ready: 'Ready',
      partial: 'Partial',
      missing: 'Missing',
      conflict: 'Conflict',
    },
    cardLabels: {
      reason: 'Current judgement',
      pendingQuestion: 'Next thing to confirm',
    },
  },
  de: {
    requirementTitle: 'Strukturiertes Anforderungsmodell',
    progressTitle: 'Anforderungsfortschritt',
    methodologyTitle: 'PM Methodik',
    icEvidenceTitle: 'IC Substrate Evidence',
    loading: 'Das strukturierte Anforderungsmodell wird aktualisiert...',
    syncing: 'Synchronisiert...',
    generateDocuments: 'Dokumente erzeugen',
    generatingDocuments: 'Dokumente werden erzeugt...',
    prdV0Ready: 'Go Coding bereit',
    prdV0ReadyHelp: 'Die Anforderung ist vollstaendig genug. Zuerst Dokumente erzeugen; Go Coding uebergibt das fertige Paket an Vibe Coding.',
    fastPath: {
      title: 'Readiness-Pfad',
      help: 'Seed senden, fokussierte Expertenfragen beantworten, dann Dokumente vor der Vibe-Coding-Uebergabe erzeugen.',
      done: 'Fertig',
      current: 'Jetzt',
      pending: 'Naechst',
      questionBudgetLabel: 'Fragenbudget',
      questionBudgetHelp: 'Je Runde eine fokussierte Frage.',
      exitRuleTitle: 'Exit-Regel',
      exitRuleHelp: 'Keine neuen Fragen stellen, sobald die Kernanforderung ready ist; sonst nur die wichtigste Luecke fragen.',
      v0StatusTitle: 'Readiness-Status',
      v0StatusKnown: 'Bekannt',
      v0StatusAssumed: 'Annahme',
      v0StatusMissing: 'Luecke',
      v0StatusConflict: 'Konflikt',
      handoffPacketTitle: 'Handoff-Paket',
      handoffPacketItems: [
        'Requirement-Dokument fuer IT Review',
        'ASSUMPTIONS.md fuer offene Punkte',
        'mock-data.json vor UI-Arbeit',
        'IT Review Decision Sheet',
        'Vibe Coding Start Here',
        'Kein Production Writeback',
      ],
      firstBuildSlice: {
        title: 'First Build Slice',
        firstPageLabel: 'Erste Seite',
        firstApiLabel: 'Erste API',
        mockDataLabel: 'Mock-Daten',
        smokeTestLabel: 'Smoke Test',
        guardrailLabel: 'Guardrail',
        defaultPage: 'Erste Requirement-Seite',
        defaultApi: 'GET Mock-Daten API',
        defaultMockData: 'Mock Record',
        defaultSmokeTest: 'Erste Seite mit Mock-Daten oeffnen und Hauptaktion pruefen.',
        guardrail: 'Kein Writeback oder Workflow-Automation',
      },
      acceptanceEvidence: {
        title: 'Acceptance Evidence',
        proofTargetLabel: 'Proof Target',
        artifactsLabel: 'Evidence-Artefakte',
        sourceLabel: 'Zu bestaetigende Quelle',
        ownerLabel: 'Zu bestaetigender Owner',
        blockedActionLabel: 'Blocked Action Check',
        defaultArtifacts: 'Screenshot / Mock-Daten-Export / Smoke-Test-Resultat',
        defaultSource: 'Source of Truth',
        defaultOwner: 'Business Owner',
        blockedActionCheck: 'Pruefen, dass Writeback und Workflow-Automation deaktiviert bleiben.',
      },
      criticalDecisions: {
        title: 'Critical Decisions',
        status: 'Pending confirmation',
        businessActionLabel: 'Business Action',
        ownerLabel: 'Primary User / Owner',
        sourceLabel: 'Source of Truth',
        writebackLabel: 'Writeback-Grenze',
        acceptanceLabel: 'Acceptance Evidence',
        defaultBusinessAction: 'letzter User Seed',
        defaultOwner: 'Business Owner',
        defaultSource: 'Source of Truth',
        defaultWriteback: 'read-only oder mock-only',
        defaultAcceptance: 'Smoke-Test Evidence',
      },
      reviewDecision: {
        title: 'IT Review Decision',
        recommendedLabel: 'Empfohlen',
        recommendedDecision: 'Bedingte Freigabe',
        allowedScopeLabel: 'Erlaubter Startumfang',
        allowedScope: 'Nur UI/API-Shell und Mock-Daten',
        approve: 'Handoff freigeben',
        conditional: 'Bedingte Freigabe',
        blocked: 'Blockiert',
        guardrail: 'Kein Production Writeback',
      },
      steps: {
        seed: {
          label: 'Ein Satz',
          help: 'Idee, Pain Point oder erste Aktion.',
        },
        prdV0: {
          label: 'Readiness vervollstaendigen',
          help: 'Die wichtigste verbleibende Anforderungsluecke schliessen.',
        },
        handoff: {
          label: 'Go Coding',
          help: 'Vibe Coding liest die generierten Dokumente und die Handoff-Checkliste; Status kommt nicht automatisch zurueck.',
        },
      },
    },
    goCoding: 'Go Coding',
    openingGoCoding: 'Coding-Workspace wird geoeffnet...',
    notCaptured: 'TBD',
    status: {
      missing: 'Fehlt',
      captured: 'Erfasst',
      pendingConfirmation: 'Offen',
      confirmed: 'Bestaetigt',
      conflict: 'Konflikt',
    },
    rows: {
      objective: 'Geschaeftsziel',
      scope: 'Umfang',
      users: 'Zielbenutzer',
      scenarios: 'Kernszenarien',
      features: 'Funktionale Anforderungen',
      pages: 'Seiten',
      rules: 'Geschaeftsregeln',
      integrations: 'Integrationssysteme',
      acceptance: 'Abnahmekriterien',
      ownership: 'Business- / Abnahmeverantwortung',
    },
    scopeLabels: {
      in: 'Im Umfang',
      out: 'Nicht im Umfang',
    },
    progressLabels: {
      readiness: 'Final readiness',
      finalReadiness: 'Final readiness',
      prdV0ReadinessTitle: 'Go Coding readiness',
      prdV0Deliverable: 'IT-reviewable requirement',
      factBaseline: 'Fact baseline',
      itReviewPacket: 'IT review packet',
      assumptionsExplicit: 'Assumptions explicit',
      vibeCodingHandoff: 'Vibe Coding handoff',
      handoffAfterPrd: 'Vor Handoff erzeugt',
      finalPrdConfirmations: 'Final PRD confirmations',
      prdV0Handoff: 'Go Coding handoff',
      readyForItReview: 'Bereit fuer IT Review',
      coverage: 'Erfassungsgrad',
      confirmationRate: 'Bestaetigungsstand',
      pendingConfirmation: 'Offen',
      blockingQuestions: 'Blockierende Fragen',
      conflict: 'Konflikt',
    },
    methodologyLabels: {
      score: 'Methodik-Evidence',
      ready: 'Bereit',
      missing: 'Luecken',
      nextQuestion: 'Naechste PM-Frage',
    },
    icEvidenceLabels: {
      score: 'Domain-Evidence',
      ready: 'Bereit',
      context: 'Abteilung',
      shape: 'Form',
      objects: 'Objekte',
      grain: 'Granularitaet',
      source: 'Quelle',
      nextQuestion: 'Naechste IC-Frage',
    },
    methodologyStatus: {
      ready: 'Bereit',
      partial: 'Teilweise',
      missing: 'Fehlt',
      conflict: 'Konflikt',
    },
    cardLabels: {
      reason: 'Aktuelle Einschaetzung',
      pendingQuestion: 'Naechste Klaerung',
    },
  },
  zh: {
    requirementTitle: '\u7ed3\u6784\u5316\u9700\u6c42\u6a21\u578b',
    progressTitle: '\u9700\u6c42\u91c7\u96c6\u8fdb\u5ea6',
    methodologyTitle: 'PM \u65b9\u6cd5\u8bba',
    icEvidenceTitle: 'IC Substrate \u9886\u57df\u8bc1\u636e',
    loading: '\u6b63\u5728\u66f4\u65b0\u5f53\u524d\u7ed3\u6784\u5316\u9700\u6c42\u6a21\u578b...',
    syncing: '\u540c\u6b65\u4e2d...',
    generateDocuments: '\u751f\u6210\u6587\u6863',
    generatingDocuments: '\u6b63\u5728\u751f\u6210\u6587\u6863...',
    prdV0Ready: '文档可生成',
    prdV0ReadyHelp: '需求信息已足够；请先生成文档，文档 OK 后再交接到 Vibe Coding。',
    fastPath: {
      title: '信息充分度路径',
      help: '发送一句话种子，继续回答专家链路问题；信息足够后先生成文档，再交接到 Vibe Coding。',
      done: '完成',
      current: '当前',
      pending: '下一步',
      questionBudgetLabel: '问题预算',
      questionBudgetHelp: '每轮只问一个关键问题。',
      exitRuleTitle: '退出规则',
      exitRuleHelp: '核心需求足够后停止新增问题；未足够时只问最关键缺口。',
      v0StatusTitle: '信息状态',
      v0StatusKnown: '已知',
      v0StatusAssumed: '假设',
      v0StatusMissing: '缺口',
      v0StatusConflict: '冲突',
      handoffPacketTitle: '交接包',
      handoffPacketItems: [
        '需求文档给 IT 评审',
        'ASSUMPTIONS.md 记录待确认缺口',
        'mock-data.json 先支撑 UI',
        'IT 评审决策表',
        'Vibe Coding 起步说明',
        '禁止生产写回',
      ],
      firstBuildSlice: {
        title: '第一构建切片',
        firstPageLabel: '第一页',
        firstApiLabel: '首个 API',
        mockDataLabel: 'Mock 数据',
        smokeTestLabel: '冒烟测试',
        guardrailLabel: '护栏',
        defaultPage: '首版需求页面',
        defaultApi: 'GET Mock 数据 API',
        defaultMockData: 'Mock 记录',
        defaultSmokeTest: '用 Mock 数据打开第一页，并验证主动作。',
        guardrail: '禁止写回或流程自动化',
      },
      acceptanceEvidence: {
        title: '验收证据',
        proofTargetLabel: '证明目标',
        artifactsLabel: '证据材料',
        sourceLabel: '待确认数据源',
        ownerLabel: '待确认 Owner',
        blockedActionLabel: '阻塞动作检查',
        defaultArtifacts: '截图 / Mock 数据导出 / 冒烟测试结果',
        defaultSource: 'source of truth',
        defaultOwner: '业务 Owner',
        blockedActionCheck: '确认写回和流程自动化仍保持禁用。',
      },
      criticalDecisions: {
        title: '关键决策',
        status: '待确认',
        businessActionLabel: '业务动作',
        ownerLabel: '主要用户 / Owner',
        sourceLabel: '数据源',
        writebackLabel: '写回边界',
        acceptanceLabel: '验收证据',
        defaultBusinessAction: '用户最新种子',
        defaultOwner: '业务 Owner',
        defaultSource: 'source of truth',
        defaultWriteback: '只读或仅 Mock',
        defaultAcceptance: '冒烟测试证据',
      },
      reviewDecision: {
        title: 'IT 评审决策',
        recommendedLabel: '推荐',
        recommendedDecision: '有条件批准',
        allowedScopeLabel: '允许起步范围',
        allowedScope: '仅 UI/API 骨架和 Mock 数据',
        approve: '批准交接',
        conditional: '有条件批准',
        blocked: '阻塞',
        guardrail: '禁止生产写回',
      },
      steps: {
        seed: {
          label: '一句话想法',
          help: '想法、痛点或首个动作。',
        },
        prdV0: {
          label: '补齐信息',
          help: '补齐剩余关键需求缺口。',
        },
        handoff: {
          label: 'Go Coding',
          help: 'Vibe Coding 可读取生成文档和交接清单；状态不会自动回传。',
        },
      },
    },
    goCoding: 'Go Coding',
    openingGoCoding: '\u6b63\u5728\u6253\u5f00 Coding \u5de5\u4f5c\u533a...',
    notCaptured: 'TBD',
    status: {
      missing: '\u672a\u6536\u96c6',
      captured: '\u5df2\u6536\u96c6',
      pendingConfirmation: '\u5f85\u786e\u8ba4',
      confirmed: '\u5df2\u786e\u8ba4',
      conflict: '\u6709\u51b2\u7a81',
    },
    rows: {
      objective: '\u4e1a\u52a1\u76ee\u6807',
      scope: '\u8303\u56f4',
      users: '\u76ee\u6807\u7528\u6237',
      scenarios: '\u6838\u5fc3\u573a\u666f',
      features: '\u529f\u80fd\u9700\u6c42',
      pages: '\u9875\u9762',
      rules: '\u4e1a\u52a1\u89c4\u5219',
      integrations: '\u96c6\u6210\u7cfb\u7edf',
      acceptance: '\u9a8c\u6536\u6807\u51c6',
      ownership: '\u4e1a\u52a1 / \u9a8c\u6536\u8d1f\u8d23\u4eba',
    },
    scopeLabels: {
      in: '\u5305\u542b',
      out: '\u4e0d\u5305\u542b',
    },
    progressLabels: {
      readiness: 'Final 就绪度',
      finalReadiness: 'Final 就绪度',
      prdV0ReadinessTitle: 'Go Coding 信息充分度',
      prdV0Deliverable: '可评审需求',
      factBaseline: '事实基线',
      itReviewPacket: 'IT 评审包',
      assumptionsExplicit: '假设已显式列出',
      vibeCodingHandoff: 'Vibe Coding 交接',
      handoffAfterPrd: '交接前生成',
      finalPrdConfirmations: 'Final PRD 待确认',
      prdV0Handoff: 'Go Coding 交接',
      readyForItReview: '可进入 IT 评审',
      coverage: '\u6536\u96c6\u8986\u76d6\u7387',
      confirmationRate: '\u786e\u8ba4\u5b8c\u6210\u5ea6',
      pendingConfirmation: '\u5f85\u786e\u8ba4',
      blockingQuestions: '阻塞问题',
      conflict: '\u6709\u51b2\u7a81',
    },
    methodologyLabels: {
      score: '\u65b9\u6cd5\u8bba\u8bc1\u636e',
      ready: '\u5df2\u5c31\u7eea',
      missing: '\u7f3a\u53e3',
      nextQuestion: '\u4e0b\u4e00\u4e2a PM \u95ee\u9898',
    },
    icEvidenceLabels: {
      score: '\u9886\u57df\u8bc1\u636e',
      ready: '\u5df2\u5c31\u7eea',
      context: '\u90e8\u95e8',
      shape: '\u5f62\u6001',
      objects: '\u5bf9\u8c61',
      grain: '\u7c92\u5ea6',
      source: '\u6570\u636e\u6e90',
      nextQuestion: '\u4e0b\u4e00\u4e2a IC \u95ee\u9898',
    },
    methodologyStatus: {
      ready: '\u5df2\u5c31\u7eea',
      partial: '\u90e8\u5206\u8bc1\u636e',
      missing: '\u7f3a\u5931',
      conflict: '\u6709\u51b2\u7a81',
    },
    cardLabels: {
      reason: '\u5f53\u524d\u5224\u65ad',
      pendingQuestion: '\u4e0b\u4e00\u6b65\u5f85\u786e\u8ba4',
    },
  },
  ms: {
    requirementTitle: 'Model Keperluan Berstruktur',
    progressTitle: 'Kemajuan Keperluan',
    methodologyTitle: 'Metodologi PM',
    icEvidenceTitle: 'Evidence IC Substrate',
    loading: 'Model keperluan berstruktur sedang dikemas kini...',
    syncing: 'Sedang menyelaras...',
    generateDocuments: 'Jana Dokumen',
    generatingDocuments: 'Sedang menjana dokumen...',
    prdV0Ready: 'Dokumen ready',
    prdV0ReadyHelp: 'Maklumat requirement sudah cukup. Jana dokumen dahulu; Go Coding handoff dokumen itu ke Vibe Coding.',
    fastPath: {
      title: 'Readiness path',
      help: 'Hantar seed, jawab soalan pakar yang fokus, kemudian jana dokumen sebelum handoff ke Vibe Coding.',
      done: 'Selesai',
      current: 'Kini',
      pending: 'Seterus',
      questionBudgetLabel: 'Bajet soalan',
      questionBudgetHelp: 'Satu soalan fokus setiap pusingan.',
      exitRuleTitle: 'Peraturan keluar',
      exitRuleHelp: 'Berhenti tanya soalan baharu apabila requirement teras ready; jika belum, tanya hanya gap paling penting.',
      v0StatusTitle: 'Status readiness',
      v0StatusKnown: 'Diketahui',
      v0StatusAssumed: 'Andaian',
      v0StatusMissing: 'Gap',
      v0StatusConflict: 'Konflik',
      handoffPacketTitle: 'Paket handoff',
      handoffPacketItems: [
        'Dokumen requirement untuk semakan IT',
        'ASSUMPTIONS.md untuk gap terbuka',
        'mock-data.json sebelum kerja UI',
        'IT Review Decision Sheet',
        'Vibe Coding Start Here',
        'Tiada writeback production',
      ],
      firstBuildSlice: {
        title: 'First build slice',
        firstPageLabel: 'Halaman pertama',
        firstApiLabel: 'API pertama',
        mockDataLabel: 'Mock data',
        smokeTestLabel: 'Smoke test',
        guardrailLabel: 'Guardrail',
        defaultPage: 'Halaman requirement pertama',
        defaultApi: 'GET mock data API',
        defaultMockData: 'Rekod mock',
        defaultSmokeTest: 'Buka halaman pertama dengan mock data dan sahkan tindakan utama.',
        guardrail: 'Tiada writeback atau workflow automation',
      },
      acceptanceEvidence: {
        title: 'Acceptance evidence',
        proofTargetLabel: 'Proof target',
        artifactsLabel: 'Evidence artifacts',
        sourceLabel: 'Source to confirm',
        ownerLabel: 'Owner to confirm',
        blockedActionLabel: 'Blocked action check',
        defaultArtifacts: 'screenshot / mock_data_export / smoke_test_result',
        defaultSource: 'source of truth',
        defaultOwner: 'business owner',
        blockedActionCheck: 'Sahkan writeback dan workflow automation kekal dimatikan.',
      },
      criticalDecisions: {
        title: 'Critical decisions',
        status: 'Pending confirmation',
        businessActionLabel: 'Business action',
        ownerLabel: 'Primary user / owner',
        sourceLabel: 'Source of truth',
        writebackLabel: 'Writeback boundary',
        acceptanceLabel: 'Acceptance evidence',
        defaultBusinessAction: 'seed pengguna terkini',
        defaultOwner: 'business owner',
        defaultSource: 'source of truth',
        defaultWriteback: 'read-only atau mock-only',
        defaultAcceptance: 'Smoke test evidence',
      },
      reviewDecision: {
        title: 'IT Review Decision',
        recommendedLabel: 'Disyorkan',
        recommendedDecision: 'Kelulusan bersyarat',
        allowedScopeLabel: 'Skop mula dibenarkan',
        allowedScope: 'Shell UI/API dan mock data sahaja',
        approve: 'Lulus handoff',
        conditional: 'Kelulusan bersyarat',
        blocked: 'Disekat',
        guardrail: 'Tiada production writeback',
      },
      steps: {
        seed: {
          label: 'Satu ayat',
          help: 'Idea, pain point, atau tindakan pertama.',
        },
        prdV0: {
          label: 'Lengkapkan readiness',
          help: 'Tutup gap requirement kritikal yang masih tinggal.',
        },
        handoff: {
          label: 'Go Coding',
          help: 'Vibe Coding membaca dokumen yang dijana dan senarai semak handoff; status tidak kembali automatik.',
        },
      },
    },
    goCoding: 'Go Coding',
    openingGoCoding: 'Membuka Workspace Coding...',
    notCaptured: 'TBD',
    status: {
      missing: 'Belum ada',
      captured: 'Sudah dikumpul',
      pendingConfirmation: 'Perlu sahkan',
      confirmed: 'Disahkan',
      conflict: 'Bercanggah',
    },
    rows: {
      objective: 'Matlamat Perniagaan',
      scope: 'Skop',
      users: 'Pengguna Sasaran',
      scenarios: 'Senario Utama',
      features: 'Keperluan Fungsi',
      pages: 'Halaman',
      rules: 'Peraturan Perniagaan',
      integrations: 'Sistem Integrasi',
      acceptance: 'Kriteria Penerimaan',
      ownership: 'Pemilik Perniagaan / Penerimaan',
    },
    scopeLabels: {
      in: 'Dalam',
      out: 'Di luar',
    },
    progressLabels: {
      readiness: 'Final readiness',
      finalReadiness: 'Final readiness',
      prdV0ReadinessTitle: 'Go Coding readiness',
      prdV0Deliverable: 'IT-reviewable requirement',
      factBaseline: 'Fact baseline',
      itReviewPacket: 'IT review packet',
      assumptionsExplicit: 'Assumptions explicit',
      vibeCodingHandoff: 'Vibe Coding handoff',
      handoffAfterPrd: 'Dijana sebelum handoff',
      finalPrdConfirmations: 'Final PRD confirmations',
      prdV0Handoff: 'Go Coding handoff',
      readyForItReview: 'Ready for IT review',
      coverage: 'Liputan Kutipan',
      confirmationRate: 'Kemajuan Pengesahan',
      pendingConfirmation: 'Perlu sahkan',
      blockingQuestions: 'Soalan menghalang',
      conflict: 'Bercanggah',
    },
    methodologyLabels: {
      score: 'Evidence Metodologi',
      ready: 'Ready',
      missing: 'Jurang',
      nextQuestion: 'Soalan PM seterusnya',
    },
    icEvidenceLabels: {
      score: 'Evidence Domain',
      ready: 'Ready',
      context: 'Jabatan',
      shape: 'Bentuk',
      objects: 'Objek',
      grain: 'Grain',
      source: 'Sumber',
      nextQuestion: 'Soalan IC seterusnya',
    },
    methodologyStatus: {
      ready: 'Ready',
      partial: 'Sebahagian',
      missing: 'Belum ada',
      conflict: 'Bercanggah',
    },
    cardLabels: {
      reason: 'Penilaian semasa',
      pendingQuestion: 'Perkara seterusnya untuk disahkan',
    },
  },
} satisfies Record<
  LanguageCode,
  {
    requirementTitle: string
    progressTitle: string
    methodologyTitle: string
    icEvidenceTitle: string
    loading: string
    syncing: string
    generateDocuments: string
    generatingDocuments: string
    prdV0Ready: string
    prdV0ReadyHelp: string
    fastPath: {
      title: string
      help: string
      done: string
      current: string
      pending: string
      questionBudgetLabel: string
      questionBudgetHelp: string
      exitRuleTitle: string
      exitRuleHelp: string
      v0StatusTitle: string
      v0StatusKnown: string
      v0StatusAssumed: string
      v0StatusMissing: string
      v0StatusConflict: string
      handoffPacketTitle: string
      handoffPacketItems: string[]
      firstBuildSlice: {
        title: string
        firstPageLabel: string
        firstApiLabel: string
        mockDataLabel: string
        smokeTestLabel: string
        guardrailLabel: string
        defaultPage: string
        defaultApi: string
        defaultMockData: string
        defaultSmokeTest: string
        guardrail: string
      }
      acceptanceEvidence: {
        title: string
        proofTargetLabel: string
        artifactsLabel: string
        sourceLabel: string
        ownerLabel: string
        blockedActionLabel: string
        defaultArtifacts: string
        defaultSource: string
        defaultOwner: string
        blockedActionCheck: string
      }
      criticalDecisions: {
        title: string
        status: string
        businessActionLabel: string
        ownerLabel: string
        sourceLabel: string
        writebackLabel: string
        acceptanceLabel: string
        defaultBusinessAction: string
        defaultOwner: string
        defaultSource: string
        defaultWriteback: string
        defaultAcceptance: string
      }
      reviewDecision: {
        title: string
        recommendedLabel: string
        recommendedDecision: string
        allowedScopeLabel: string
        allowedScope: string
        approve: string
        conditional: string
        blocked: string
        guardrail: string
      }
      steps: Record<
        'seed' | 'prdV0' | 'handoff',
        {
          label: string
          help: string
        }
      >
    }
    goCoding: string
    openingGoCoding: string
    notCaptured: string
    status: Record<'missing' | 'captured' | 'pendingConfirmation' | 'confirmed' | 'conflict', string>
    rows: Record<
      | 'objective'
      | 'scope'
      | 'users'
      | 'scenarios'
      | 'features'
      | 'pages'
      | 'rules'
      | 'integrations'
      | 'acceptance'
      | 'ownership',
      string
    >
    scopeLabels: Record<'in' | 'out', string>
    progressLabels: Record<
      | 'readiness'
      | 'finalReadiness'
      | 'prdV0ReadinessTitle'
      | 'prdV0Deliverable'
      | 'factBaseline'
      | 'itReviewPacket'
      | 'assumptionsExplicit'
      | 'vibeCodingHandoff'
      | 'handoffAfterPrd'
      | 'finalPrdConfirmations'
      | 'prdV0Handoff'
      | 'readyForItReview'
      | 'coverage'
      | 'confirmationRate'
      | 'pendingConfirmation'
      | 'blockingQuestions'
      | 'conflict',
      string
    >
    methodologyLabels: Record<'score' | 'ready' | 'missing' | 'nextQuestion', string>
    icEvidenceLabels: Record<
      'score' | 'ready' | 'context' | 'shape' | 'objects' | 'grain' | 'source' | 'nextQuestion',
      string
    >
    methodologyStatus: Record<'ready' | 'partial' | 'missing' | 'conflict', string>
    cardLabels: Record<'reason' | 'pendingQuestion', string>
  }
>
