<script setup lang="ts">
import { computed, ref } from 'vue'

import MarkdownRenderer from './MarkdownRenderer.vue'
import { computeStructuredRequirementProgress } from '../lib/structuredRequirementProgress'
import type { LanguageCode } from '../types/session'
import type {
  StructuredRequirementCollectionStatus,
  StructuredRequirementFeature,
  StructuredRequirementModel,
  StructuredRequirementPage,
} from '../types/structuredRequirement'

type PreviewTab = 'user' | 'developer'

type PreviewCopy = {
  title: string
  subtitle: string
  loading: string
  syncing: string
  tbd: string
  progressLabel: string
  confirmationLabel: string
  tabs: {
    user: string
    developer: string
  }
  documentTitles: {
    user: string
    developer: string
  }
  draftHints: {
    user: string
    developer: string
  }
  missingHint: string
  featureLabel: string
  pageLabel: string
  fields: {
    projectName: string
    requirementName: string
    requestingDepartment: string
    businessOwner: string
    softwareType: string
    primaryUser: string
    decisionOrAction: string
    acceptanceOwner: string
    background: string
    objective: string
    description: string
    trigger: string
    processingLogic: string
    inputs: string
    outputs: string
    exceptionCases: string
    pageName: string
    entryPoint: string
    pageElements: string
    buttonActions: string
    draftNote: string
  }
  userSections: {
    title: string
    documentInfo: string
    background: string
    backgroundSummary: string
    objective: string
    scope: string
    inScope: string
    outOfScope: string
    usersAndScenarios: string
    targetUsers: string
    coreScenarios: string
    functionalRequirements: string
    featureOverview: string
    featureDetails: string
    businessRules: string
    pageInteraction: string
    pageDescription: string
    interactionFlow: string
    copywriting: string
    dataDependencies: string
    risksNotes: string
    acceptanceCriteria: string
    openQuestions: string
  }
  developerSections: {
    title: string
    scopeGoals: string
    scopeIn: string
    scopeOut: string
    roles: string
    useCases: string
    functionalRequirements: string
    featureOverview: string
    featureDetails: string
    businessRules: string
    nonFunctionalRequirements: string
    architecture: string
    modules: string
    moduleCandidates: string
    pageTouchpoints: string
    api: string
    dataModel: string
    dependencies: string
    keyFlows: string
    security: string
    observability: string
    deployment: string
    testing: string
    risks: string
    milestones: string
    openQuestions: string
  }
}

const props = withDefaults(
  defineProps<{
    language: LanguageCode
    model: StructuredRequirementModel
    loading?: boolean
    syncing?: boolean
    error?: string
  }>(),
  {
    loading: false,
    syncing: false,
    error: '',
  },
)

const enCopy: PreviewCopy = {
  title: 'Document Drafts',
  subtitle: 'Switch between the PRD draft and the technical draft generated from the current requirement model.',
  loading: 'Refreshing the latest collected requirements...',
  syncing: 'Syncing...',
  tbd: 'TBD',
  progressLabel: 'Collection coverage',
  confirmationLabel: 'Confirmation progress',
  tabs: {
    user: 'User View',
    developer: 'Developer View',
  },
  documentTitles: {
    user: 'PRD draft',
    developer: 'System design draft',
  },
  draftHints: {
    user: '> This PRD draft auto-syncs from the currently collected requirements.',
    developer: '> This design draft is assembled from the structured requirement model for quick technical review.',
  },
  missingHint: '> Missing or unconfirmed information is marked as TBD.',
  featureLabel: 'Feature',
  pageLabel: 'Page',
  fields: {
    projectName: 'Project name',
    requirementName: 'Requirement name',
    requestingDepartment: 'Requesting department',
    businessOwner: 'Business owner',
    softwareType: 'First-version software type',
    primaryUser: 'Primary user',
    decisionOrAction: 'Decision/action supported',
    acceptanceOwner: 'Acceptance owner',
    background: 'Background',
    objective: 'Objective',
    description: 'Description',
    trigger: 'Trigger',
    processingLogic: 'Processing logic',
    inputs: 'Inputs',
    outputs: 'Outputs',
    exceptionCases: 'Exception cases',
    pageName: 'Page name',
    entryPoint: 'Entry point',
    pageElements: 'Page elements',
    buttonActions: 'Button actions',
    draftNote: 'Draft note',
  },
  userSections: {
    title: '# PRD Template (Live Draft)',
    documentInfo: '## 1. Document Information',
    background: '## 2. Background',
    backgroundSummary: '### 2.1 Background Summary',
    objective: '### 2.2 Objective',
    scope: '## 3. Scope',
    inScope: '### 3.1 In Scope',
    outOfScope: '### 3.2 Out of Scope',
    usersAndScenarios: '## 4. Users and Usage Scenarios',
    targetUsers: '### 4.1 Target Users',
    coreScenarios: '### 4.2 Core Scenarios',
    functionalRequirements: '## 5. Functional Requirements',
    featureOverview: '### 5.1 Feature Overview',
    featureDetails: '### 5.2 Feature Details',
    businessRules: '## 6. Business Rules',
    pageInteraction: '## 7. Page / Interaction Notes',
    pageDescription: '### 7.1 Page Description',
    interactionFlow: '### 7.2 Interaction Flow',
    copywriting: '## 8. Copywriting',
    dataDependencies: '## 9. Data and Dependencies',
    risksNotes: '## 10. Risks and Notes',
    acceptanceCriteria: '## 11. Acceptance Criteria',
    openQuestions: '## 12. Open Questions',
  },
  developerSections: {
    title: '# System Design Document (Draft Scaffold)',
    scopeGoals: '## 1. Scope and Goals',
    scopeIn: '### 1.1 In Scope',
    scopeOut: '### 1.2 Out of Scope',
    roles: '## 2. User Roles and Participants',
    useCases: '## 3. System Use Cases',
    functionalRequirements: '## 4. Functional Requirements',
    featureOverview: '### 4.1 Feature Overview',
    featureDetails: '### 4.2 Feature Details',
    businessRules: '### 4.3 Business Rules',
    nonFunctionalRequirements: '## 5. Non-functional Requirements',
    architecture: '## 6. High-level Architecture Design',
    modules: '## 7. Module Responsibilities',
    moduleCandidates: '### 7.1 Candidate Modules',
    pageTouchpoints: '### 7.2 Page / Touchpoint Notes',
    api: '## 8. API Design (Draft)',
    dataModel: '## 9. Data Model and Database Design',
    dependencies: '### 9.1 Known Data / Dependency Inputs',
    keyFlows: '## 10. Key Flows / Sequence Notes',
    security: '## 11. Security, Privacy, and Compliance',
    observability: '## 12. Observability and Operations',
    deployment: '## 13. Deployment and Environment Planning',
    testing: '## 14. Testing and Acceptance Plan',
    risks: '## 15. Risks, Trade-offs, and Assumptions',
    milestones: '## 16. Milestones and Delivery Plan',
    openQuestions: '## 17. Open Questions / Missing Inputs',
  },
}

