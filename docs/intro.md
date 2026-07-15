# SpecViewer

## Technical Requirements for an AI Skills Repository

**Document status:** Draft
**Repository name:** `spec-viewer`
**Product name:** SpecViewer
**Target version:** MVP 1.0
**Primary repository language:** English
**Supported source-document languages:** Any language supported by the active AI model
**Default workspace visibility:** Private
**git-repo** git remote add origin https://github.com/vladkrasavinwork-lab/spec-viewer.git

---

# 1. Назначение документа

Настоящее техническое задание описывает требования к репозиторию SpecViewer — набору переиспользуемых AI skills и вспомогательных инструментов для работы с техническими заданиями на разработку цифровых продуктов.

Система должна позволять:

1. Принимать исходное техническое задание в документном формате.
2. Преобразовывать его в канонический Markdown.
3. Проверять качество, полноту и готовность ТЗ к разработке.
4. Формировать уточняющие вопросы.
5. Создавать исправленную версию ТЗ.
6. Оценивать сроки и стоимость разработки.
7. Учитывать использование AI-assisted development.
8. Оценивать инфраструктурные и эксплуатационные расходы.
9. Хранить все материалы каждого проекта в отдельном приватном workspace.
10. Исключать попадание приватных проектных материалов в Git.

Репозиторий не является системой управления проектами, генератором программного кода или заменой профессиональной юридической, финансовой либо security-экспертизы.

---

# 2. Цели продукта

## 2.1. Основная цель

Создать стандартизированный и воспроизводимый процесс преобразования исходного ТЗ в набор проверенных проектных артефактов:

* отчёт о качестве;
* реестр обнаруженных проблем;
* список уточняющих вопросов;
* исправленное ТЗ;
* реестр предположений;
* оценку сроков;
* оценку стоимости;
* сценарии инфраструктурных расходов;
* модель стоимости поддержки.

## 2.2. Дополнительные цели

Система должна:

* уменьшать количество пропущенных требований;
* выявлять противоречия до начала разработки;
* отделять подтверждённые требования от предположений;
* предотвращать скрытое придумывание бизнес-правил моделью;
* обеспечивать связь оценки с конкретными требованиями;
* сохранять историю изменений;
* позволять повторно запускать анализ после получения ответов;
* обеспечивать единообразный формат результатов для разных проектов;
* быть пригодной для командного использования;
* оставаться переносимой между AI-окружениями, поддерживающими Agent Skills.

---

# 3. Термины

## 3.1. Skill

Версионируемый набор инструкций, reference-файлов, шаблонов и при необходимости детерминированных скриптов, предназначенный для выполнения одной специализированной задачи.

Для совместимости с OpenAI Codex каждый skill должен находиться в отдельной директории, содержать обязательный `SKILL.md` с полями `name` и `description` и при необходимости директории `scripts/`, `references/` и `assets/`. Репозиторные skills должны располагаться в `.agents/skills/`.

## 3.2. Workspace

Изолированная директория конкретного проекта, содержащая исходный документ, нормализованную версию, контекст, ответы, результаты skills и историю запусков.

## 3.3. Source document

Оригинальный документ, предоставленный пользователем: DOCX, PDF, Markdown или другой поддерживаемый формат.

## 3.4. Canonical Markdown

Стандартизированная Markdown-версия исходного документа, используемая всеми skills как основной источник.

## 3.5. Finding

Обнаруженная проблема, риск, противоречие, пробел или неопределённость в ТЗ.

## 3.6. Blocking question

Вопрос, без ответа на который невозможно безопасно продолжить исправление или достоверную оценку проекта.

## 3.7. AI-assisted development

Модель разработки, в которой AI используется для генерации кода, тестов, документации, анализа, рефакторинга и других задач, но итоговые решения и контроль качества остаются за человеком.

## 3.8. Run

Один зафиксированный запуск skill с определённой версией входных данных, конфигурации и методологии.

---

# 4. Нормативные обозначения

В настоящем документе используются следующие уровни обязательности:

* **MUST** — обязательное требование MVP.
* **SHOULD** — рекомендуемое требование, которое может быть отложено только по обоснованной причине.
* **MAY** — необязательная возможность.

---

# 5. Основные архитектурные принципы

## 5.1. Один skill — одна задача

Каждый skill MUST иметь одну основную ответственность.

В MVP запрещается объединять проверку, переписывание и оценку в один универсальный skill.

Такое разделение соответствует рекомендации создавать skill для одной сфокусированной работы, явно определять его входы и выходы и начинать с конкретных сценариев использования.

## 5.2. Progressive disclosure

Основной `SKILL.md` MUST быть компактным.

Подробные методологии, схемы, примеры, чек-листы и шаблоны MUST храниться в:

* `references/`;
* `assets/`;
* `scripts/`, если требуется детерминированная обработка.

AI сначала получает метаданные skills, затем загружает полный `SKILL.md` выбранного skill и только после этого обращается к необходимым reference-файлам или scripts.

## 5.3. Evidence-based output

Каждое существенное замечание MUST ссылаться на конкретный раздел исходного документа либо объяснять, почему такой ссылки нет.

## 5.4. No silent invention

AI MUST NOT скрыто придумывать:

* бизнес-правила;
* роли пользователей;
* юридические требования;
* сроки хранения данных;
* SLA;
* нагрузку;
* бюджет;
* стоимость труда;
* тарифы облачных провайдеров;
* критерии успешности продукта.

## 5.5. Private by default

Все реальные проектные workspace MUST быть приватными по умолчанию и MUST NOT отслеживаться Git.

## 5.6. Source immutability

Исходные документы MUST NOT изменяться.

Все исправленные версии должны создаваться как новые артефакты.

## 5.7. Human-readable and machine-readable

Основные результаты MUST иметь:

* человекочитаемую Markdown-версию;
* структурированные YAML- или JSON-реестры там, где требуется трассировка и автоматическая проверка.

## 5.8. Reproducibility

Каждый результат MUST содержать:

* версию skill;
* версию методологии;
* версию схемы;
* идентификатор запуска;
* идентификатор проекта;
* хеш входного документа;
* дату генерации;
* уровень уверенности.

---

# 6. Объём MVP

В MVP должны входить три skills.

## 6.1. `product-spec-review`

Проверка качества ТЗ и поиск недостатков.

## 6.2. `product-spec-rewrite`

Создание исправленной версии ТЗ с учётом замечаний и ответов пользователя.

## 6.3. `product-delivery-estimate`

Оценка:

* объёма разработки;
* календарных сроков;
* стоимости разработки;
* влияния AI-assisted development;
* инфраструктурных расходов;
* стоимости технической поддержки.

## 6.4. Вспомогательные возможности

