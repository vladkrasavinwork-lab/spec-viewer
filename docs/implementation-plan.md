# План реализации SpecViewer MVP 1.0

## 1. Цель и результат MVP

Реализовать репозиторий `spec-viewer` с тремя независимыми AI skills и детерминированными инструментами, которые обеспечивают полный приватный цикл обработки технического задания:

```text
source document
  → normalization
  → review
  → clarifications
  → rewrite
  → delivery estimate
```

Готовый MVP должен создавать версионированные, трассируемые и машинно-валидируемые артефакты, не изменять исходные документы и не допускать попадания приватных workspace в Git.

## 2. Принципы реализации

- Сначала фиксируются общие контракты: структура workspace, схемы, статусы, идентификаторы и метаданные запусков.
- Один skill решает одну задачу; review, rewrite и estimate не смешиваются.
- Файловые операции выполняются детерминированными инструментами, а содержательный анализ — skills.
- Structured artifacts проектируются до реализации соответствующего skill.
- Evals создаются одновременно с функциональностью, а не после неё.
- Каждый этап завершается проверяемым вертикальным результатом.
- Исходные документы и завершённые runs неизменяемы.

## 3. Этапы реализации

### Этап 0 — Уточнение контрактов MVP

**Цель:** устранить неоднозначности, которые могут привести к несовместимым schemas, tools и skills.

**Работы:**

1. Зафиксировать технологический стек детерминированных tools и тестов.
2. Утвердить точные YAML/JSON-форматы всех структурированных артефактов.
3. Определить правила генерации `project.id`, `run_id`, requirement IDs, issue IDs и hashes.
4. Зафиксировать матрицу переходов lifecycle и правила устаревания результатов.
5. Определить атомарную модель обновления `project.yaml` и поведение при partial/failed run.
6. Выбрать библиотеки нормализации DOCX и текстового PDF.
7. Зафиксировать CLI-контракты tools: аргументы, exit codes, stdout/stderr и формат ошибок.
8. Составить traceability matrix между требованиями ТЗ, acceptance criteria и eval cases.

**Результаты:**

- короткий architecture decision record по стеку;
- согласованные контракты CLI;
- черновики всех schemas;
- матрица `requirement/AC → implementation → test`.

**Критерий завершения:** структура данных и интерфейсы позволяют независимо реализовывать tools и три skills без изменения базовых контрактов.

---

### Этап 1 — Основа репозитория и защита приватности

**Цель:** создать безопасный каркас, на котором можно разрабатывать остальные части MVP.

**Работы:**

1. Создать структуру директорий из ТЗ: `.agents/skills`, `standards`, `profiles`, `schemas`, `templates`, `tools`, `examples`, `evals`.
2. Добавить `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`.
3. Настроить `.gitignore` для `workspaces/` и любых путей с `_private`.
4. Реализовать локальную и CI-проверку:
   - tracked paths внутри `workspaces/`;
   - путей с `_private` в Git index, включая force-added файлы;
   - исходных проектных документов вне разрешённых examples;
   - secrets;
   - признаков несanitized examples.
5. Создать синтетические fixtures для позитивных и негативных privacy-тестов.
6. Описать правила классификации данных и публикации examples.

**Результаты:**

- базовый репозиторий;
- privacy validation scripts;
- CI pipeline;
- начальный набор workspace/privacy evals.

**Проверки:** AC-017, AC-018 и соответствующие privacy cases.

**Критерий завершения:** CI блокирует приватные и небезопасные файлы, включая принудительно добавленные в index.

---

### Этап 2 — Общая модель данных, schemas и templates

**Цель:** создать единый машинно-проверяемый контракт для всех компонентов.

**Работы:**

1. Реализовать JSON Schemas для:
   - `project.yaml`;
   - document metadata;
   - review summary, issue и clarification registers;
   - change, assumption и traceability registers;
   - work breakdown, estimate summary и infrastructure scenarios;
   - run metadata.