const zhCopy: PreviewCopy = {
  title: '\u6587\u6863\u8349\u7a3f',
  subtitle: '\u5207\u6362\u67e5\u770b PRD \u8349\u7a3f\u4e0e\u8bbe\u8ba1\u8349\u7a3f\u3002',
  loading: '\u6b63\u5728\u5237\u65b0\u6700\u65b0\u6536\u96c6\u5230\u7684\u9700\u6c42...',
  syncing: '\u540c\u6b65\u4e2d...',
  tbd: 'TBD',
  progressLabel: '\u6536\u96c6\u8986\u76d6\u7387',
  confirmationLabel: '\u786e\u8ba4\u5b8c\u6210\u5ea6',
  tabs: {
    user: '\u7528\u6237\u7248',
    developer: '\u5f00\u53d1\u7248',
  },
  documentTitles: {
    user: 'PRD \u8349\u7a3f',
    developer: '\u8bbe\u8ba1\u8349\u7a3f',
  },
  draftHints: {
    user: '> \u8be5 PRD \u8349\u7a3f\u4f1a\u6839\u636e\u5f53\u524d\u5df2\u6536\u96c6\u7684\u9700\u6c42\u81ea\u52a8\u540c\u6b65\u66f4\u65b0\u3002',
    developer: '> \u8be5\u8bbe\u8ba1\u6587\u6863\u8349\u7a3f\u4f1a\u5148\u57fa\u4e8e\u7ed3\u6784\u5316\u9700\u6c42\u751f\u6210\u7a33\u5b9a\u9aa8\u67b6\uff0c\u65b9\u4fbf\u5feb\u901f\u6280\u672f\u8bc4\u5ba1\u3002',
  },
  missingHint: '> \u5c1a\u672a\u786e\u8ba4\u6216\u7f3a\u5931\u7684\u4fe1\u606f\u4f1a\u6807\u8bb0\u4e3a TBD\u3002',
  featureLabel: '\u529f\u80fd',
  pageLabel: '\u9875\u9762',
  fields: {
    projectName: '\u9879\u76ee\u540d\u79f0',
    requirementName: '\u9700\u6c42\u540d\u79f0',
    requestingDepartment: '\u63d0\u9700\u90e8\u95e8',
    businessOwner: '\u4e1a\u52a1 Owner',
    softwareType: '\u7b2c\u4e00\u7248\u8f6f\u4ef6\u5f62\u6001',
    primaryUser: '\u6838\u5fc3\u4f7f\u7528\u8005',
    decisionOrAction: '\u652f\u6301\u7684\u51b3\u7b56 / \u52a8\u4f5c',
    acceptanceOwner: '\u9a8c\u6536\u8d23\u4efb\u4eba',
    background: '\u80cc\u666f\u8bf4\u660e',
    objective: '\u76ee\u6807',
    description: '\u529f\u80fd\u63cf\u8ff0',
    trigger: '\u89e6\u53d1\u65b9\u5f0f',
    processingLogic: '\u5904\u7406\u903b\u8f91',
    inputs: '\u8f93\u5165\u9879',
    outputs: '\u8f93\u51fa\u7ed3\u679c',
    exceptionCases: '\u5f02\u5e38\u60c5\u51b5',
    pageName: '\u9875\u9762\u540d\u79f0',
    entryPoint: '\u5165\u53e3\u4f4d\u7f6e',
    pageElements: '\u9875\u9762\u5143\u7d20',
    buttonActions: '\u6309\u94ae\u52a8\u4f5c',
    draftNote: '\u8349\u7a3f\u8bf4\u660e',
  },
  userSections: {
    title: '# PRD \u6587\u6863\u6a21\u677f\uff08\u5b9e\u65f6\u8349\u7a3f\uff09',
    documentInfo: '## 1. \u6587\u6863\u4fe1\u606f',
    background: '## 2. \u9700\u6c42\u80cc\u666f',
    backgroundSummary: '### 2.1 \u80cc\u666f\u8bf4\u660e',
    objective: '### 2.2 \u9700\u6c42\u76ee\u6807',
    scope: '## 3. \u9700\u6c42\u8303\u56f4',
    inScope: '### 3.1 \u672c\u6b21\u8303\u56f4',
    outOfScope: '### 3.2 \u975e\u672c\u6b21\u8303\u56f4',
    usersAndScenarios: '## 4. \u7528\u6237\u4e0e\u4f7f\u7528\u573a\u666f',
    targetUsers: '### 4.1 \u76ee\u6807\u7528\u6237',
    coreScenarios: '### 4.2 \u6838\u5fc3\u573a\u666f',
    functionalRequirements: '## 5. \u529f\u80fd\u9700\u6c42',
    featureOverview: '### 5.1 \u529f\u80fd\u6982\u8ff0',
    featureDetails: '### 5.2 \u529f\u80fd\u660e\u7ec6',
    businessRules: '## 6. \u4e1a\u52a1\u89c4\u5219',
    pageInteraction: '## 7. \u9875\u9762 / \u4ea4\u4e92\u8bf4\u660e',
    pageDescription: '### 7.1 \u9875\u9762\u8bf4\u660e',
    interactionFlow: '### 7.2 \u4ea4\u4e92\u6d41\u7a0b',
    copywriting: '## 8. \u6587\u6848\u8bf4\u660e',
    dataDependencies: '## 9. \u6570\u636e\u4e0e\u4f9d\u8d56',
    risksNotes: '## 10. \u98ce\u9669\u4e0e\u5907\u6ce8',
    acceptanceCriteria: '## 11. \u9a8c\u6536\u6807\u51c6',
    openQuestions: '## 12. \u5f85\u786e\u8ba4\u95ee\u9898',
  },
  developerSections: {
    title: '# \u7cfb\u7edf\u8bbe\u8ba1\u6587\u6863\uff08\u8349\u7a3f\u9aa8\u67b6\uff09',
    scopeGoals: '## 1. \u8303\u56f4\u4e0e\u76ee\u6807',
    scopeIn: '### 1.1 \u672c\u6b21\u8303\u56f4',
    scopeOut: '### 1.2 \u975e\u672c\u6b21\u8303\u56f4',
    roles: '## 2. \u7528\u6237\u89d2\u8272\u4e0e\u53c2\u4e0e\u65b9',
    useCases: '## 3. \u7cfb\u7edf\u7528\u4f8b',
    functionalRequirements: '## 4. \u529f\u80fd\u9700\u6c42',
    featureOverview: '### 4.1 \u529f\u80fd\u6982\u8ff0',
    featureDetails: '### 4.2 \u529f\u80fd\u660e\u7ec6',
    businessRules: '### 4.3 \u4e1a\u52a1\u89c4\u5219',
    nonFunctionalRequirements: '## 5. \u975e\u529f\u80fd\u9700\u6c42',
    architecture: '## 6. \u9ad8\u5c42\u67b6\u6784\u8bbe\u8ba1',
    modules: '## 7. \u6a21\u5757\u804c\u8d23\u5212\u5206',
    moduleCandidates: '### 7.1 \u5019\u9009\u6a21\u5757',
    pageTouchpoints: '### 7.2 \u9875\u9762 / \u89e6\u70b9\u8bf4\u660e',
    api: '## 8. API \u8bbe\u8ba1\uff08\u8349\u6848\uff09',
    dataModel: '## 9. \u6570\u636e\u6a21\u578b\u4e0e\u6570\u636e\u5e93\u8bbe\u8ba1',
    dependencies: '### 9.1 \u5df2\u8bc6\u522b\u7684\u6570\u636e / \u4f9d\u8d56\u8f93\u5165',
    keyFlows: '## 10. \u5173\u952e\u6d41\u7a0b / \u65f6\u5e8f\u8bf4\u660e',
    security: '## 11. \u5b89\u5168\u3001\u9690\u79c1\u4e0e\u5408\u89c4',
    observability: '## 12. \u53ef\u89c2\u6d4b\u6027\u4e0e\u8fd0\u7ef4',
    deployment: '## 13. \u90e8\u7f72\u4e0e\u73af\u5883\u89c4\u5212',
    testing: '## 14. \u6d4b\u8bd5\u4e0e\u9a8c\u6536\u65b9\u6848',
    risks: '## 15. \u98ce\u9669\u3001\u6743\u8861\u4e0e\u5047\u8bbe',
    milestones: '## 16. \u91cc\u7a0b\u7891\u4e0e\u4ea4\u4ed8\u8ba1\u5212',
    openQuestions: '## 17. \u5f85\u786e\u8ba4\u95ee\u9898 / \u7f3a\u5931\u8f93\u5165',
  },
}