MVP также MUST включать:

* инициализацию workspace;
* нормализацию документа;
* управление версиями артефактов;
* обновление project manifest;
* проверку приватности;
* схемы выходных файлов;
* автоматические проверки структуры;
* eval-наборы для каждого skill.

---

# 7. Что не входит в MVP

В MVP не входят:

* генерация production-кода;
* автоматическая постановка задач в Jira;
* интеграция с CRM;
* интеграция с бухгалтерскими системами;
* автоматическое выставление коммерческих предложений;
* автоматическая закупка облачных ресурсов;
* автоматический деплой;
* юридическая сертификация документов;
* формальная security-сертификация;
* точное прогнозирование рыночной стоимости разработчиков;
* получение актуальных облачных тарифов без явно подключённого источника;
* полноценный веб-интерфейс;
* multi-agent orchestration;
* управление реализацией после завершения оценки.

---

# 8. Целевой пользовательский сценарий

## 8.1. Основной сценарий

1. Пользователь предоставляет файл с ТЗ.
2. Система получает или формирует название проекта.
3. Создаётся workspace:

```text
workspaces/<project-slug>_private/
```

4. Исходный файл сохраняется без изменений.
5. Документ преобразуется в канонический Markdown.
6. Фиксируются предупреждения конвертации.
7. Запускается `product-spec-review`.
8. Формируется отчёт, реестр проблем и вопросы.
9. Пользователь отвечает на существенные вопросы.
10. Ответы сохраняются в контексте проекта.
11. Review может быть запущен повторно.
12. Запускается `product-spec-rewrite`.
13. Создаётся исправленное ТЗ.
14. Запускается `product-delivery-estimate`.
15. Создаются оценки разработки, инфраструктуры и поддержки.
16. `project.yaml` обновляется ссылками на актуальные результаты.
17. Все предыдущие запуски сохраняются.
18. Проверка приватности подтверждает отсутствие проектных файлов в Git index.

## 8.2. Повторный запуск

При изменении исходного документа, добавлении ответов или корректировке ограничений система MUST:

* не удалять предыдущие результаты;
* сформировать новый `run_id`;
* зафиксировать новый хеш входа;
* определить устаревшие результаты;
* обновить указатели на актуальные артефакты;
* сохранить трассировку между версиями.

---

# 9. Структура репозитория

```text
spec-viewer/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── LICENSE
├── .gitignore
│
├── .agents/
│   └── skills/
│       ├── product-spec-review/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   ├── assets/
│       │   └── scripts/
│       │
│       ├── product-spec-rewrite/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   ├── assets/
│       │   └── scripts/
│       │
│       └── product-delivery-estimate/
│           ├── SKILL.md
│           ├── references/
│           ├── assets/
│           └── scripts/
│
├── standards/
│   ├── canonical-document-format.md
│   ├── requirement-writing-standard.md
│   ├── requirement-id-policy.md
│   ├── issue-taxonomy.md
│   ├── clarification-protocol.md
│   ├── assumption-policy.md
│   ├── estimation-methodology.md
│   ├── ai-assisted-development-model.md
│   ├── workspace-lifecycle.md
│   └── privacy-policy.md
│
├── profiles/
│   ├── product/
│   │   ├── generic-product.md
│   │   ├── web-application.md
│   │   ├── mobile-application.md
│   │   ├── api-integration.md
│   │   ├── internal-system.md
│   │   └── ai-product.md
│   │
│   ├── team/
│   │   ├── solo-ai-assisted.md
│   │   ├── small-ai-assisted-team.md
│   │   └── traditional-team.md
│   │
│   └── operations/
│       ├── prototype.md
│       ├── standard-production.md
│       └── high-availability.md
│
├── schemas/
│   ├── project.schema.json
│   ├── document-metadata.schema.json
│   ├── review-summary.schema.json
│   ├── issue-register.schema.json
│   ├── clarification-register.schema.json
│   ├── assumption-register.schema.json
│   ├── change-log.schema.json
│   ├── work-breakdown.schema.json
│   ├── estimate-summary.schema.json
│   └── infrastructure-scenarios.schema.json
│
├── templates/
│   ├── workspace/
│   ├── review/
│   ├── rewrite/
│   └── estimate/
│
├── tools/
│   ├── workspace/
│   ├── normalization/
│   ├── validation/
│   └── history/
│
├── examples/
│   ├── good/
│   ├── incomplete/
│   ├── contradictory/
│   ├── ai-assisted-estimation/
│   └── end-to-end/
│
├── evals/
│   ├── review/
│   ├── rewrite/
│   ├── estimate/
│   ├── workspace/
│   └── privacy/
│
└── workspaces/
    └── .gitkeep
```

`workspaces/` MUST быть полностью исключена из Git. Файл `.gitkeep` в production-варианте не требуется, если он мешает полному исключению директории.

---

# 10. Языковая политика

## 10.1. Язык skills

Следующие файлы MUST быть написаны на английском:

* `SKILL.md`;
* содержимое `references/`;
* шаблоны в `assets/`;
* имена полей YAML и JSON;
* описания схем;
* названия issue types;
* названия статусов;
* системные сообщения инструментов.

## 10.2. Язык пользовательских результатов

По умолчанию отчёты MUST формироваться на языке исходного документа.

Пользователь MAY задать:

```yaml
output_language: en
```

или:

```yaml
output_language: ru
```

## 10.3. Терминология

Установленные в проекте термины MUST сохраняться.

Если один объект называется в документе разными словами, review skill должен:

1. Зафиксировать терминологическую неоднозначность.
2. Предложить каноническое название.
3. Не заменять термины до запуска rewrite skill.

---

# 11. Структура project workspace

```text
workspaces/
└── customer-portal_private/
    ├── project.yaml
    ├── README.md
    │
    ├── source/
    │   └── original-specification.docx
    │
    ├── normalized/
    │   ├── specification.md
    │   ├── document-metadata.yaml
    │   ├── conversion-warnings.md
    │   └── media/
    │
    ├── context/
    │   ├── project-context.md
    │   ├── glossary.md
    │   ├── constraints.md
    │   ├── stakeholder-answers.md
    │   ├── clarification-register.yaml
    │   └── estimation-inputs.yaml
    │
    └── artifacts/
        ├── review/
        │   └── <run-id>/
        ├── rewrite/
        │   └── <run-id>/
        └── estimate/
            └── <run-id>/
```

## 11.1. Именование workspace

Название workspace MUST:

* использовать lowercase;
* использовать дефисы вместо пробелов;
* заканчиваться на `_private`;
* не содержать абсолютных путей;
* не содержать `..`;
* не содержать управляющих символов.

Пример:

```text
mobile-banking_private
```

## 11.2. Run ID