2. Зафиксировать enums: lifecycle, readiness, severity, confidence, statuses, issue taxonomy и resolution strategies.
3. Добавить проверку относительных путей и запрет выхода за workspace.
4. Создать templates для workspace, review, rewrite и estimate artifacts.
5. Реализовать общий schema validator и понятный формат validation errors.
6. Добавить contract tests для валидных и невалидных fixtures.

**Результаты:** versioned schemas, templates и reusable validator.

**Проверки:** AC-015, AC-019; валидация всех примеров.

**Критерий завершения:** каждый запланированный structured artifact имеет schema, валидный fixture и набор негативных contract tests.

---

### Этап 3 — Workspace lifecycle и история запусков

**Цель:** реализовать безопасное управление проектом и неизменяемыми runs.

**Работы:**

1. Реализовать `workspace-init`:
   - безопасный slug;
   - обязательный суффикс `_private`;
   - структура директорий;
   - начальный валидный `project.yaml`.
2. Реализовать `run-create` с уникальным UTC `run_id`, фиксацией входных hashes и запретом перезаписи.
3. Реализовать `manifest-update` с предварительной валидацией и атомарной заменой.
4. Реализовать `workspace-validate`: структура, schemas, symlinks, path traversal, Git index и ссылки на artifacts.
5. Реализовать `artifact-archive` и правила неизменяемости completed runs.
6. Реализовать вычисление устаревших artifacts при изменении входов.
7. Покрыть lifecycle переходы и rollback при ошибке тестами.

**Результаты:** CLI-инструменты управления workspace и runs.

**Проверки:** AC-001, AC-002, AC-015, AC-016, AC-019.

**Критерий завершения:** можно создать workspace, открыть run, безопасно завершить его, атомарно обновить manifest и доказать, что старые результаты не изменились.

---

### Этап 4 — Нормализация документов

**Цель:** получить стабильный canonical Markdown для всех обязательных форматов MVP.

**Порядок реализации:** Markdown → DOCX → текстовый PDF.

**Работы:**

1. Реализовать общий pipeline импорта без изменения source file.
2. Для Markdown выполнить безопасное копирование/канонизацию и извлечение metadata.
3. Для DOCX сохранить заголовки, списки, таблицы, ссылки, изображения и исходный порядок.
4. Для текстового PDF извлечь текст, страницы и предупреждения о возможном нарушении структуры.
5. Добавить source markers и каталог `media/`.
6. Генерировать `document-metadata.yaml` и `conversion-warnings.md`.
7. Явно распознавать scanned PDF как unsupported/low-confidence сценарий, не выдавая OCR-результат за точный.
8. Проверять hash исходника до и после обработки.

**Результаты:** `document-normalize` и fixtures для трёх обязательных форматов.

**Проверки:** AC-002, AC-003; тесты таблиц, изображений, пустых/повреждённых документов и warnings.

**Критерий завершения:** обязательные форматы создают читаемый Markdown и metadata, а все известные потери отражаются в warnings.

---

### Этап 5 — Skill `product-spec-review`

**Цель:** находить доказательные проблемы ТЗ без переписывания документа.

**Работы:**

1. Создать компактный англоязычный `SKILL.md` с уникальными trigger boundaries.
2. Вынести в references:
   - review workflow и rubric;
   - readiness model;
   - issue taxonomy;
   - severity/confidence policy;
   - clarification protocol;
   - self-check и правила дедупликации.
3. Добавить базовые product profiles и правила выбора не более трёх профилей.
4. Создать templates пяти выходных artifacts.
5. Обеспечить evidence links, проверку всего документа до заявления об отсутствии требования и отделение conversion warnings от findings.
6. Реализовать связь `finding → question` и исключение уже отвеченных вопросов.
7. Создать не менее 15 review eval cases.

**Результаты:** review skill, references, assets и eval dataset.

**Проверки:** AC-004, AC-005, AC-006, AC-007.

**Критерий завершения:** skill стабильно создаёт валидные review artifacts, обнаруживает seeded issues, не меняет исходник и не генерирует дубликаты вопросов.