const previewCopy: Record<LanguageCode, PreviewCopy> = {
  en: enCopy,
  de: {
    ...enCopy,
    title: 'Dokumententwuerfe',
    subtitle: 'Zwischen PRD-Entwurf und technischem Entwurf aus dem aktuellen Anforderungsmodell wechseln.',
    loading: 'Aktualisiere die zuletzt erfassten Anforderungen...',
    syncing: 'Synchronisiert...',
    progressLabel: 'Erfassungsgrad',
    confirmationLabel: 'Bestaetigungsstand',
    tabs: {
      user: 'Fachbereich',
      developer: 'Entwicklung',
    },
    documentTitles: {
      user: 'PRD-Entwurf',
      developer: 'Systemdesign-Entwurf',
    },
    draftHints: {
      user: '> Dieser PRD-Entwurf synchronisiert sich automatisch mit den aktuell erfassten Anforderungen.',
      developer: '> Dieser Design-Entwurf wird aus dem strukturierten Anforderungsmodell fuer die technische Pruefung aufgebaut.',
    },
    missingHint: '> Fehlende oder noch nicht bestaetigte Informationen werden als TBD markiert.',
    featureLabel: 'Funktion',
    pageLabel: 'Seite',
    fields: {
      projectName: 'Projektname',
      requirementName: 'Anforderungsname',
      requestingDepartment: 'Anfordernde Abteilung',
      businessOwner: 'Business Owner',
      softwareType: 'Softwaretyp der ersten Version',
      primaryUser: 'Hauptnutzer',
      decisionOrAction: 'Unterstuetzte Entscheidung/Aktion',
      acceptanceOwner: 'Abnahmeverantwortlicher',
      background: 'Hintergrund',
      objective: 'Ziel',
      description: 'Beschreibung',
      trigger: 'Ausloeser',
      processingLogic: 'Verarbeitungslogik',
      inputs: 'Eingaben',
      outputs: 'Ausgaben',
      exceptionCases: 'Ausnahmefaelle',
      pageName: 'Seitenname',
      entryPoint: 'Einstiegspunkt',
      pageElements: 'Seitenelemente',
      buttonActions: 'Button-Aktionen',
      draftNote: 'Entwurfshinweis',
    },
    userSections: {
      title: '# PRD-Vorlage (Live-Entwurf)',
      documentInfo: '## 1. Dokumentinformationen',
      background: '## 2. Hintergrund',
      backgroundSummary: '### 2.1 Hintergrundbeschreibung',
      objective: '### 2.2 Ziel',
      scope: '## 3. Umfang',
      inScope: '### 3.1 Im Umfang',
      outOfScope: '### 3.2 Nicht im Umfang',
      usersAndScenarios: '## 4. Nutzer und Nutzungsszenarien',
      targetUsers: '### 4.1 Zielnutzer',
      coreScenarios: '### 4.2 Kernszenarien',
      functionalRequirements: '## 5. Funktionale Anforderungen',
      featureOverview: '### 5.1 Funktionsueberblick',
      featureDetails: '### 5.2 Funktionsdetails',
      businessRules: '## 6. Geschaeftsregeln',
      pageInteraction: '## 7. Seiten- / Interaktionshinweise',
      pageDescription: '### 7.1 Seitenbeschreibung',
      interactionFlow: '### 7.2 Interaktionsablauf',
      copywriting: '## 8. Textinhalte',
      dataDependencies: '## 9. Daten und Abhaengigkeiten',
      risksNotes: '## 10. Risiken und Hinweise',
      acceptanceCriteria: '## 11. Abnahmekriterien',
      openQuestions: '## 12. Offene Fragen',
    },
    developerSections: {
      title: '# Systemdesign-Dokument (Entwurfsgeruest)',
      scopeGoals: '## 1. Umfang und Ziele',
      scopeIn: '### 1.1 Im Umfang',
      scopeOut: '### 1.2 Nicht im Umfang',
      roles: '## 2. Nutzerrollen und Beteiligte',
      useCases: '## 3. Systemanwendungsfaelle',
      functionalRequirements: '## 4. Funktionale Anforderungen',
      featureOverview: '### 4.1 Funktionsueberblick',
      featureDetails: '### 4.2 Funktionsdetails',
      businessRules: '### 4.3 Geschaeftsregeln',
      nonFunctionalRequirements: '## 5. Nicht-funktionale Anforderungen',
      architecture: '## 6. High-Level-Architektur',
      modules: '## 7. Modulverantwortlichkeiten',
      moduleCandidates: '### 7.1 Kandidatenmodule',
      pageTouchpoints: '### 7.2 Seiten- / Touchpoint-Hinweise',
      api: '## 8. API-Design (Entwurf)',
      dataModel: '## 9. Datenmodell und Datenbankdesign',
      dependencies: '### 9.1 Bekannte Daten- / Abhaengigkeitseingaben',
      keyFlows: '## 10. Wichtige Ablaeufe / Sequenzhinweise',
      security: '## 11. Sicherheit, Datenschutz und Compliance',
      observability: '## 12. Observability und Betrieb',
      deployment: '## 13. Deployment- und Umgebungsplanung',
      testing: '## 14. Test- und Abnahmeplan',
      risks: '## 15. Risiken, Trade-offs und Annahmen',
      milestones: '## 16. Meilensteine und Lieferplan',
      openQuestions: '## 17. Offene Fragen / fehlende Inputs',
    },
  },
  zh: zhCopy,
  ms: {
    ...enCopy,
    title: 'Draf Dokumen',
    subtitle: 'Tukar antara draf PRD dan draf teknikal berdasarkan model keperluan semasa.',
    loading: 'Menyegarkan keperluan terkini yang telah dikumpul...',
    syncing: 'Menyelaras...',
    progressLabel: 'Liputan kutipan',
    confirmationLabel: 'Kemajuan pengesahan',
    tabs: {
      user: 'Paparan Pengguna',
      developer: 'Paparan Pembangun',
    },
    documentTitles: {
      user: 'Draf PRD',
      developer: 'Draf reka bentuk sistem',
    },
    draftHints: {
      user: '> Draf PRD ini diselaraskan secara automatik daripada keperluan yang sedang dikumpul.',
      developer: '> Draf reka bentuk ini dibina daripada model keperluan berstruktur untuk semakan teknikal pantas.',
    },
    missingHint: '> Maklumat yang belum lengkap atau belum disahkan ditandakan sebagai TBD.',
    featureLabel: 'Fungsi',
    pageLabel: 'Halaman',
    fields: {
      projectName: 'Nama projek',
      requirementName: 'Nama keperluan',
      requestingDepartment: 'Jabatan pemohon',
      businessOwner: 'Pemilik bisnes',
      softwareType: 'Jenis perisian versi pertama',
      primaryUser: 'Pengguna utama',
      decisionOrAction: 'Keputusan/tindakan disokong',
      acceptanceOwner: 'Pemilik penerimaan',
      background: 'Latar belakang',
      objective: 'Objektif',
      description: 'Penerangan',
      trigger: 'Pencetus',
      processingLogic: 'Logik pemprosesan',
      inputs: 'Input',
      outputs: 'Output',
      exceptionCases: 'Kes pengecualian',
      pageName: 'Nama halaman',
      entryPoint: 'Titik masuk',
      pageElements: 'Elemen halaman',
      buttonActions: 'Tindakan butang',
      draftNote: 'Nota draf',
    },
    userSections: {
      title: '# Templat PRD (Draf Langsung)',
      documentInfo: '## 1. Maklumat Dokumen',
      background: '## 2. Latar Belakang',
      backgroundSummary: '### 2.1 Ringkasan Latar Belakang',
      objective: '### 2.2 Objektif',
      scope: '## 3. Skop',
      inScope: '### 3.1 Dalam Skop',
      outOfScope: '### 3.2 Di Luar Skop',
      usersAndScenarios: '## 4. Pengguna dan Senario Penggunaan',
      targetUsers: '### 4.1 Pengguna Sasaran',
      coreScenarios: '### 4.2 Senario Utama',
      functionalRequirements: '## 5. Keperluan Fungsi',
      featureOverview: '### 5.1 Gambaran Fungsi',
      featureDetails: '### 5.2 Butiran Fungsi',
      businessRules: '## 6. Peraturan Bisnes',
      pageInteraction: '## 7. Nota Halaman / Interaksi',
      pageDescription: '### 7.1 Penerangan Halaman',
      interactionFlow: '### 7.2 Aliran Interaksi',
      copywriting: '## 8. Teks Antara Muka',
      dataDependencies: '## 9. Data dan Kebergantungan',
      risksNotes: '## 10. Risiko dan Nota',
      acceptanceCriteria: '## 11. Kriteria Penerimaan',
      openQuestions: '## 12. Soalan Terbuka',
    },
    developerSections: {
      title: '# Dokumen Reka Bentuk Sistem (Rangka Draf)',
      scopeGoals: '## 1. Skop dan Matlamat',
      scopeIn: '### 1.1 Dalam Skop',
      scopeOut: '### 1.2 Di Luar Skop',
      roles: '## 2. Peranan Pengguna dan Peserta',
      useCases: '## 3. Kes Penggunaan Sistem',
      functionalRequirements: '## 4. Keperluan Fungsi',
      featureOverview: '### 4.1 Gambaran Fungsi',
      featureDetails: '### 4.2 Butiran Fungsi',
      businessRules: '### 4.3 Peraturan Bisnes',
      nonFunctionalRequirements: '## 5. Keperluan Bukan Fungsi',
      architecture: '## 6. Reka Bentuk Seni Bina Peringkat Tinggi',
      modules: '## 7. Tanggungjawab Modul',
      moduleCandidates: '### 7.1 Modul Cadangan',
      pageTouchpoints: '### 7.2 Nota Halaman / Titik Sentuh',
      api: '## 8. Reka Bentuk API (Draf)',
      dataModel: '## 9. Model Data dan Reka Bentuk Pangkalan Data',
      dependencies: '### 9.1 Input Data / Kebergantungan Dikenal Pasti',
      keyFlows: '## 10. Aliran Utama / Nota Urutan',
      security: '## 11. Keselamatan, Privasi dan Pematuhan',
      observability: '## 12. Kebolehcerapan dan Operasi',
      deployment: '## 13. Perancangan Deployment dan Persekitaran',
      testing: '## 14. Pelan Ujian dan Penerimaan',
      risks: '## 15. Risiko, Trade-off dan Andaian',
      milestones: '## 16. Milestone dan Pelan Serahan',
      openQuestions: '## 17. Soalan Terbuka / Input Hilang',
    },
  },
}