Рекомендуемый формат:

```text
20260715T143000Z-review
20260715T151500Z-rewrite
20260715T160000Z-estimate
```

Run ID MUST быть уникальным внутри проекта.

## 11.3. Отсутствие `latest`-копий

MVP SHOULD NOT создавать дублирующие каталоги `latest/`.

Актуальные результаты должны определяться через `project.yaml`. Это предотвращает расхождение между копиями.

---

# 12. Project manifest

Файл `project.yaml` является главным индексом workspace.

Пример:

```yaml
schema_version: "1.0"

project:
  id: "PRJ-0001"
  slug: "customer-portal"
  name: "Customer Portal"
  privacy: "private"
  source_language: "ru"
  output_language: "ru"

status:
  lifecycle: "estimated"
  specification_readiness: "ready_with_conditions"

source:
  original_file: "source/original-specification.docx"
  normalized_file: "normalized/specification.md"
  source_hash: "sha256:..."
  normalized_hash: "sha256:..."

latest_runs:
  review: "20260715T143000Z-review"
  rewrite: "20260715T151500Z-rewrite"
  estimate: "20260715T160000Z-estimate"

latest_artifacts:
  review_report: "artifacts/review/20260715T143000Z-review/review-report.md"
  issue_register: "artifacts/review/20260715T143000Z-review/issue-register.yaml"
  revised_specification: "artifacts/rewrite/20260715T151500Z-rewrite/revised-specification.md"
  estimate_report: "artifacts/estimate/20260715T160000Z-estimate/estimate-report.md"

open_items:
  critical_issues: 0
  high_issues: 3
  unanswered_blocking_questions: 0
  unresolved_assumptions: 4
```

## 12.1. Требования к manifest

Система MUST:

* обновлять manifest только после успешного завершения запуска;
* не указывать незавершённый run как актуальный;
* валидировать manifest по JSON Schema;
* использовать относительные пути;
* запрещать ссылки за пределы workspace;
* сохранять предыдущий manifest при ошибке.

---

# 13. Жизненный цикл проекта

Допустимые состояния:

```text
created
normalized
reviewed
awaiting_answers
ready_for_rewrite
rewritten
ready_for_estimation
estimated
archived
```

## 13.1. Переходы

```text
created
  ↓
normalized
  ↓
reviewed
  ├── awaiting_answers
  │       ↓
  │   reviewed
  ↓
ready_for_rewrite
  ↓
rewritten
  ↓
ready_for_estimation
  ↓
estimated
```

## 13.2. Правила

* Estimation MAY выполняться до rewrite, но результат должен иметь низкую или среднюю уверенность.
* Rewrite MUST NOT считаться завершённым при наличии unanswered blocking questions.
* Наличие Critical issue MUST блокировать статус `implementation_ready`.
* Повторный review не должен удалять предыдущие issue IDs без объяснения.

---

# 14. Нормализация исходного документа

## 14.1. Поддерживаемые форматы MVP

MUST:

* `.md`;
* `.docx`;
* текстовый `.pdf`.

SHOULD:

* Google Docs export;
* `.txt`;
* `.html`.

Сканированные PDF MAY быть отложены за пределы MVP либо обрабатываться с явным предупреждением о качестве OCR.

## 14.2. Результаты нормализации

```text
normalized/
├── specification.md
├── document-metadata.yaml
├── conversion-warnings.md
└── media/
```

## 14.3. Что должно сохраняться

Нормализатор MUST стараться сохранить:

* иерархию заголовков;
* нумерацию разделов;
* списки;
* таблицы;
* ссылки;
* подписи изображений;
* примечания;
* номера исходных страниц или секций;
* связь между изображением и разделом;
* исходный порядок блоков.

## 14.4. Source markers

Markdown SHOULD содержать технические комментарии:

```md
<!-- source-page: 7 -->
<!-- source-section: 4.2 -->
<!-- source-table: 3 -->
```

## 14.5. Conversion warnings

В `conversion-warnings.md` MUST фиксироваться:

* потерянные таблицы;
* изображения без распознанного текста;
* объединённые ячейки;
* нераспознанные формулы;
* отсутствующие шрифтовые признаки;
* возможное нарушение порядка;
* пропущенные комментарии;
* низкая уверенность OCR.

Review skill MUST NOT автоматически классифицировать conversion warning как недостаток ТЗ.

---

# 15. Skill `product-spec-review`

## 15.1. Назначение

Проверять ТЗ и формировать доказательный отчёт о его качестве без изменения исходного документа.

## 15.2. Trigger scope

Skill должен активироваться для запросов вида:

* review this specification;
* audit this PRD;
* find gaps in the requirements;
* check whether the specification is ready for development;
* identify contradictions;
* assess specification quality.

Skill MUST NOT активироваться для запроса, содержащего только просьбу переписать документ.

## 15.3. Обязательные входы

* `normalized/specification.md`;
* `normalized/document-metadata.yaml`.

## 15.4. Опциональные входы

* `normalized/conversion-warnings.md`;
* `context/project-context.md`;
* `context/glossary.md`;
* `context/constraints.md`;
* предыдущий issue register;
* профиль продукта.

## 15.5. Workflow

Skill MUST:

1. Проверить наличие и читаемость входов.
2. Определить тип документа.
3. Определить тип продукта.
4. Оценить достаточность контекста.
5. Выделить blocking questions.
6. Применить базовую rubric.
7. Подключить не более двух релевантных product profiles.
8. Найти проблемы и противоречия.
9. Проверить связанные разделы документа.
10. Исключить дублирующие findings.
11. Назначить severity и confidence.
12. Сформировать отчёт.
13. Сформировать структурированный issue register.
14. Выполнить self-check.
15. Не изменять исходный Markdown.

## 15.6. Выходы

```text
artifacts/review/<run-id>/
├── review-report.md
├── review-summary.yaml
├── issue-register.yaml
├── clarification-questions.md
└── run-metadata.yaml
```

## 15.7. Модель оценки

Категории:

1. Context and objectives.
2. Scope.
3. Stakeholders and actors.
4. Functional completeness.
5. Requirement clarity.
6. Verifiability.
7. Consistency.
8. Edge cases and failure behavior.
9. Non-functional requirements.
10. Delivery readiness.

Оценка каждой категории:

```text
0 — Absent
1 — Critically insufficient
2 — Weak
3 — Acceptable with gaps
4 — Good
5 — Implementation-ready
```

## 15.8. Readiness levels

```text
NOT_READY
DISCOVERY_REQUIRED
READY_WITH_CONDITIONS
IMPLEMENTATION_READY
```

### `NOT_READY`

Назначается, если присутствует хотя бы одно условие:

* открытая Critical problem;
* неизвестна основная цель продукта;
* не определён ключевой пользователь;
* отсутствует основной пользовательский сценарий;
* документ повреждён или не читается.

### `DISCOVERY_REQUIRED`

Назначается, если:

* нет Critical blockers;
* остаются существенные High issues;
* требуется продуктовая или техническая discovery-фаза;
* оценка возможна только с низкой уверенностью.

### `READY_WITH_CONDITIONS`

Назначается, если:

* ключевой scope понятен;
* нет Critical blockers;
* оставшиеся вопросы локальны;
* разработку можно начинать при явно зафиксированных assumptions.

### `IMPLEMENTATION_READY`

Назначается, если:

* нет открытых Critical и High blockers;
* ключевые требования проверяемы;
* роли, бизнес-правила и интеграции определены;
* основные ошибки и edge cases описаны;
* существенные NFR заданы;
* acceptance criteria позволяют проверить результат.

## 15.9. Формат finding

Каждый finding MUST включать:

```yaml
id: "ISSUE-014"
type: "undefined_business_rule"
severity: "high"
confidence: "high"

source:
  section: "5.4"
  heading: "Account deletion"
  excerpt: "The user can delete the account."

problem: >
  The specification does not define data retention,
  subscription handling, or recovery behavior.

impact:
  - backend
  - mobile
  - billing
  - compliance

resolution_strategy: "decision_required"

question_ids:
  - "Q-007"

status: "open"
```

## 15.10. Severity

```text
Critical
High
Medium
Low
```

Severity MUST отражать влияние на продукт и разработку, а не качество текста.

## 15.11. Confidence

```text
High
Medium
Low
```

Low confidence MUST использоваться, если:

* конвертация могла потерять часть информации;
* информация может находиться во внешнем документе;
* формулировка допускает несколько трактовок;
* вывод зависит от неуказанного контекста.

## 15.12. Запрещённое поведение

Skill MUST NOT:

* переписывать ТЗ;
* добавлять требования;
* выдавать style preferences за Critical issues;
* считать каждое отсутствие детали ошибкой;
* задавать вопрос, на который уже есть ответ;
* создавать дубликаты одной проблемы;
* утверждать, что requirement отсутствует, не проверив весь документ.

---

# 16. Issue taxonomy

MVP MUST поддерживать следующие типы:

```text
missing_requirement
ambiguous_requirement
conflicting_requirement
non_testable_requirement
missing_acceptance_criteria
undefined_actor
undefined_business_rule
missing_error_scenario
missing_edge_case
missing_non_functional_requirement
missing_dependency
missing_data_definition
missing_integration_contract
security_risk
privacy_risk
compliance_risk
delivery_risk
estimation_blocker
conversion_uncertainty
terminology_inconsistency
scope_uncertainty
```

Добавление нового типа MUST требовать обновления:

* taxonomy reference;
* JSON Schema;
* eval cases;
* changelog.

---

# 17. Clarification protocol

## 17.1. Уровни вопросов

### Blocking

Без ответа нельзя безопасно продолжить конкретный этап.

### Important non-blocking

Работа может продолжаться при явном assumption.

### Optional

Вопрос улучшает результат, но не влияет на корректность текущего этапа.

## 17.2. Ограничение количества

Skill SHOULD задавать не более 10 вопросов за одну итерацию.

Сначала MUST выводиться вопросы с максимальным влиянием на:

* бизнес-логику;
* архитектуру;
* безопасность;
* сроки;
* стоимость;
* compliance.

## 17.3. Формат вопроса

```md
### Q-007 — Account deletion retention

**Priority:** Blocking  
**Category:** Data lifecycle

**Question**

How long must user data be retained after account deletion?

**Why this matters**

The answer affects database cleanup, audit logs,
legal compliance, support procedures, and user messaging.

**Suggested options**

1. Immediate deletion
2. Soft deletion for a defined period
3. Retention according to an external policy
4. Other

**Affected requirements**

- REQ-ACCOUNT-014
- REQ-DATA-006
```

## 17.4. Хранение ответов

Ответы MUST храниться с ID исходного вопроса.

```md
## Q-007

**Status:** Answered  
**Answer:** User data is soft-deleted for 30 days.  
**Answered by:** Product owner  
**Answered at:** 2026-07-15T15:00:00Z
```

Skill MUST NOT повторно задавать answered question, если входные условия не изменились.

---

# 18. Skill `product-spec-rewrite`

## 18.1. Назначение

Создавать улучшенную версию ТЗ на основе:

* исходного документа;
* review findings;
* ответов заинтересованных лиц;
* подтверждённых ограничений;
* корпоративного шаблона.

## 18.2. Обязательные входы

* `normalized/specification.md`.

## 18.3. Рекомендуемые входы

* актуальный `issue-register.yaml`;
* `stakeholder-answers.md`;
* `clarification-register.yaml`;
* `constraints.md`;
* `glossary.md`.

## 18.4. Режимы

### `conservative`

Сохраняет структуру документа и исправляет только необходимые элементы.

### `structured`

Перестраивает документ по стандартному шаблону.

### `implementation-ready`

Расширяет подтверждённые требования до проверяемого уровня, включая acceptance criteria.

Режим по умолчанию:

```text
conservative
```

## 18.5. Resolution strategies

Каждая проблема MUST быть классифицирована.

### `EDITORIAL`

Может быть исправлена без продуктового решения:

* орфография;
* терминология;
* нумерация;
* дублирование;
* неоднозначное местоимение при очевидном контексте;
* нарушение структуры.

### `DERIVED`

Исправление однозначно следует из подтверждённых требований.

Такая правка MUST содержать ссылки на supporting requirements.

### `DECISION_REQUIRED`

Требуется решение человека:

* новое бизнес-правило;
* выбор роли;
* retention period;
* SLA;
* security policy;
* pricing logic;
* scope inclusion;
* юридическое условие.

Skill MUST NOT самостоятельно закрывать `DECISION_REQUIRED`.

## 18.6. Workflow

1. Проверить входы.
2. Определить актуальный review run.
3. Загрузить stakeholder answers.
4. Сопоставить issues и ответы.
5. Классифицировать resolution strategy.
6. Проверить blocking questions.
7. Применить editorial changes.
8. Применить подтверждённые решения.
9. Добавить acceptance criteria там, где они однозначно следуют из требований.
10. Сформировать revised specification.
11. Сформировать change log.
12. Сформировать assumption register.
13. Сформировать traceability map.
14. Выполнить проверку полноты.
15. Не изменять исходник.

## 18.7. Выходы

```text
artifacts/rewrite/<run-id>/
├── revised-specification.md
├── change-log.md
├── change-register.yaml
├── assumption-register.yaml
├── unresolved-questions.md
├── requirement-traceability.yaml
└── run-metadata.yaml
```