---

### Этап 6 — Skill `product-spec-rewrite`

**Цель:** создавать новую версию ТЗ только на основе подтверждённой информации и явно отмеченных assumptions.

**Работы:**

1. Создать `SKILL.md` с отдельными triggers и запретом выполнять review/estimate вместо rewrite.
2. Описать режимы `conservative`, `structured`, `implementation-ready`.
3. Реализовать классификацию `EDITORIAL`, `DERIVED`, `DECISION_REQUIRED`.
4. Блокировать завершение при unanswered blocking questions.
5. Реализовать стабильные requirement IDs и traceability между source, issue, answer, assumption и change.
6. Создать revised specification, change log/register, assumption register, unresolved questions и traceability map.
7. Добавить проверки сохранности подтверждённых требований и запрета скрытого изменения scope.
8. Создать не менее 10 rewrite eval cases.

**Результаты:** rewrite skill и полный набор rewrite artifacts.

**Проверки:** AC-008, AC-009, а также source immutability и schema validation.

**Критерий завершения:** каждое существенное изменение объяснимо и трассируемо, а нерешённые продуктовые решения не маскируются под требования.

---

### Этап 7 — Skill `product-delivery-estimate`

**Цель:** формировать прозрачную сценарную оценку разработки и эксплуатации.

**Работы:**

1. Создать `SKILL.md` и references по estimation methodology.
2. Реализовать estimation readiness и поиск blockers.
3. Формировать WBS по disciplines со связями на requirements/issues и зависимостями.
4. Рассчитывать three-point baseline effort с сохранением диапазонов.
5. Реализовать AI-assisted model на уровне каждого work item с review/rework overhead.
6. Строить календарный диапазон с dependencies, parallelism, availability, QA и stabilization.
7. Рассчитывать стоимость только при предоставленных rates; иначе выводить effort и формулу.
8. Создать provider-neutral infrastructure scenarios и параметрическую AI usage model.
9. Реализовать support levels и раздельный расчёт инфраструктуры и engineering support.
10. Создать не менее 10 estimate eval cases.

**Результаты:** estimate skill и девять предусмотренных artifacts.

**Проверки:** AC-010–AC-014.

**Критерий завершения:** baseline и AI-assisted диапазоны объяснимы, ставки не выдумываются, неизвестная нагрузка обрабатывается сценариями, assumptions и uncertainty видимы.

---

### Этап 8 — Сквозная интеграция и стабилизация

**Цель:** подтвердить полный пользовательский сценарий и готовность MVP к выпуску.

**Работы:**

1. Связать tools и skills через единый workspace lifecycle.
2. Реализовать минимум три end-to-end fixtures:
   - полный и качественный документ;
   - неполный документ с циклом вопросов и ответов;
   - противоречивый/низкокачественно конвертированный документ.
3. Проверить повторные runs, stale detection, manifest pointers и сохранность истории.
4. Выполнить полный набор schema, privacy, workspace и skill evals.
5. Проверить все AC-001–AC-020 и Definition of Done.
6. Подготовить sanitized end-to-end example и quick start.
7. Провести documentation review и устранить расхождения между кодом, schemas и методологиями.
8. Подготовить release notes и tag `v1.0.0` после прохождения quality gate.

**Результаты:** интегрированный MVP, документация, examples, отчёт о прохождении acceptance criteria.

**Проверки:** AC-020, все предыдущие AC и минимум 43 специализированных + 3 end-to-end eval cases.

**Критерий завершения:** полный цикл выполняется на чистом окружении, все structured artifacts валидны, приватность подтверждена, исходники и completed runs неизменны.

## 4. Зависимости и рекомендуемый порядок

```text
Этап 0
  ↓
Этап 1 ───────────────┐
  ↓                   │
Этап 2                │
  ↓                   │
Этап 3                │
  ↓                   │
Этап 4                │
  ↓                   │
Этап 5 → Этап 6 → Этап 7
  └───────────────────┘
              ↓
           Этап 8
```