const activeTab = ref<PreviewTab>('user')
const copy = computed(() => previewCopy[props.language] ?? previewCopy.en)
const progress = computed(() => computeStructuredRequirementProgress(props.model))
const userMarkdownDocument = computed(() => buildUserMarkdownDocument(props.model, copy.value, progress.value))
const developerMarkdownDocument = computed(() => buildDeveloperMarkdownDocument(props.model, copy.value, progress.value))
const activeDocument = computed(() =>
  activeTab.value === 'user' ? userMarkdownDocument.value : developerMarkdownDocument.value,
)
const activeDocumentTitle = computed(() =>
  activeTab.value === 'user' ? copy.value.documentTitles.user : copy.value.documentTitles.developer,
)

function onWheelScroll(event: WheelEvent): void {
  const container = event.currentTarget as HTMLElement | null
  if (!container || container.scrollHeight <= container.clientHeight + 1) {
    return
  }

  const maxScrollTop = container.scrollHeight - container.clientHeight
  const isAtTop = container.scrollTop <= 0
  const isAtBottom = container.scrollTop >= maxScrollTop - 1

  if ((event.deltaY < 0 && isAtTop) || (event.deltaY > 0 && isAtBottom)) {
    return
  }

  event.preventDefault()
  const nextScrollTop = container.scrollTop + event.deltaY
  container.scrollTop = Math.min(maxScrollTop, Math.max(0, nextScrollTop))
}