## 18.8. Change log

Каждая существенная правка MUST содержать:

* change ID;
* affected section;
* source issue ID;
* тип изменения;
* описание до;
* описание после;
* основание;
* confidence;
* статус подтверждения.

## 18.9. Assumptions

Assumption MUST включать:

```yaml
id: "ASSUMPTION-004"
statement: "Password reset links expire after 30 minutes."
reason: "The source document does not define expiration."
impact:
  - security
  - backend
  - email
status: "unconfirmed"
owner: "security_owner"
```

Неподтверждённое assumption MUST NOT выглядеть как окончательно согласованное требование.

## 18.10. Traceability

Каждое новое или изменённое requirement SHOULD быть связано с:

* source section;
* source requirement ID;
* issue ID;
* answer ID;
* assumption ID;
* change ID.

## 18.11. Запрещённое поведение

Skill MUST NOT:

* удалять требование без записи в change log;
* выбирать сторону противоречия без основания;
* превращать recommendation в обязательное requirement;
* добавлять юридические нормы без источника;
* менять scope проекта скрыто;
* скрывать unresolved questions;
* утверждать assumption как факт.

---

# 19. Skill `product-delivery-estimate`

## 19.1. Назначение

Формировать прозрачную сценарную оценку:

* effort;
* calendar duration;
* development cost;
* AI-assisted development impact;
* infrastructure cost;
* launch and stabilization effort;
* monthly maintenance cost.

## 19.2. Обязательные входы

* нормализованное или исправленное ТЗ;
* актуальный issue register;
* project context.

## 19.3. Дополнительные входы

* team profile;
* hourly or monthly rates;
* technology stack;
* infrastructure preferences;
* cloud provider;
* expected usage;
* SLA;
* AI usage profile;
* support model;
* delivery deadline.

## 19.4. Estimation readiness

Результат MUST иметь один статус:

```text
PRELIMINARY
LOW_CONFIDENCE
BLOCKED_BY_OPEN_DECISIONS
READY_FOR_PLANNING
```

### `PRELIMINARY`

Используется для ранней оценки концепции.

### `LOW_CONFIDENCE`

Используется при значительном числе assumptions.

### `BLOCKED_BY_OPEN_DECISIONS`

Используется, если неизвестны параметры, существенно влияющие на архитектуру или стоимость.

### `READY_FOR_PLANNING`

Используется, если scope достаточно стабилен для планирования.

## 19.5. Workflow

Skill MUST:

1. Определить версию ТЗ.
2. Проверить readiness review.
3. Найти estimation blockers.
4. Определить состав продукта.
5. Разбить проект на work items.
6. Связать work items с requirements.
7. Разделить работу по disciplines.
8. Выполнить baseline estimate.
9. Оценить AI applicability для каждого work item.
10. Рассчитать AI-assisted estimate.
11. Учесть review и rework overhead.
12. Построить зависимости.
13. Сформировать календарный диапазон.
14. Рассчитать стоимость при наличии ставок.
15. Сформировать инфраструктурные сценарии.
16. Сформировать support model.
17. Зафиксировать assumptions и exclusions.
18. Провести consistency check.

## 19.6. Work breakdown

Минимальные категории:

* discovery;
* product clarification;
* UX/UI;
* architecture;
* frontend;
* backend;
* mobile;
* integrations;
* data migration;
* quality assurance;
* security review;
* DevOps;
* documentation;
* deployment;
* stabilization;
* project management.

## 19.7. Three-point estimate

Каждый work item MUST содержать:

* optimistic;
* expected;
* conservative.

Для агрегированного ожидаемого значения MVP MAY использовать:

```text
Expected = (Optimistic + 4 × Most Likely + Conservative) / 6
```

Итоговый отчёт MUST сохранять исходный диапазон, а не показывать только одно число.

## 19.8. Work item format

```yaml
id: "WORK-014"
title: "Payment provider integration"

requirement_ids:
  - "REQ-PAY-001"
  - "REQ-PAY-002"

issue_ids:
  - "ISSUE-018"

disciplines:
  - backend
  - frontend
  - qa
  - devops

complexity: "high"

baseline_effort:
  optimistic_hours: 48
  expected_hours: 72
  conservative_hours: 112

ai_assisted_effort:
  optimistic_hours: 40
  expected_hours: 60
  conservative_hours: 96

confidence: "medium"

assumption_ids:
  - "ASSUMPTION-EST-007"

dependencies:
  - "WORK-009"
```

---

# 20. AI-assisted development model

## 20.1. Общий принцип

MVP MUST NOT применять единый процент ускорения ко всему проекту.

AI influence MUST рассчитываться на уровне work item.

## 20.2. Оцениваемые параметры

```yaml
ai_assistance:
  applicability: "high"
  expected_acceleration: "moderate"
  human_review_required: true
  review_overhead: "medium"
  rework_risk: "medium"
```

## 20.3. Типы задач с высокой применимостью AI

Примеры, а не гарантированные коэффициенты:

* boilerplate;
* стандартные CRUD-операции;
* типовые API clients;
* тестовые заготовки;
* документация;
* форматирование;
* статический анализ;
* локальный рефакторинг.

## 20.4. Типы задач с ограниченной применимостью AI

* неясная бизнес-логика;
* продуктовые решения;
* архитектурные компромиссы;
* threat modeling;
* security approval;
* compliance;
* production incident response;
* нестабильные внешние интеграции;
* legacy-системы без тестов.

## 20.5. Development profile

```yaml
development_model:
  mode: "ai_assisted"

  team:
    backend_developers: 1
    frontend_developers: 1
    qa_engineers: 0.5
    product_manager: 0.25

  experience_level: "senior"

  ai_usage:
    code_generation: true
    test_generation: true
    documentation: true
    code_review_support: true
    architecture_support: true
    autonomous_production_changes: false

  mandatory_human_review:
    - security
    - database_migrations
    - billing
    - authentication
    - production_deployment
```

## 20.6. Отчёт

Отчёт MUST отдельно показывать:

```text
Baseline effort
AI-assisted effort
Expected reduction
Review overhead
Unchanged work
Main uncertainty factors
```

---

# 21. Календарная оценка

Календарный срок MUST NOT рассчитываться простым делением часов на количество разработчиков.

Skill должен учитывать:

* зависимости;
* параллельность;
* специализацию;
* доступность команды;
* review bottlenecks;
* внешние согласования;
* QA;
* стабилизацию;
* deployment windows;
* резерв на rework.

Отчёт MUST показывать:

* effort range;
* calendar range;
* предполагаемый состав команды;
* critical path;
* основные ограничения параллельности.