После стабилизации schemas и workspace contracts части Stage 4–7 можно разрабатывать параллельно, но интеграция каждого skill должна проходить через общие validators и lifecycle tools.

## 5. Приоритеты внутри MVP

### P0 — блокирует основной сценарий

- Git/privacy protection;
- schemas и artifact contracts;
- workspace lifecycle;
- нормализация MD/DOCX/text PDF;
- три skills и их обязательные outputs;
- source/run immutability;
- manifest integrity;
- acceptance и end-to-end tests.

### P1 — необходимо для качественного MVP

- product/team/operations profiles;
- conversion source markers;
- stale artifact detection;
- rich traceability;
- CI secret scanning;
- полноценные sanitized examples и документация.

### P2 — допустимо перенести после 1.0 при нехватке ресурса

- Google Docs export, TXT и HTML;
- OCR scanned PDF;
- provider-specific pricing integrations;
- дополнительные profiles и расширенные migration tools.

## 6. Quality gates

Каждый этап принимается только при выполнении четырёх условий:

1. Все созданные structured artifacts проходят schema validation.
2. Позитивные и негативные тесты этапа проходят в CI.
3. Нет регрессии privacy checks и source/run immutability.
4. Документация и version metadata обновлены вместе с реализацией.

Перед релизом дополнительно требуется:

- пройти AC-001–AC-020;
- иметь минимум 15 review, 10 rewrite, 10 estimate, 8 privacy/workspace и 3 end-to-end cases;
- подтвердить отсутствие tracked files в `workspaces/` и путей с `_private`;
- проверить полный workflow на чистом checkout;
- убедиться, что trigger boundaries трёх skills не пересекаются;
- сформировать changelog и release tag `v1.0.0`.

## 7. Основные риски и меры снижения

| Риск | Влияние | Мера снижения |
|---|---|---|
| Schemas меняются после реализации skills | Массовая переделка artifacts и evals | Стабилизировать contracts на этапах 0–2, версионировать breaking changes |
| Потери при DOCX/PDF-конвертации | Ложные findings и неверная оценка | Source markers, conversion warnings, confidence policy, fixtures со сложной разметкой |
| Skills скрыто придумывают решения | Недостоверное ТЗ и оценка | Resolution strategies, assumption register, blocking protocol, refusal evals |
| Пересечение triggers skills | Запуск неверного workflow | Уникальные descriptions, routing evals, явные negative trigger cases |
| Приватные данные попадают в Git | Критический инцидент | `.gitignore`, index/CI checks, secret scan, synthetic-only examples |
| Оценка выглядит точнее, чем позволяет контекст | Ошибочные бюджетные решения | Диапазоны, readiness, confidence, assumptions, запрет выдумывать rates |
| Manifest указывает на незавершённый run | Повреждение истории проекта | Атомарное обновление только после validation и completed status |
| Большой объём evals откладывается до конца | Позднее обнаружение ошибок методологии | Создавать evals одновременно с каждым skill и tool |

## 8. Рекомендуемые контрольные точки

1. **Foundation ready:** приватность, CI и каркас репозитория работают.
2. **Contracts frozen for MVP:** schemas, templates и lifecycle согласованы.
3. **Normalization ready:** три обязательных формата поддержаны.
4. **Review vertical slice:** normalize → review → valid artifacts.
5. **Rewrite vertical slice:** answers → rewrite → traceability.
6. **Estimate vertical slice:** specification → WBS → baseline/AI/infrastructure/support.
7. **Release candidate:** три end-to-end сценария и все quality gates пройдены.
8. **MVP 1.0:** документация актуальна, acceptance report готов, создан `v1.0.0`.

## 9. Что сознательно не включается

План не включает production-code generation, Jira/CRM/accounting integrations, deployment, закупку облачных ресурсов, полноценный web UI, multi-agent orchestration, юридическую/security-сертификацию и получение актуальных цен без явно подключённого источника. Эти функции остаются за границами MVP согласно исходному ТЗ.