function buildUserMarkdownDocument(
  model: StructuredRequirementModel,
  labels: PreviewCopy,
  progressValue: ReturnType<typeof computeStructuredRequirementProgress>,
): string {
  const lines: string[] = [
    labels.userSections.title,
    '',
    labels.draftHints.user,
    labels.missingHint,
    `> ${labels.progressLabel}: ${progressValue.collectionCoveragePercentage}% | ${labels.confirmationLabel}: ${progressValue.confirmationPercentage}%`,
    '',
    labels.userSections.documentInfo,
    '',
    `- ${labels.fields.projectName}: ${valueOrTbd(model.document_info.project_name, labels.tbd)}`,
    `- ${labels.fields.requirementName}: ${valueOrTbd(model.document_info.requirement_name, labels.tbd)}`,
    ...asProductContextLines(model, labels),
    '',
    labels.userSections.background,
    '',
    labels.userSections.backgroundSummary,
    '',
    valueOrTbd(model.background.summary, labels.tbd),
    '',
    labels.userSections.objective,
    '',
    valueOrTbd(model.background.objective, labels.tbd),
    '',
    labels.userSections.scope,
    '',
    labels.userSections.inScope,
    ...asBulletSection(model.scope.in_scope, labels.tbd),
    '',
    labels.userSections.outOfScope,
    ...asBulletSection(model.scope.out_of_scope, labels.tbd),
    '',
    labels.userSections.usersAndScenarios,
    '',
    labels.userSections.targetUsers,
    ...asBulletSection(model.users_and_scenarios.target_users, labels.tbd),
    '',
    labels.userSections.coreScenarios,
    ...asNumberedSection(model.users_and_scenarios.core_scenarios, labels.tbd),
    '',
    labels.userSections.functionalRequirements,
    '',
    labels.userSections.featureOverview,
    '',
    valueOrTbd(model.functional_requirements.overview, labels.tbd),
    '',
    labels.userSections.featureDetails,
    ...asFeatureSection(model.functional_requirements.feature_details, labels),
    '',
    labels.userSections.businessRules,
    ...asBulletSection(model.business_rules, labels.tbd),
    '',
    labels.userSections.pageInteraction,
    '',
    labels.userSections.pageDescription,
    ...asPageSection(model.page_and_interaction.pages, labels),
    '',
    labels.userSections.interactionFlow,
    ...asNumberedSection(model.page_and_interaction.interaction_flow, labels.tbd),
    '',
    labels.userSections.copywriting,
    ...asBulletSection(model.copywriting, labels.tbd),
    '',
    labels.userSections.dataDependencies,
    ...asBulletSection(model.data_and_dependencies, labels.tbd),
    '',
    labels.userSections.risksNotes,
    ...asBulletSection(model.risks_and_notes, labels.tbd),
  ]

  if (model.acceptance_criteria.length) {
    lines.push('', labels.userSections.acceptanceCriteria, ...asBulletSection(model.acceptance_criteria, labels.tbd))
  }

  if (model.open_questions.length) {
    lines.push('', labels.userSections.openQuestions, ...asBulletSection(model.open_questions, labels.tbd))
  }

  return lines.join('\n')
}