---

# 22. Стоимость разработки

## 22.1. При наличии ставок

Стоимость MUST рассчитываться по discipline и сценарию.

```text
Cost = Effort × Rate
```

Необходимо учитывать:

* development;
* QA;
* design;
* DevOps;
* management;
* stabilization;
* contingency.

## 22.2. При отсутствии ставок

Skill MUST:

* показать effort;
* вывести формулу;
* запросить ставки либо предложить пользователю заполнить cost profile;
* не придумывать рыночную стоимость специалистов.

## 22.3. Валюта

Валюта MUST задаваться в `estimation-inputs.yaml`.

```yaml
currency: "USD"
```

Конвертация валют не входит в базовую оценку без отдельного актуального источника курса.

---

# 23. Инфраструктурная оценка

## 23.1. Сценарии

MVP MUST поддерживать:

```text
Prototype
Small production
Expected production
High-growth production
```

## 23.2. Категории расходов

* application compute;
* database;
* object storage;
* CDN;
* network traffic;
* background workers;
* cache;
* search;
* queue;
* monitoring;
* logging;
* backups;
* staging;
* secrets management;
* email;
* SMS;
* push notifications;
* third-party APIs;
* AI model APIs;
* disaster recovery.

## 23.3. Provider-neutral mode

По умолчанию оценка SHOULD быть provider-neutral.

Вместо неподтверждённых цен skill должен показывать:

* необходимый ресурс;
* предполагаемый объём;
* единицу расчёта;
* формулу;
* диапазон.

## 23.4. Provider-specific mode

Если пользователь предоставляет провайдера и актуальные цены, оценка MAY использовать их.

Каждая внешняя цена MUST содержать:

* источник;
* дату получения;
* регион;
* валюту;
* применённый тариф;
* assumptions.

## 23.5. AI usage cost

Для AI-продуктов MUST учитываться:

* количество запросов;
* средний размер входа;
* средний размер ответа;
* model class;
* retries;
* evaluation traffic;
* caching;
* fallback model;
* peak usage.

При отсутствии этих данных MUST быть сформирована параметрическая модель.

---

# 24. Стоимость поддержки

MVP MUST отдельно рассчитывать:

1. Базовую эксплуатацию.
2. Monitoring and incident response.
3. Bug-fix capacity.
4. Dependency and security updates.
5. Infrastructure administration.
6. Product improvement capacity.

## 24.1. Support levels

### `light`

* best-effort support;
* плановые обновления;
* отсутствие строгого SLA.

### `standard`

* регулярный monitoring;
* резерв на исправления;
* плановые releases;
* рабочее время поддержки.

### `critical`

* высокий SLA;
* on-call;
* расширенный monitoring;
* резервирование;
* disaster recovery;
* повышенная стоимость эксплуатации.

## 24.2. Отчёт

```text
Infrastructure cost
Third-party services
AI usage
Monitoring and backups
Engineering support
Incident reserve
Feature capacity
Estimated monthly total
Confidence
```

---

# 25. Выходы estimation skill

```text
artifacts/estimate/<run-id>/
├── estimate-report.md
├── estimate-summary.yaml
├── work-breakdown.yaml
├── estimate-assumptions.yaml
├── development-scenarios.yaml
├── infrastructure-scenarios.yaml
├── support-model.yaml
├── open-estimation-questions.md
└── run-metadata.yaml
```

## 25.1. Обязательные разделы отчёта

1. Executive summary.
2. Estimation readiness.
3. Scope basis.
4. Exclusions.
5. Development effort.
6. Calendar duration.
7. Team model.
8. AI-assisted impact.
9. Development cost.
10. Infrastructure scenarios.
11. Support cost.
12. Main risks.
13. Assumptions.
14. Open questions.
15. Confidence explanation.

---

# 26. Метаданные запуска

Каждый run MUST содержать:

```yaml
run_id: "20260715T160000Z-estimate"
project_id: "PRJ-0001"

skill:
  name: "product-delivery-estimate"
  version: "1.0.0"

methodology_version: "1.0"
schema_version: "1.0"

inputs:
  specification_hash: "sha256:..."
  issue_register_hash: "sha256:..."
  context_hash: "sha256:..."

generated_at: "2026-07-15T16:00:00Z"
status: "completed"
confidence: "medium"
```

---

# 27. Workspace tooling

Файловые операции MUST выполняться детерминированными инструментами, а не свободной импровизацией analytical skills.

## 27.1. Необходимые операции

### `workspace-init`

* валидирует название;
* создаёт workspace;
* добавляет `_private`;
* создаёт структуру директорий;
* создаёт начальный `project.yaml`.

### `document-normalize`

* принимает source file;
* создаёт canonical Markdown;
* создаёт metadata;
* создаёт conversion warnings.

### `run-create`

* создаёт уникальную директорию запуска;
* фиксирует версии входов;
* запрещает перезапись существующего run.

### `manifest-update`

* валидирует выходы;
* обновляет ссылки на актуальные артефакты;
* выполняет атомарную замену manifest.

### `workspace-validate`

* проверяет структуру;
* проверяет схемы;
* проверяет относительные пути;
* проверяет наличие `_private`;
* проверяет Git index;
* проверяет отсутствие выхода за пределы workspace.

### `artifact-archive`

* сохраняет завершённые результаты;
* запрещает изменение завершённого run без создания новой версии.

## 27.2. Ограничения

Tools MUST NOT:

* удалять исходный документ;
* перезаписывать completed run;
* писать за пределами workspace;
* следовать небезопасной symbolic link;
* использовать абсолютный путь из пользовательского документа;
* добавлять private files в Git.

---

# 28. Git и приватность

## 28.1. Базовая политика

Реальные рабочие проекты MUST NOT храниться в Git.

`workspaces/` MUST быть полностью исключена.

## 28.2. `_private`

Любой путь, содержащий `_private`, MUST считаться приватным.

Пример правил `.gitignore`:

```gitignore
workspaces/
**/*_private*/
**/*_private*
```

Конкретная реализация MAY использовать эквивалентные правила.

## 28.3. Многоуровневая защита

MVP MUST иметь:

1. `.gitignore`.
2. Локальную проверку перед commit.
3. CI-проверку tracked paths.
4. Проверку workspace naming.
5. Проверку отсутствия private artifacts в examples.
6. Проверку secrets.
7. Проверку того, что реальные исходные документы не находятся вне `workspaces/`.

## 28.4. CI policy

CI MUST завершаться ошибкой, если:

* tracked path содержит `_private`;
* tracked path находится внутри `workspaces/`;
* обнаружен оригинальный проектный документ вне разрешённых sanitized examples;
* schema содержит секрет;
* example не имеет отметки sanitization;
* workspace template содержит реальные данные.

## 28.5. Force-added files

Проверка MUST обнаруживать private file даже в случае его принудительного добавления в Git index.

## 28.6. Public examples

В Git MAY находиться только:

* синтетический пример;
* полностью обезличенный пример;
* пример с явным подтверждением публикации.

Каждый public example MUST содержать:

```yaml
data_classification: "public_synthetic"
sanitized: true
```

## 28.7. Secrets

В workspace и repository MUST NOT храниться:

* API keys;
* access tokens;
* passwords;
* private certificates;
* production connection strings.

Для ссылок на секреты должны использоваться placeholders.

---

# 29. Требования к `SKILL.md`

Каждый `SKILL.md` MUST содержать YAML frontmatter:

```yaml
---
name: product-spec-review
description: >
  Review product and software development specifications for completeness,
  clarity, consistency, testability, delivery readiness, and product risks.
  Use when the user asks to audit, evaluate, validate, or identify gaps in
  a product requirements document or technical specification.
  Do not use this skill to rewrite the specification.
---
```

Описание MUST:

* начинаться с основного назначения;
* содержать trigger cases;
* содержать границы использования;
* отличаться от описаний остальных skills;
* не быть перегруженным внутренними деталями.

`name` и `description` являются основными сигналами выбора skill, поэтому расплывчатые или пересекающиеся описания ухудшают маршрутизацию.

---

# 30. Product profiles

Review и estimate skills SHOULD подключать профиль продукта.

## 30.1. `web-application`

Проверяет:

* browser compatibility;
* responsive behavior;
* authentication;
* session lifecycle;
* accessibility;
* frontend errors;
* analytics;
* caching;
* SEO, если применимо.

## 30.2. `mobile-application`

Проверяет:

* operating systems;
* device compatibility;
* offline behavior;
* permissions;
* push notifications;
* deep links;
* lifecycle;
* store constraints;
* accessibility;
* biometric authentication.

## 30.3. `api-integration`

Проверяет:

* authentication;
* authorization;
* timeouts;
* retries;
* idempotency;
* rate limits;
* pagination;
* versioning;
* error contract;
* observability;
* backward compatibility.

## 30.4. `ai-product`

Проверяет:

* model scope;
* output quality criteria;
* hallucination handling;
* human review;
* prompt injection;
* prohibited outputs;
* data usage;
* fallback;
* latency;
* token cost;
* model updates;
* evaluation datasets.

## 30.5. Правила подключения

За один запуск SHOULD подключаться:

* один основной профиль;
* не более двух дополнительных профилей.

Skill MUST объяснять выбор профиля в run metadata.

---

# 31. Requirement IDs

Исправленное ТЗ SHOULD использовать стабильные IDs:

```text
REQ-AUTH-001
REQ-PAY-004
REQ-DATA-012
NFR-SEC-003
NFR-PERF-002
```

ID MUST:

* быть уникальным внутри проекта;
* не изменяться при редакционной правке;
* изменяться только при создании нового требования;
* сохраняться в traceability;
* не переиспользоваться после удаления requirement.

---

# 32. Validation и обработка ошибок

## 32.1. Input validation

Skill MUST прекратить выполнение с понятной ошибкой, если:

* отсутствует входной документ;
* Markdown пуст;
* manifest повреждён;
* schema version не поддерживается;
* путь выходит за workspace;
* входной файл изменился во время запуска.

## 32.2. Partial result

Если часть анализа выполнена, но запуск не завершён, результат MUST иметь статус:

```text
failed
partial
blocked
```

Такой run MUST NOT становиться актуальным в `project.yaml`.

## 32.3. Error report

Ошибка MUST включать:

* stage;
* input;
* причина;
* безопасное описание;
* рекомендуемое действие;
* информацию о сохранённых partial artifacts.

## 32.4. Idempotency

Повторный запуск с теми же входами MAY создавать новый run, но MUST давать логически эквивалентную структуру результатов.

---

# 33. Versioning

Раздельно версионируются:

* repository;
* skill;
* methodology;
* rubric;
* schema;
* template;
* product profile.

Пример:

```yaml
repository_version: "1.0.0"
skill_version: "1.2.0"
methodology_version: "1.1"
rubric_version: "2.0"
schema_version: "1.0"
template_version: "1.0"
```

## 33.1. Breaking changes

Изменение считается breaking, если:

* изменяется обязательное поле;
* удаляется тип issue;
* меняется семантика readiness;
* меняется структура workspace;
* меняются правила расчёта без обратной совместимости.

## 33.2. Migration

Для breaking schema change MUST быть предусмотрено:

* описание миграции;
* версия источника;
* версия назначения;
* проверка результата;
* возможность сохранить исходный файл.

---

# 34. Evals

Evals MUST разрабатываться одновременно со skills.

Официальные рекомендации по тестированию skills предполагают сочетание детерминированных проверок и содержательной rubric, а не только общего pass/fail.

## 34.1. Review evals

Минимальные случаи:

* качественное ТЗ;
* неполное ТЗ;
* противоречивое ТЗ;
* отсутствующие роли;
* отсутствующие acceptance criteria;
* требования без error behavior;
* данные находятся в другом разделе;
* необычное, но корректное решение;
* плохая конвертация;
* смешанный язык.

## 34.2. Rewrite evals

* сохранение подтверждённых требований;
* исправление терминологии;
* обработка противоречий;
* refusal to invent;
* unresolved question preservation;
* change log completeness;
* stable requirement IDs;
* traceability.

## 34.3. Estimate evals

* проект с полной информацией;
* проект без ставок;
* проект без нагрузки;
* AI-assisted solo developer;
* AI-assisted small team;
* external integration uncertainty;
* infrastructure-heavy product;
* AI API-heavy product;
* blocked estimate;
* comparison of baseline and AI-assisted estimates.

## 34.4. Privacy evals

* workspace исключён;
* nested `_private` directory исключена;
* force-added private path обнаружен;
* source document вне workspace обнаружен;
* secret обнаружен;
* sanitized example разрешён;
* path traversal заблокирован.

## 34.5. Оцениваемые свойства

```text
Did the skill detect the seeded issue?
Did it cite the correct section?
Did it assign a reasonable severity?
Did it avoid false positives?
Did it avoid repeating answered questions?
Did rewrite preserve confirmed requirements?
Did it label assumptions?
Did estimate expose its assumptions?
Did it avoid inventing rates?
Did privacy validation block tracked private files?
```

## 34.6. Минимальный объём MVP

MVP MUST содержать не менее:

* 15 review cases;
* 10 rewrite cases;
* 10 estimate cases;
* 8 privacy and workspace cases;
* 3 end-to-end cases.

---