function buildDeveloperMarkdownDocument(
  model: StructuredRequirementModel,
  labels: PreviewCopy,
  progressValue: ReturnType<typeof computeStructuredRequirementProgress>,
): string {
  const riskNotes = normalizeList(model.risks_and_notes)
  const developerRiskNotes = progressValue.fullyConfirmed
    ? riskNotes
    : [
        `${labels.fields.draftNote}: ${draftAssumptionNote(labels)}`,
        ...riskNotes,
      ]

  const lines: string[] = [
    labels.developerSections.title,
    '',
    labels.draftHints.developer,
    labels.missingHint,
    `> ${labels.progressLabel}: ${progressValue.collectionCoveragePercentage}% | ${labels.confirmationLabel}: ${progressValue.confirmationPercentage}%`,
    '',
    labels.developerSections.scopeGoals,
    '',
    `- ${labels.fields.projectName}: ${valueOrTbd(model.document_info.project_name, labels.tbd)}`,
    `- ${labels.fields.requirementName}: ${valueOrTbd(model.document_info.requirement_name, labels.tbd)}`,
    ...asProductContextLines(model, labels),
    `- ${labels.fields.background}: ${valueOrTbd(model.background.summary, labels.tbd)}`,
    `- ${labels.fields.objective}: ${valueOrTbd(model.background.objective, labels.tbd)}`,
    '',
    labels.developerSections.scopeIn,
    ...asBulletSection(model.scope.in_scope, labels.tbd),
    '',
    labels.developerSections.scopeOut,
    ...asBulletSection(model.scope.out_of_scope, labels.tbd),
    '',
    labels.developerSections.roles,
    ...asBulletSection(model.users_and_scenarios.target_users, labels.tbd),
    '',
    labels.developerSections.useCases,
    ...asNumberedSection(model.users_and_scenarios.core_scenarios, labels.tbd),
    '',
    labels.developerSections.functionalRequirements,
    '',
    labels.developerSections.featureOverview,
    '',
    valueOrTbd(model.functional_requirements.overview, labels.tbd),
    '',
    labels.developerSections.featureDetails,
    ...asFeatureSection(model.functional_requirements.feature_details, labels),
    '',
    labels.developerSections.businessRules,
    ...asBulletSection(model.business_rules, labels.tbd),
    '',
    labels.developerSections.nonFunctionalRequirements,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.architecture,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.modules,
    '',
    labels.developerSections.moduleCandidates,
    ...asBulletSection(collectModuleCandidates(model), labels.tbd),
    '',
    labels.developerSections.pageTouchpoints,
    ...asPageSection(model.page_and_interaction.pages, labels),
    '',
    labels.developerSections.api,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.dataModel,
    '',
    labels.developerSections.dependencies,
    ...asBulletSection(model.data_and_dependencies, labels.tbd),
    '',
    labels.developerSections.keyFlows,
    ...asNumberedSection(model.page_and_interaction.interaction_flow, labels.tbd),
    '',
    labels.developerSections.security,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.observability,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.deployment,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.testing,
    ...asBulletSection(model.acceptance_criteria, labels.tbd),
    '',
    labels.developerSections.risks,
    ...asBulletSection(developerRiskNotes, labels.tbd),
    '',
    labels.developerSections.milestones,
    ...asBulletSection([], labels.tbd),
    '',
    labels.developerSections.openQuestions,
    ...asBulletSection(collectOpenQuestions(model.collection_status, model.open_questions), labels.tbd),
  ]

  return lines.join('\n')
}