# 35. Сквозные acceptance criteria

## AC-001 — Workspace initialization

При создании проекта система создаёт корректную директорию, заканчивающуюся на `_private`, и валидный `project.yaml`.

## AC-002 — Source preservation

После выполнения любого skill хеш исходного файла не изменяется.

## AC-003 — Markdown normalization

DOCX с заголовками, списками и таблицей преобразуется в читаемый Markdown, а потери фиксируются в warnings.

## AC-004 — Evidence-based review

Каждый High или Critical finding содержит source location либо явное объяснение отсутствия ссылки.

## AC-005 — No rewrite during review

Review run не изменяет и не создаёт revised specification.

## AC-006 — Blocking questions

При отсутствии критического бизнес-правила review создаёт blocking question и связывает его с finding.

## AC-007 — No duplicate questions

После сохранения ответа повторный run не задаёт тот же вопрос без изменения контекста.

## AC-008 — Safe rewrite

Rewrite не закрывает `DECISION_REQUIRED`, если отсутствует ответ.

## AC-009 — Change traceability

Каждое существенное изменение связано минимум с issue, answer, source requirement или assumption.

## AC-010 — Baseline estimate

Estimate содержит baseline effort range.

## AC-011 — AI-assisted estimate

Estimate отдельно показывает AI-assisted range и не применяет единый коэффициент ко всему проекту.

## AC-012 — Missing rates

Если ставки не предоставлены, skill показывает effort и формулу стоимости, но не придумывает денежную сумму.

## AC-013 — Infrastructure uncertainty

Если нагрузка неизвестна, skill создаёт сценарии или параметрическую модель.

## AC-014 — Support cost

Estimate включает инфраструктуру и engineering support как разные статьи.

## AC-015 — Version metadata

Каждый run содержит skill version, methodology version, schema version и input hashes.

## AC-016 — Run immutability

Повторный запуск не перезаписывает завершённый run.

## AC-017 — Private paths

CI отклоняет любой tracked path, содержащий `_private`.

## AC-018 — Workspaces

CI отклоняет любой tracked file внутри `workspaces/`.

## AC-019 — Manifest integrity

`project.yaml` указывает только на существующие и завершённые runs.

## AC-020 — End-to-end

Для тестового документа выполняется полный цикл:

```text
normalize → review → answers → rewrite → estimate
```

Все результаты проходят schema validation.

---

# 36. Нефункциональные требования

## 36.1. Portability

Skills SHOULD оставаться instruction-first и не зависеть от конкретной ОС без необходимости.

## 36.2. Determinism

Структура файлов, naming и schema validation MUST быть детерминированными.

## 36.3. Auditability

Любое существенное изменение или оценка MUST быть объяснимыми.

## 36.4. Maintainability

Методологии MUST быть вынесены из `SKILL.md` в references.

## 36.5. Extensibility

Добавление нового product profile не должно требовать изменения core workflow.

## 36.6. Privacy

Никакой private workspace не должен попадать в репозиторий при штатном или ошибочном сценарии.

## 36.7. Usability

Основной пользовательский сценарий не должен требовать ручного создания директорий и файлов.

## 36.8. Failure safety

Ошибка генерации не должна повреждать предыдущий результат или manifest.

---

# 37. Документация MVP

Репозиторий MUST содержать:

## `README.md`

* назначение;
* список skills;
* quick start;
* пример полного workflow;
* предупреждение о приватности;
* описание структуры.

## `AGENTS.md`

* общие правила работы AI в репозитории;
* запрет на запись private data вне workspace;
* порядок выбора skills;
* правила обновления manifest;
* правила запуска validation.

## `CONTRIBUTING.md`

* добавление нового skill;
* добавление issue type;
* изменение schema;
* создание eval;
* требования к pull request.

## `SECURITY.md`

* классификация данных;
* handling secrets;
* reporting;
* правила sanitized examples;
* запрет публикации client documents.

## `CHANGELOG.md`

Изменения skills, schemas и методологий.

---

# 38. Этапы реализации

## Stage 1 — Repository foundation

* создать структуру;
* настроить Git privacy;
* добавить базовые schemas;
* добавить workspace template;
* добавить validation requirements;
* создать документацию.

## Stage 2 — Review skill

* реализовать rubric;
* issue taxonomy;
* clarification protocol;
* review outputs;
* review evals.

## Stage 3 — Rewrite skill

* resolution strategies;
* change log;
* assumption register;
* traceability;
* rewrite evals.

## Stage 4 — Estimate skill

* work breakdown;
* baseline estimate;
* AI-assisted model;
* infrastructure scenarios;
* support model;
* estimate evals.

## Stage 5 — Workspace lifecycle

* initialization;
* normalization;
* run creation;
* manifest update;
* history;
* path validation.

## Stage 6 — End-to-end validation

* сквозные тесты;
* privacy tests;
* documentation review;
* sample project;
* MVP release.

---

# 39. Definition of Done для MVP 1.0

MVP считается завершённым, если:

1. В `.agents/skills/` находятся три независимых skills.
2. Каждый skill имеет корректный `SKILL.md`.
3. Skills имеют непересекающиеся trigger boundaries.
4. Создание workspace выполняется автоматически.
5. Workspace является private by default.
6. Поддерживается нормализация DOCX, Markdown и текстового PDF.
7. Review создаёт отчёт, issues и questions.
8. Rewrite создаёт новую спецификацию, change log и assumptions.
9. Estimate создаёт baseline и AI-assisted scenarios.
10. Estimate включает infrastructure и support.
11. Все structured artifacts проходят schema validation.
12. Все runs имеют metadata и hashes.
13. Исходный документ остаётся неизменным.
14. Completed runs не перезаписываются.
15. Git и CI блокируют private paths.
16. Реальные workspace не отслеживаются Git.
17. Есть минимум 43 специализированных eval cases и 3 end-to-end cases.
18. Все Critical acceptance criteria проходят.
19. README содержит полный пример использования.
20. Создан release tag `v1.0.0`.

---

# 40. Итоговый контракт системы

SpecViewer должен соблюдать следующий основной принцип:

> Review identifies evidence-based problems. Rewrite resolves only what can be resolved from confirmed information. Estimate exposes ranges, assumptions, uncertainty, and the real limits of AI-assisted development.

Конечным результатом работы над каждым проектом должен быть проверяемый набор связанных артефактов:

```text
Source document
    ↓
Canonical Markdown
    ↓
Review findings
    ↓
Clarifications and answers
    ↓
Revised specification
    ↓
Development and operations estimate
```

Все артефакты должны быть:

* приватными;
* версионированными;
* трассируемыми;
* воспроизводимыми;
* понятными человеку;
* доступными для машинной проверки.