function asBulletSection(values: string[], fallback: string): string[] {
  const normalized = normalizeList(values)
  if (!normalized.length) {
    return ['', `- ${fallback}`]
  }

  return ['', ...normalized.map((item) => `- ${item}`)]
}

function asNumberedSection(values: string[], fallback: string): string[] {
  const normalized = normalizeList(values)
  if (!normalized.length) {
    return ['', `1. ${fallback}`]
  }

  return ['', ...normalized.map((item, index) => `${index + 1}. ${item}`)]
}

function asFeatureSection(features: StructuredRequirementFeature[], labels: PreviewCopy): string[] {
  const normalized = features.filter((item) => featureHasContent(item))
  if (!normalized.length) {
    return ['', `- ${labels.tbd}`]
  }

  const lines: string[] = ['']
  normalized.forEach((feature, index) => {
    const title = feature.feature_name || feature.description || labels.tbd
    lines.push(`#### ${labels.featureLabel} ${index + 1}: ${title}`)
    lines.push('')
    lines.push(`- ${labels.fields.description}: ${valueOrTbd(feature.description, labels.tbd)}`)
    lines.push(`- ${labels.fields.trigger}: ${valueOrTbd(feature.trigger, labels.tbd)}`)
    lines.push(`- ${labels.fields.processingLogic}: ${valueOrTbd(feature.processing_logic, labels.tbd)}`)
    lines.push(`- ${labels.fields.inputs}: ${joinOrTbd(feature.inputs, labels.tbd)}`)
    lines.push(`- ${labels.fields.outputs}: ${joinOrTbd(feature.outputs, labels.tbd)}`)
    lines.push(`- ${labels.fields.exceptionCases}: ${joinOrTbd(feature.exception_cases, labels.tbd)}`)
    if (index < normalized.length - 1) {
      lines.push('')
    }
  })
  return lines
}

function asPageSection(pages: StructuredRequirementPage[], labels: PreviewCopy): string[] {
  const normalized = pages.filter((item) => pageHasContent(item))
  if (!normalized.length) {
    return ['', `- ${labels.tbd}`]
  }

  const lines: string[] = ['']
  normalized.forEach((page, index) => {
    const title = page.page_name || page.entry_point || labels.tbd
    lines.push(`#### ${labels.pageLabel} ${index + 1}: ${title}`)
    lines.push('')
    lines.push(`- ${labels.fields.pageName}: ${valueOrTbd(page.page_name, labels.tbd)}`)
    lines.push(`- ${labels.fields.entryPoint}: ${valueOrTbd(page.entry_point, labels.tbd)}`)
    lines.push(`- ${labels.fields.pageElements}: ${joinOrTbd(page.page_elements, labels.tbd)}`)
    lines.push(`- ${labels.fields.buttonActions}: ${joinOrTbd(page.button_actions, labels.tbd)}`)
    if (index < normalized.length - 1) {
      lines.push('')
    }
  })
  return lines
}

function collectModuleCandidates(model: StructuredRequirementModel): string[] {
  const values = [
    ...model.functional_requirements.feature_details.map((item) => item.feature_name || item.description),
    ...model.page_and_interaction.pages.map((item) => item.page_name || item.entry_point),
  ]
  return uniqueStrings(values)
}

function collectOpenQuestions(
  collectionStatus: StructuredRequirementCollectionStatus,
  openQuestions: string[],
): string[] {
  const pendingQuestions = Object.values(collectionStatus).flatMap((item) => item.pending_questions)
  return uniqueStrings([...openQuestions, ...pendingQuestions])
}

function asProductContextLines(model: StructuredRequirementModel, labels: PreviewCopy): string[] {
  const context = model.product_context
  return [
    `- ${labels.fields.requestingDepartment}: ${valueOrTbd(context.requesting_department, labels.tbd)}`,
    `- ${labels.fields.businessOwner}: ${valueOrTbd(context.business_owner, labels.tbd)}`,
    `- ${labels.fields.softwareType}: ${valueOrTbd(context.software_type, labels.tbd)}`,
    `- ${labels.fields.primaryUser}: ${valueOrTbd(context.primary_user, labels.tbd)}`,
    `- ${labels.fields.decisionOrAction}: ${valueOrTbd(context.decision_or_action, labels.tbd)}`,
    `- ${labels.fields.acceptanceOwner}: ${valueOrTbd(context.acceptance_owner, labels.tbd)}`,
  ]
}

function uniqueStrings(values: string[]): string[] {
  return Array.from(new Set(normalizeList(values)))
}

function normalizeList(values: string[]): string[] {
  return values.map((item) => item.trim()).filter(Boolean)
}

function joinOrTbd(values: string[], fallback: string): string {
  const normalized = normalizeList(values)
  return normalized.length ? normalized.join(', ') : fallback
}

function valueOrTbd(value: string, fallback: string): string {
  const normalized = value.trim()
  return normalized || fallback
}

function draftAssumptionNote(labels: PreviewCopy): string {
  if (labels.tabs.user === '\u7528\u6237\u7248') {
    return '\u5f53\u524d\u9700\u6c42\u8fd8\u6ca1\u6709\u5168\u90e8\u786e\u8ba4\uff0c\u8bbe\u8ba1\u6587\u6863\u4e2d\u4ecd\u5305\u542b\u8349\u7a3f\u6027\u5047\u8bbe\u3002'
  }
  return 'Not all requirements are fully confirmed yet, so this design preview still contains draft assumptions.'
}

function featureHasContent(feature: StructuredRequirementFeature): boolean {
  return Boolean(
    feature.feature_name ||
      feature.description ||
      feature.trigger ||
      feature.processing_logic ||
      feature.inputs.length ||
      feature.outputs.length ||
      feature.exception_cases.length,
  )
}

function pageHasContent(page: StructuredRequirementPage): boolean {
  return Boolean(
    page.page_name ||
      page.entry_point ||
      page.page_elements.length ||
      page.button_actions.length,
  )
}
</script>

<template>
  <section class="document-preview-card" @wheel="onWheelScroll">
    <header class="document-preview-head">
      <div>
        <h3>{{ copy.title }}</h3>
        <p>{{ copy.subtitle }}</p>
      </div>

      <div class="document-preview-head-actions">
        <span v-if="syncing" class="document-preview-badge">{{ copy.syncing }}</span>

        <div class="document-preview-tabs" role="tablist" aria-label="preview switcher">
          <button
            type="button"
            class="document-preview-tab"
            :class="{ active: activeTab === 'user' }"
            role="tab"
            :aria-selected="activeTab === 'user'"
            @click="activeTab = 'user'"
          >
            {{ copy.tabs.user }}
          </button>
          <button
            type="button"
            class="document-preview-tab"
            :class="{ active: activeTab === 'developer' }"
            role="tab"
            :aria-selected="activeTab === 'developer'"
            @click="activeTab = 'developer'"
          >
            {{ copy.tabs.developer }}
          </button>
        </div>
      </div>
    </header>

    <div v-if="loading" class="document-preview-state">
      {{ copy.loading }}
    </div>
    <div v-else-if="error" class="document-preview-state error">
      {{ error }}
    </div>
    <div v-else class="document-preview-shell">
      <div class="document-preview-label">{{ activeDocumentTitle }}</div>
      <MarkdownRenderer class="document-preview-content" :source="activeDocument" />
    </div>
  </section>
</template>

<style scoped>
.document-preview-card {
  min-height: 0;
  height: 100%;
  display: block;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #ffffff;
  box-shadow: var(--shadow-soft, 0 8px 22px rgba(38, 55, 70, 0.08));
  overflow: auto;
  scrollbar-gutter: stable;
  scrollbar-width: none;
  scrollbar-color: transparent transparent;
}

.document-preview-card::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.document-preview-card:hover {
  scrollbar-width: thin;
  scrollbar-color: rgba(117, 136, 173, 0.82) transparent;
}

.document-preview-card:hover::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.document-preview-card:hover::-webkit-scrollbar-thumb {
  background: rgba(117, 136, 173, 0.82);
  border-radius: 999px;
}

.document-preview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--line);
}

.document-preview-head h3 {
  margin: 0;
  font-size: 0.92rem;
  color: var(--ink);
}

.document-preview-head p {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.45;
}

.document-preview-head-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.document-preview-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 9px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.12);
  color: #173f9f;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}

.document-preview-badge::before {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  animation: syncPulse 1.2s ease-in-out infinite;
}

.document-preview-tabs {
  display: inline-flex;
  align-items: center;
  padding: 3px;
  border-radius: 8px;
  background: var(--accent-soft);
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.16);
}

.document-preview-tab {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding: 8px 13px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.document-preview-tab:hover {
  color: var(--ink);
}

.document-preview-tab.active {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 10px 18px rgba(37, 99, 235, 0.22);
}

.document-preview-state {
  margin: 16px;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px dashed rgba(37, 99, 235, 0.34);
  color: var(--muted);
  background: #fbfdfe;
  line-height: 1.5;
  font-size: 0.82rem;
}

.document-preview-state.error {
  border-style: solid;
  border-color: rgba(220, 38, 38, 0.38);
  color: #991b1b;
  background: rgba(220, 38, 38, 0.13);
}

.document-preview-shell {
  display: block;
  padding: 16px;
  overflow: visible;
}

.document-preview-label {
  margin-bottom: 8px;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.document-preview-content {
  margin: 0;
  padding: 14px 16px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: #fbfdfe;
  color: var(--ink);
  font-size: 0.86rem;
  line-height: 1.62;
  white-space: normal;
  overflow: visible;
  max-height: none;
}

@media (max-width: 900px) {
  .document-preview-head {
    flex-direction: column;
  }

  .document-preview-head-actions {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .document-preview-card {
    min-height: min(76vh, 680px);
  }

  .document-preview-tabs {
    width: 100%;
  }

  .document-preview-tab {
    flex: 1;
    text-align: center;
  }
}

@keyframes syncPulse {
  0%,
  100% {
    opacity: 0.35;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
