# 해외 공인 스타트업 레이더 — 소프트웨어 설계

> 상태: **설계 검토 중 · 구현 전** · 2026-11-05
> 이 파일은 설계 원본이다. 화면용 페이지는 `portfolio/startup-radar-architecture.html`(ttomstudio.com)이고 내용은 같다.
> 새 비공개 레포 `startup-radar`로 옮겨 `docs/DESIGN.md`로 두고, 구현은 거기서 한다. **승인 전에는 코드를 작성하지 않는다.**

17개국의 투자 보도, 정부·액셀러레이터 공인 명단, 피칭·해커톤 수상작만 모아 한국에 없는데 될 만한 아이디어를 찾는다. 집의 Mac mini가 매주 월요일 새벽에 혼자 수집하고 로컬 LLM으로 거른다. 사람은 아침에 폰으로 시트를 열어 볼 만한 것에 체크만 한다.

---

## 0. 확정된 결정

| 항목 | 결정 |
|---|---|
| 실행 환경 | 집의 Mac mini **M1 · 16GB**, 하루 종일 켜져 있음. launchd가 자동으로 깨운다. **사람이 실행하는 단계는 없다** |
| 코드 위치 | 별도 **비공개** 레포 `startup-radar`. 사이트 레포에는 설계 페이지만 남긴다. DB·로그·키는 레포에도 넣지 않는다 |
| 처리 범위 | 최초 실행 때 최근 12개월치를 DB에 **적재만** 한다 (LLM 안 거침). 매주는 **최신 1주일치만** 거르고 시트에 올린다 |
| LLM | 로컬 Ollama가 기본 (비용 0). 품질이 모자란 단계만 Claude API로 바꿀 수 있게 설정으로 분리 |
| paywall=partial | 피드의 제목·요약만 보관하고 원문 페이지는 열지 않는다. DealStreetAsia(paywall=y)도 같은 방식의 예외로 허용 |
| signal | `funding_db`는 보존 (accredited와 같은 취급). `report`(KOTRA)는 수집하지 않고 수동 참고만 |
| KR 소스 | 한국 유사 서비스를 찾는 비교 인덱스로만 쓴다. 검토 화면에는 나오지 않는다 |
| funding_news 폐기 | 금액·라운드·투자사가 **모두** 확인되지 않을 때만 폐기 (하나라도 있으면 보존) |
| 해커톤 수상작 | 참가 등록자 수나 총상금이 임계값을 넘는 대회의 수상작만. 값은 설정 파일 |

---

## 1. 전체 아키텍처

```
 ┌ 인터넷 ───────────────────────────────────────────────────────────────┐
 │  GitHub 레포 (코드·sources.csv)          소스 사이트 90곳 (RSS·GNews·목록)   │
 └──────┬───────────────────────────────────────────▲────────────────────┘
        │ git pull (주 1회)                          │ robots 준수 · 3초 간격
 ┌ 집 Mac mini (M1 · 16GB · 상시 켜짐) — 전부 자동 ──┼────────────────────┐
 │  launchd ──▶ radar run ──────────────────────▶ 수집기 ──▶ SQLite (12개월 적재) │
 │  (매일 03:00·부팅 시)  (이번 주 사이클 필요할 때만)               │            │
 │                                                    KR 후보 ┆      ▼            │
 │  시트 게시 ◀── 판정 ◀── Ollama 로컬 LLM ◀──────────────── 규칙 필터            │
 │  (이번 주 덮어쓰기·☑ 회수) (보존·폐기·KR) (A 추출·분류, B 한국 비교) (중복·7일·투자 키워드) │
 └──────┬──────────────────────────────┬──────────────────────────────────┘
        ▼                              ┆ (선택)
 ┌ 보는 곳 ──────────────────────────────▼──────────────────────────────┐
 │  Google Sheets ◀──▶ 나 (폰, 월요일 아침 ☑·메모)     Claude API (선택)      │
 └──────────────────────────────────────────────────────────────────────┘
```

**원칙**
- **프로세스는 하나다.** `radar run`이라는 CLI가 전부 한다. 큐·워커·서버·컨테이너는 없다.
- **상태 기반으로 이어서 한다.** 각 단계는 자기 입력 상태인 행만 집어 처리한다. 정전이나 재시동으로 끊겨도 다음 실행이 이어서 한다.
- **바뀌는 건 설정 파일이다.** 소스가 수백 개로 늘어도 바뀌는 것은 `sources.csv`와 `adapters.yaml`이다.
- **의존성은 최소한으로 한다.** `requests`, `feedparser`, `PyYAML`, `beautifulsoup4`, `gspread` 다섯 개. Ollama는 HTTP로 부르므로 SDK가 필요 없다. Claude API를 켤 때만 `anthropic`을 추가한다. SQLite(FTS5 포함), robots.txt(`urllib.robotparser`), 로그, 메일(`smtplib`)은 표준 라이브러리로 처리한다. 헤드리스 브라우저는 넣지 않는다. JS 렌더링이 필요한 곳은 내장 JSON이나 공개 API를 쓰고, 그것도 없으면 `manual`로 돌린다. Python 3.11 이상.

### 레포 배치 (제안)

```
startup-radar/                (비공개)
├── docs/DESIGN.md            ← 이 파일
├── config/
│   ├── sources.csv           ← sources_seed_v2.csv + 열 3개 (§2.1)
│   ├── settings.yaml         ← 간격·임계값·모델·예산·시트 ID
│   ├── adapters.yaml         ← crawl/api 소스별 옵션
│   ├── patterns.yaml         ← 다국어 투자 키워드 (규칙 필터)
│   └── aliases.yaml          ← (선택) 회사명 별칭
├── radar/                    ← 파이썬 패키지 (§3)
├── prompts/                  ← stage_a.md, stage_b.md, annual_winners.md
├── tests/fixtures/           ← 어댑터별 실제 응답 샘플
└── data/                     ← .gitignore: radar.db, logs/, backups/, exports/
```

키 파일(Google 서비스 계정, 선택한 경우 Anthropic, Gmail 앱 비밀번호)은 Mac mini의 `~/.config/startup-radar/`에 권한 600으로 둔다. 레포에는 넣지 않는다.

### 세 가지 흐름

**매주 자동 · 월 03:00 ~ 07:00경**
1. launchd가 `radar run`을 깨운다. 이번 주 사이클이 이미 끝났으면 바로 종료한다.
2. 지난주 시트의 ☑·메모를 DB로 회수한다.
3. 대상 소스를 수집하고 중복을 지운 뒤 **최근 7일 것만** 남긴다.
4. 규칙으로 1차 폐기하고, 로컬 LLM이 추출·분류한다. 그다음 판정하고 한국 유사 서비스와 비교한다.
5. 시트의 '이번 주' 탭을 새로 쓰고, 맨 위에 실행 요약 한 줄을 남긴다.

**최초 1회 · 설치 날**
1. Mac mini에 레포를 clone하고 Ollama와 모델을 설치한 뒤 `radar doctor`로 점검한다 (Ollama 응답, 모델, 시트 접근, 키 파일 권한, 디스크).
2. `radar backfill`: 12개월치 공인 명단·수상작·피드 과거 페이지를 DB에 **적재만** 한다. LLM은 거치지 않는다. 몇 시간에서 하루 정도 걸리고, 끊겨도 이어서 한다.
3. KR 소스의 12개월치가 그대로 한국 비교 인덱스가 된다.
4. `radar install`로 launchd를 등록하면 그다음부터는 자동이다.

**사람이 하는 일**
1. 월요일 아침에 폰에서 시트의 '이번 주' 탭을 연다.
2. 볼 만한 회사에 ☑를 하고, 필요하면 메모를 남긴다.
3. 체크한 것은 다음 실행 때 '관심' 탭에 쌓인다.
4. 가끔 `sources.csv`에 한 줄을 넣고 push한다. 다음 사이클 시작 때 반영된다.

---

## 자동 실행 · Mac mini

설치가 끝나면 사람이 실행할 일은 없다. crontab 역할을 **launchd**가 맡는다. 매일 03:00과 부팅 직후에 `radar run`을 깨우고, 스크립트는 **"이번 주(월요일 시작) 사이클이 끝났는가"**만 본다. 평소에는 월요일 03:00에 한 번 돌고, 나머지 날은 확인만 하고 바로 끝난다. 정전이나 업데이트로 월요일에 꺼져 있었다면 켜진 직후나 다음 날 03:00에 밀린 사이클을 돈다.

| | launchd (채택) | cron |
|---|---|---|
| 놓친 실행 | 잠자기 중에 놓친 실행은 깨어날 때 1회. 부팅 직후 1회(`RunAtLoad`) 가능 | 놓치면 건너뜀 |
| macOS 권한 | 사용자 에이전트라 추가 권한 불필요 | 폴더에 따라 cron에 전체 디스크 접근 권한 필요 |
| 로그 | stdout/stderr 파일 지정 | 로컬 메일 (설정 필요) |
| 등록 | `radar install`이 plist를 만들고 등록 | `crontab -e` 한 줄 |

- 잠금 파일(`data/radar.lock`, PID 기록. 죽은 PID면 무시)로 같은 시각에 두 개가 겹쳐 돌지 않게 한다. 실행은 `caffeinate -i radar run`으로 감싼다.
- 주간 사이클을 시작할 때 `git pull --ff-only`로 코드와 설정을 갱신한다. 실패하면 현재 버전으로 계속 돌고 로그를 남긴다.
- 사이클 완료 표시(`runs.cycle_done`)는 시트 게시까지 끝나야 남긴다. 중간에 끊기면 다음 깨움이 남은 단계부터 이어서 한다.

**Mac mini 준비 체크리스트**

| 항목 | 내용 |
|---|---|
| 잠자기 끄기 | 시스템 설정 → 에너지 → 자동 잠자기 방지 (`pmset sleep 0`). 디스플레이만 꺼지는 것은 상관없다 |
| 정전 후 자동 시동 | "정전 후 자동으로 시동" (`pmset autorestart 1`) |
| 자동 로그인 | launchd 사용자 에이전트와 Ollama는 로그인 세션 안에서 돈다. FileVault가 켜져 있으면 자동 로그인이 안 되므로 재시동 후 한 번 직접 로그인해야 한다 (열린 질문 1) |
| 원격 로그인 (SSH) | 노트북에서 `ssh mini radar status`로 상태 확인·수정 |
| Ollama | `brew install ollama` → `brew services start ollama`. 모델 하나만, 동시 처리 1(`OLLAMA_NUM_PARALLEL=1`), 컨텍스트 8K |
| OS 업데이트 | 보안 업데이트만 자동. 재시동이 필요한 업데이트는 월요일 새벽을 피한다 |
| 시간대 | Asia/Seoul |

---

## 2. 데이터 모델

### 2.1 소스 설정 `config/sources.csv`

기존 12개 열(country, region, name, url, feed_url, fetch_type, signal, lang, tier, paywall, active, notes)은 그대로 두고 3개만 더한다.

| 추가 열 | 의미 |
|---|---|
| `source_id` | 고정 키 (예: `crunchbase-news`, `gnews-ko-funding`). DB가 이 값으로 소스를 식별하므로 이름을 바꿔도 이력이 유지된다 |
| `scope` | 비우면 paywall에서 정해진다: `n`→`full`, `partial`→`feed_only`, `y`→`skip`. 예외는 직접 적는다 (DealStreetAsia = `feed_only`) |
| `adapter` | crawl·api 소스의 어댑터 이름 (`devpost`, `list_diff_html` …). rss·gnews는 비워 둔다 |

**수집 대상** = `active=y` · `tier ≤ max_tier`(처음은 1) · `fetch_type ≠ manual` · `signal ≠ report` · `scope ≠ skip` · 자동 비활성 아님 · (rss/gnews라면) 피드 검증 통과.
`feed_only`인데 `feed_url`이 없는 소스(더브이씨, STARTUP DB News, Fortune Term Sheet)는 수집할 길이 없어 제외되고 로그에 남는다.

### 2.2 테이블

| 테이블 | 한 행 = | 주요 컬럼 |
|---|---|---|
| `sources` | 소스 1곳 | CSV 열 전부 + `feed_status`(unverified/ok/redirected/stale/not_feed/empty/http_error/robots_blocked), `feed_final_url`, `feed_checked_at`, `etag`, `last_modified`, `consecutive_failures`, `zero_item_runs`, `last_success_at`, `last_error`, `disabled_at`, `disabled_reason`, `next_probe_at`, `removed`. CSV에서 지운 행도 기록은 남긴다 |
| `runs` | 실행 1회 | `started_at`, `ended_at`, `trigger`(launchd/manual), `cycle_week`(2026-W46), `cycle_done`, `stats_json` |
| `fetch_log` | 소스 × 실행 | `outcome`(ok/not_modified/http_error/timeout/parse_error/robots_blocked/skipped), `http_status`, `n_found`, `n_new`, `duration_ms`, `error` |
| `crawl_state` | 어댑터 커서 | `source_id`, `key`, `value_json`, `updated_at`. 수상 발표를 기다리는 해커톤 목록, 연간 결과 페이지의 해시, 적재 진행 위치 등 |
| `items` | 원문 1건 | `source_id`, **`signal`(수집 시점 복사본)**, `signal_detail`(YC W26, Devpost 1st Place …), `country`, `lang`, `url`, `url_norm`, `url_hash`(유일), `external_id`(유일: source_id+external_id), `title`, `title_key`, `summary`(2,000자), `body`(scope=full만, 6,000자), `published_at`, `event_at`, `fetched_at`(수집일), `extra_json`, `status`, `dup_of`, `llm_attempts` |
| `items_fts` | FTS5 색인 | `title` + `summary` 전문 검색 (`unicode61`). KR 소스 행이 곧 한국 비교 인덱스다. 과거 언급 조회에도 쓴다 |
| `mentions` | 원문 안의 회사 1곳 (판정 단위) | `item_id`, `company_id`, `company_name`, `company_name_native`, `website`, `country`, `one_liner_ko`, `target_customer_ko`, `customer_type`, `category`, `round`, `amount`, `currency`, `amount_usd`, `investors_json`, `award_prize`, `is_winner`, `evidence_quote`, `keywords_ko`, `decision`, `discard_reason`, `kr_similar`, `kr_matches_json`, `kr_reason`, `backend`, `model`, `prompt_ver` |
| `companies` | 묶인 회사 1곳 (검토 단위) | `display_name`, `name_key`, `domain`, `country`, `first_seen_at`, `last_seen_at`, `signals`(집합 캐시) |
| `reviews` | 사람의 표시 | `company_id`, `interesting`(☑), `note`, `reviewed_week`, `synced_at` |

- 원문 1건에서 회사가 여러 곳 나올 수 있다 (주간 라운드업 기사, 수상자 목록). 그래서 items와 mentions를 나눴다.
- 한국 비교 인덱스를 따로 만들지 않는다. KR 원문은 이미 한국어라 LLM 없이 전문 검색하면 되고, 12개월 적재분이 그대로 인덱스가 된다. 조사가 붙은 단어(배달앱을)는 접두 검색(`배달*`)으로 잡는다. trigram은 2음절 검색어를 못 찾아서 쓰지 않는다.

### 2.3 signal 보관 방식 (3단)
1. **items.signal**: 수집 시점의 소스 signal을 복사해 둔다. 나중에 CSV를 고쳐도 과거 근거는 그대로 남는다.
2. **mentions**: `evidence_quote`(원문 그대로 인용한 구절)와 투자·수상 필드가 그 signal이 실제로 확인됐다는 기록이다. 폐기 규칙은 이 필드만 보고 코드가 판정한다.
3. **companies.signals**: 회사에 붙은 모든 signal의 집합. 시트에는 `accredited: YC W26 · funding_news: Series A $12M (Crunchbase News)`처럼 근거가 쌓여 보인다.

---

## 3. 모듈과 책임

| 모듈 | 책임 |
|---|---|
| `cli` | `run` · `backfill` · `install` · `doctor` · `verify` · `status` · `export` · `rejudge` · `sheet init` · `sources list/enable/add-gnews` |
| `config` | CSV·YAML 로드와 검사 (필수 열, 중복 source_id, 허용값). 잘못된 행은 그 행만 건너뛰고 경고 |
| `db` | 스키마·마이그레이션(`PRAGMA user_version`), 주간 백업, 쿼리 |
| `http` | **유일한 네트워크 출구.** UA, 호스트별 간격, robots.txt, 타임아웃·재시도, 조건부 GET, feed_only 원문 차단, 응답 5MB 상한 |
| `normalize` | URL 정규화, 제목 키, 회사명 키, 등록 도메인, 통화 → USD 환산 |
| `fetchers` | `rss` · `gnews` · `api`(범용 JSON) · `crawl/`(어댑터 등록부 + 범용 2종 + 전용) |
| `verify` | 피드 검증·자동 탐색, 보고서 |
| `window` · `dedup` | 최근 7일 창 판정(`archived`), 기사 단위·회사 단위 중복 병합 |
| `prefilter` | LLM 전 규칙 폐기 (`patterns.yaml`) |
| `llm` | 백엔드 인터페이스 하나 + 구현체 `ollama` · `anthropic` · `none`. 프롬프트 로드, JSON 스키마, 재시도 |
| `judge` | 추출 결과 → 보존·폐기·KR. 규칙은 여기 한 곳에만 있다. LLM 없이 다시 돌릴 수 있다 (`rejudge`) |
| `publish` | 시트 게시·☑ 회수, 소스 상태 탭, 폐기 샘플 탭 |
| `notify` | 시트 요약 줄, (선택) 실패 시 메일 |

규칙: 네트워크는 `http`만, 판정 규칙은 `judge`에만, 모델 호출은 `llm`만 한다.

---

## 4. 수집 → 중복제거 → 거르기 → 반영

```
items.status
  (수집) ─▶ new ─┬─▶ dup           다른 소스에 같은 기사 → dup_of 기록, 끝
                ├─▶ archived      최근 7일 창 밖 (최초 12개월 적재분, 놓친 주) → 검색용으로만 보관
                ├─▶ prefiltered   규칙으로 확정 폐기 (투자 정보 0개 · 해커톤 규모 미달) → 끝
                └─▶ llm_pending ─▶ extracted ─▶ mentions 생성     (3회 실패 시 llm_error)

mentions.decision
  ─┬─▶ kr_index    회사 국가 = KR → 검토에서 제외
   ├─▶ discarded   사유 코드와 함께 보관 (화면에서만 빠짐)
   └─▶ kept ─▶ 한국 비교(B단계) ─▶ 시트 '이번 주'
```

### 최근 1주일 창
- 매주 다루는 것은 `event_at`이 최근 7일 안에 든 항목뿐이다.
- `event_at`은 뉴스라면 게시일이고, 목록·수상작처럼 날짜가 없거나 늦게 발표되는 항목은 **처음 본 날**이다 (예: 3주 전에 끝난 해커톤의 수상작이 이번 주에 공개되면 이번 주 항목).
- 사이클을 몇 주 놓쳤어도 처리하는 건 최신 7일치뿐이다. 나머지는 `archived`로 남아 검색으로만 볼 수 있다.
- `radar backfill`로 들어온 12개월치는 모두 `archived`다.

### 중복 제거
- **기사 단위 (LLM 전)**
  - 정규화한 URL이 같으면 중복이다. 정규화는 다음 순서로 한다: 소문자화, `http`→`https`, `www.`·`m.`·AMP 경로 제거, `utm_*`·`fbclid`·`gclid`·`mc_cid`·`ref`·`ref_src` 제거, 남은 쿼리 정렬, 프래그먼트와 끝의 `/` 제거.
  - 정규화한 제목이 같고 게시일이 3일 안이어도 중복이다 (Google News가 다른 매체 기사를 다시 실어 오는 경우).
  - 대표 기사는 tier가 높고 본문이 있는 쪽으로 고른다.
- **회사 단위 (LLM 후)**
  - 사이트의 등록 도메인이 같으면 같은 회사다 (`www.`·`app.` 제거).
  - 도메인이 없으면 회사명 키로 비교한다. 회사명 키는 NFKC → 소문자 → 법인 접미사 제거(Inc, Ltd, LLC, GmbH, AG, SAS, SA, BV, Oy, AB, AS, Pte, Pty, KK, 株式会社, 合同会社, 有限公司, 股份有限公司, (주), 주식회사 …) → 공백·구두점 제거로 만든다.
  - 이름이 같아도 양쪽 도메인이 서로 다르면 다른 회사로 본다. 잘못 묶인 것은 `aliases.yaml`에 한 줄로 바로잡는다.

### 판정 규칙 (`judge`, 위에서부터 처음 걸리는 규칙 적용)

| # | 조건 | 결과 · 사유 코드 |
|---|---|---|
| 0 | (LLM 전) funding_news인데 원문에 금액·라운드·투자사 패턴이 하나도 없다 | `prefiltered / no_funding_detail` |
| 1 | 회사명이 없다 (시장 동향, 칼럼, 인사, 행사 공지) | `discarded / no_company` |
| 2 | 회사명이 원문에 없다 (모델이 지어낸 이름 차단) | `discarded / name_not_in_text` |
| 3 | `evidence_quote`가 원문에 그대로 없다 (공백 정규화 후 부분 문자열 검사) | `discarded / evidence_mismatch` |
| 4 | 회사 국가 = KR, 또는 KR 소스 | `kr_index` |
| 5 | funding_news인데 투자 사건이 아니다 | `discarded / not_funding_event` |
| 6 | funding_news인데 라운드·금액·투자사가 모두 null이다 | `discarded / no_funding_detail` |
| 7 | pitch_winner·hackathon_winner인데 `is_winner ≠ true`다 | `discarded / not_winner` |
| 8 | 그 외 (accredited, funding_db 포함) | `kept` |

- 규칙 0은 확실한 것만 미리 버리는 보수적인 필터다. 패턴이 하나라도 걸리면 LLM으로 넘긴다.
- 규칙 0의 패턴(`patterns.yaml`):
  - 금액: `$ € £ ¥ ₹ S$`, `million/billion/M/B`, `억 원`·`만 달러`, `億円`·`万円`, `亿元`·`万元`, `Mio.`, `millions d'euros` …
  - 라운드: `pre-seed`, `seed`, `Series [A-H]`, `시드`·`시리즈 [A-Z]`, `シード`·`シリーズ[A-Z]`, `天使轮`·`Pre-A`·`[A-F]轮`, `Finanzierungsrunde`, `levée de fonds`, `tour de table` …
  - 투자사: `led by`, `backed by`, `participation from`, `주도`·`참여`, `主導`·`引受`, `领投`·`跟投`, `angeführt von`, `mené par` …
- 규칙 2·3은 작은 로컬 모델이 지어낸 내용을 코드로 막는 장치다.
- **폐기는 삭제가 아니다.** 규칙을 바꾸면 `radar rejudge`가 저장된 추출값으로 LLM 없이 다시 판정한다.

---

## 5. fetch_type별 수집 방식

### 공통 · 수집 예절 (`http`)

| 항목 | 방침 |
|---|---|
| User-Agent | `StartupRadar/0.1 (personal research; +https://ttomstudio.com/portfolio/startup-radar-architecture.html)`. 연락처로 이메일 대신 설계 페이지를 적는다 |
| robots.txt | 호스트별 24시간 캐시. 4xx면 전부 허용으로 본다. 5xx나 타임아웃이면 이번 실행에서 그 호스트를 건너뛴다. 금지된 경로는 요청하지 않고 `robots_blocked`로 기록한다. `Crawl-delay`를 따른다 |
| 간격 | 같은 호스트는 최소 3초, 크롤링 어댑터는 5초. 다른 호스트끼리는 기다리지 않는다 |
| 타임아웃·재시도 | 연결 10초, 읽기 20초. 5xx·타임아웃은 최대 2회 지수 백오프로 재시도. 429는 `Retry-After`를 따르되 60초가 넘으면 이번 실행에서 포기 |
| 조건부 GET | 피드는 ETag와 If-Modified-Since. 304는 성공으로 친다 |
| 유료 | `skip`이면 요청하지 않는다. `feed_only`면 피드 URL이 아닌 요청을 `http`가 직접 거부하므로 어댑터가 실수해도 원문이 열리지 않는다 |

소스가 수백 개가 돼도 순차 처리로 충분하다 (다른 호스트끼리는 대기가 없다). 필요해지면 호스트별 간격을 지키는 스레드 풀(`max_workers`, 기본 1)을 켠다.

| fetch_type | 방법 |
|---|---|
| `rss` | 조건부 GET → `feedparser`. link→url, guid→external_id, summary→HTML 제거 2,000자, published→게시일. 엔트리 0개나 파싱 실패는 실패로 센다. 본문 보강은 기본으로 꺼 둔다. **12개월 적재**: WordPress 피드는 `?paged=2,3…`을 지원하는 곳이 많아, 적재 때 12개월 전에 닿거나 실패할 때까지 페이지를 넘긴다. 지원하지 않는 피드는 지금 보이는 만큼만 적재한다 |
| `gnews` | rss와 같다. 제목 끝의 ` - 매체명`을 떼어 출처로 두고 `<source>` 요소도 쓴다. 링크는 Google 리다이렉트라 풀지 않고, 중복은 제목 키로 판정한다. 원문은 열지 않는다. **복제**는 CSV에 한 줄이면 된다. `radar sources add-gnews --country DE --lang de --q "Startup Finanzierungsrunde"`가 URL을 조립해 행을 넣어 준다. 12개월 적재는 할 수 없다 (최근 약 100건만 나옴) |
| `api` | 범용 JSON 어댑터. `adapters.yaml`에 URL 템플릿, 결과 배열 경로, 필드 매핑, 페이지 넘김(page/offset/cursor), 최대 페이지를 적으면 코드 없이 추가된다. 로그인이나 키가 필요하면 `manual` |
| `crawl` | 어댑터 세 종류 (아래). 사이트 구조가 바뀌면 오류 없이 0건이 나오므로, 전에 1건 이상이던 소스가 2회 연속 0건이면 실패로 센다. 어댑터마다 실제 응답 1개를 `tests/fixtures/`에 저장해 두고 "몇 건이 나와야 한다"를 테스트한다 |

### crawl 어댑터

| 어댑터 | 쓰는 곳 | 동작 |
|---|---|---|
| `list_diff_html` (범용) | J-Startup, French Tech, EIC, Startup Estonia, TIPS, Startup India, Station F, Techstars, 500, Antler, Sequoia, a16z, MassChallenge, Venture Kick | 목록 페이지(필요하면 페이지 넘김)를 YAML의 CSS 셀렉터로 읽어 이름·링크·설명·(선정 연도)를 뽑는다. **전에 본 적 없는 항목만** 새 item이 된다. 첫 적재분은 모두 `archived`다 |
| `annual_winners_page` (범용) | 연 1회 피칭대회 8곳 (Startup World Cup, CES Innovation Awards, Hult Prize, SXSW Pitch, Web Summit PITCH, Slush 100, SusHi Tech, IVS LaunchPad) | YAML에 연도별 결과 페이지 URL을 적는다. **월 1회** 확인하고, 본문 해시가 바뀌면 페이지 텍스트에서 수상 기업만 LLM으로 뽑는다 |
| 전용 | YC Companies, YC Launches, Devpost, PR TIMES 資金調達, Startup Nation Finder (+ tier 2 해커톤) | 사이트가 화면에 쓰는 공개 데이터(내장 JSON 등)를 읽는다. 데이터 위치, robots, 로그인 벽 여부는 구현 전 **스파이크 1일**에서 확인한다. 안 되는 곳은 `manual`로 돌리고 기록한다 |

전용 어댑터 메모 (스파이크에서 확인):
- **YC Companies**: 디렉터리가 쓰는 공개 데이터에서 배치 필드로 최근 배치만 읽는다. 안 되면 배치별 공개 목록을 `list_diff_html`로 읽는다.
- **YC Launches**: 런칭 목록에서 새 글만 받는다. 회사는 Companies 쪽과 도메인으로 병합한다.
- **PR TIMES 資金調達**: 사이트 내 검색 결과(`資金調達`)의 최신 목록만 읽는다. 보도자료 본문은 공개라 full이다. 회사·카테고리 RSS가 있는지도 확인한다.
- **Startup Nation Finder**: 공개 회사 페이지의 펀딩 라운드를 읽는다. 로그인 벽이 있으면 `manual`로 돌린다.

---

## 6. 수상작만 골라내기

원칙: **구조로 거를 수 있으면 수집 단계에서 거른다** (LLM 비용·시간 0). 구조로 안 되면 LLM의 `is_winner`와 판정 규칙 7로 거른다. 일반 출품작은 아예 저장하지 않는다.

```yaml
hackathon:              # settings.yaml — 둘 중 하나만 넘으면 통과
  min_registrants: 200
  min_prize_usd: 5000
  winners_wait_days: 45  # 마감 후 수상 발표를 기다리는 기간
```

| 소스 | tier | 대회 고르기 | 수상 판별 |
|---|---|---|---|
| Devpost | 1 | 사이트가 쓰는 해커톤 목록 데이터에서 종료된 대회를 읽고, 참가자 수·상금으로 임계값 검사 (필드 존재는 스파이크로 확인) | 대회별 `/project-gallery`에서 **Winner 배지**가 붙은 카드만. 프로젝트 페이지(`/software/<slug>`)에서 설명과 받은 상 이름을 `signal_detail`로. 마감 직후에는 배지가 없으므로 `crawl_state` 대기 목록에 넣고 45일 동안 매주 다시 본다. 적재 때는 갤러리 카드(이름·태그라인·배지)만 읽고, 상세 페이지는 그 주에 처리할 때 연다 |
| Devfolio | 2 | 해커톤 목록 (내장 데이터) | prize 표시가 있는 프로젝트만 |
| ETHGlobal | 2 | 이벤트별 쇼케이스 | **Finalist만** (`prize_filter: finalist_only`). 이벤트마다 스폰서 상이 수십 개라 전부 받으면 양이 넘친다 |
| lablab.ai | 2 | 이벤트 목록 | 이벤트 페이지의 Winners 영역 제출물만 |
| DoraHacks | 3 | 해커톤 목록 | Results 탭의 수상 BUIDL만 |
| Mashup Awards | 3 | connpass 결과 공지 | `annual_winners_page` 방식으로 LLM 추출 |
| TC Battlefield | 1 | 태그 RSS (참가사 소개 기사도 섞임) | LLM `is_winner` + 규칙 7. 인용 구절에 수상 사실이 있어야 한다 |
| 연간 피칭대회 8곳 | 2–3 | `annual_winners_page` | 결과 페이지에서 수상자만. CES는 Best of Innovation과 Honoree 모두 수상으로 보되 `award_prize`로 구분 |

해커톤 수상팀은 아직 회사가 아닌 경우가 많다. 프로젝트명을 회사명 자리에 넣고 `extra_json.is_project=true`로 표시해서 시트에서 걸러 볼 수 있게 한다.

---

## 7. feed_url 검증 절차

`radar verify [--all | --id …] [--apply]`: 새로 추가된(`unverified`) 소스는 매 실행에서, 전체는 월 1회 자동으로 검증한다.

| 단계 | 검사 | 실패 시 상태 |
|---|---|---|
| 1 | robots.txt가 피드 경로를 허용하는가 | `robots_blocked` |
| 2 | 리다이렉트를 따라가 200이 오는가. 최종 URL을 기록한다 | `http_error` / `redirected` |
| 3 | RSS·Atom으로 파싱되는가 (200으로 HTML 페이지가 오는 경우를 거른다) | `not_feed` |
| 4 | 엔트리가 1개 이상인가 | `empty` |
| 5 | 최신 엔트리가 30일 안인가 | `stale` (수집은 함) |
| 6 | 참고: 최근 20개 중 투자 키워드 비율, feed_only 소스의 요약 길이, WordPress 페이지 넘김 지원 여부 | 보고서에만 표시 |

- **피드 URL이 틀렸거나 비어 있을 때**: 홈페이지의 `<link rel="alternate" type="application/rss+xml|atom+xml">`를 먼저 찾는다. 없으면 `/feed`, `/feed/`, `/rss`, `/rss.xml`, `/atom.xml`, `/index.xml` 순서로 시도해 1~5단계를 통과하는 후보를 찾는다.
- **CSV를 몰래 고치지 않는다.** 결과는 `data/verify_report.csv`로 낸다. `--apply`를 줄 때만 후보를 CSV `feed_url`에 쓰고, 원본은 `.bak`으로 남긴다.
- 수집 대상은 `ok`, `redirected`, `stale`뿐이다. 한 번도 작동한 적 없는 소스는 실패 횟수에 넣지 않는다.

---

## 8. LLM 1차 거르기

### 8.1 LLM은 꼭 필요한가

**수집과 폐기만이라면 없어도 된다. 요구한 추출 항목을 채우려면 필요하다.**
- 공인 명단과 해커톤처럼 구조가 있는 소스는 회사명·수상 여부·날짜가 데이터에 이미 있다. 투자 기사도 "금액·라운드·투자사가 하나라도 있는가"는 다국어 정규식으로 판정할 수 있다.
- 하지만 7개 언어로 된 자유 문장에서 회사명을 뽑는 일, 한국어 한 줄 설명·타깃·카테고리, 한국 유사 서비스 판단은 규칙으로 만들 수 없다.
- 그래서 **규칙이 먼저 걸러 LLM이 볼 양을 줄이고, LLM은 규칙이 못 하는 일만 한다.** `llm.backend: none`이면 시트에는 원어 제목과 정규식으로 뽑은 금액·라운드만 올라가고, 파이프라인 자체는 그 상태로도 돈다.

| 작업 | 규칙만으로 | LLM이 필요한 이유 |
|---|---|---|
| 중복 제거, 최근 7일 창, 유료·robots | ✔ | — |
| 공인 명단·해커톤의 회사명·수상 여부 | ✔ (구조화 데이터) | — |
| 투자 정보 0개인 기사 폐기 | ✔ (다국어 패턴, 보수적으로) | — |
| 자유 문장에서 회사명·금액·투자사 뽑기 | △ 영어 제목은 일부만 | 독·불·중·일·스웨덴어 기사, 라운드업 기사(회사 여러 곳) |
| 한국어 한 줄 설명, 타깃 고객, 카테고리 | ✗ | 요약·번역 |
| 수상 기사인지 참가 소개 기사인지 | △ 키워드는 오탐이 많음 | 문맥 판단 |
| 한국 유사 서비스 판단 | △ 후보 검색까지만 | 후보 중 실제로 비슷한지 판단 |

### 8.2 M1 16GB에서 쓸 로컬 모델

- Apple Silicon은 CPU와 GPU가 메모리를 나눠 쓴다. 16GB 중 GPU가 기본으로 쓸 수 있는 몫은 약 2/3(≈10.7GB)이다. 그래서 **4비트 양자화 기준 7GB 안팎의 8~10B급**이 알맞다.
- 이 작업은 짧은 원문에서 정해진 칸을 채우는 일이라, 큰 모델의 추론력보다 다국어 독해와 JSON 형식 준수가 중요하다.
- Ollama는 `format` 인자에 JSON 스키마를 주면 응답 형식을 강제할 수 있다.

| 후보 (Ollama 태그) | 크기 | 판단 |
|---|---|---|
| **qwen3.5:9b** | ≈ 6.6 GB | **1순위.** 중국어·일본어 원문이 많은 이 작업에 강하다. 사고(think) 모드는 끄고 쓴다 |
| gemma4:e4b | ≈ 7–10 GB | 비교 후보. 실효 4B급이라 더 빠르지만 추출 정확도는 낮을 수 있다 |
| 14B급 (Q4) | ≈ 9 GB | 품질 상한 확인용. 메모리가 빠듯하고 속도는 절반 수준 |
| gpt-oss:20b | ≈ 14 GB | 제외. GPU 몫을 넘는다 |

- 태그와 크기는 2026-11 검색 기준이다. 구현할 때 Ollama 라이브러리에서 다시 확인한다.
- 모델은 Phase 3에서 정답을 단 50건으로 맞붙여 보고 고른다. 모델 이름은 `settings.yaml`의 한 줄이다.
- 호출 설정: `think: false`, `temperature: 0`, `num_ctx: 8192`, `format: <JSON 스키마>`, `keep_alive: 30m`(사이클 동안 모델을 메모리에 유지).

### 8.3 작은 모델용 안전장치
- 요청 1건 = 원문 1건. 출력 칸은 짧게 하고, 카테고리 같은 값은 고정 목록(enum)에서만 고르게 한다.
- 회사명과 인용 구절이 원문에 실제로 있는지 코드가 검사한다 (판정 규칙 2·3).
- 투자 금액·라운드·투자사는 "원문에 쓰인 것만, 없으면 null"로 한다. 판정은 LLM이 아니라 `judge`가 한다.
- 한국 비교는 **DB에서 찾은 후보**(KR 소스 12개월치 전문 검색 상위 8개)를 근거로만 판단한다. 작은 모델은 한국 스타트업을 잘 모르므로, "없음" 대신 **"DB에서 못 찾음"**으로 표시한다.
- 시스템 프롬프트를 고정해 두면 Ollama가 같은 앞부분의 계산을 재사용해서, 원문 부분만 새로 읽는다.
- 프롬프트에는 언어별 예시 3개(영어 라운드업, 일본어 보도자료, 중국어 기사)를 넣는다. 예시를 바꾸면 `prompt_ver`를 올린다.

### 8.4 A단계 프롬프트 초안 · 추출·분류 (`prompts/stage_a.md`)

```
[system]
너는 스타트업 뉴스·명단에서 사실만 뽑아 JSON으로 정리하는 추출기다.
입력은 원문 1건(제목, 요약 또는 본문, 출처, 출처의 공인 유형 signal)이다.

규칙
1. 원문에 쓰여 있는 사실만 적는다. 추측·배경지식으로 채우지 않는다. 없으면 null.
   투자 금액·라운드·투자사는 원문에 명시된 경우에만. "undisclosed/비공개"는 금액 null.
2. 원문에 회사가 여러 곳이면(라운드업 기사, 수상자 목록) mentions에 각각 넣는다.
   특정 회사가 주인공이 아닌 글(시장 동향, 칼럼, 인사, 행사 공지)은 mentions = [].
3. company_name 과 evidence_quote 는 원문의 글자를 그대로 복사한다.
   evidence_quote 는 투자·선정·수상 사실을 보여 주는 30~200자 구절.
4. is_winner: 실제로 상을 받았을 때만 true. 참가·결선 진출 예정·데모 발표는 false.
   대회와 무관하면 null.
5. one_liner_ko: 누구에게 무엇을 해 주는지 한국어 한 문장, 60자 이내, 수식어 없이.
6. keywords_ko: 서비스 핵심을 나타내는 한국어 명사 3~6개. 조사·형용사 없이.
7. category: 아래 목록에서 하나만.
   AI·데이터 | 개발자도구·인프라 | 보안 | 핀테크 | 인슈어테크 | 헬스케어 | 바이오 |
   커머스·리테일 | 푸드·농업 | 모빌리티 | 물류 | 에너지·기후 | 교육 | HR·업무툴 |
   부동산·건설 | 미디어·콘텐츠 | 게임 | 여행·레저 | 하드웨어·로보틱스 | 생활·소비자앱 | 기타
8. country: 본사 국가 ISO 2글자. 원문에서 알 수 없으면 null.

[user]
signal: {signal}   source: {source_name} ({source_country})   detail: {signal_detail}
title: {title}
published: {published_at}
text: {summary 또는 body}
```

응답 스키마:

```
{ "is_funding_event": bool,
  "mentions": [{
    "company_name": str, "company_name_native": str|null, "website": str|null,
    "country": str|null, "one_liner_ko": str, "target_customer_ko": str,
    "customer_type": "B2B"|"B2C"|"B2B2C"|"B2G"|"unknown", "category": enum,
    "round": "pre-seed"|"seed"|"series_a"|…|"grant"|"other"|null,
    "amount": number|null, "currency": str|null, "investors": [str],
    "award_prize": str|null, "is_winner": bool|null,
    "evidence_quote": str, "keywords_ko": [str] }] }
```

연간 결과 페이지용 변형(`prompts/annual_winners.md`)은 같은 스키마에 지시만 바꾼다: "이 페이지는 {event} {year} 결과 페이지다. 수상자만 넣고 심사위원·후원사·참가 기업은 넣지 마라."

### 8.5 B단계 프롬프트 초안 · 한국 유사 서비스 (`prompts/stage_b.md`)

```
[system]
해외 회사 1곳과, 한국 스타트업 뉴스 DB에서 찾은 후보 기사 목록을 받는다.
후보 중에 같은 문제를 같은 고객에게 푸는 한국 서비스가 있는지 판단한다.
- 있음: 거의 같은 서비스가 후보에 있다
- 비슷함: 같은 문제를 다른 방식·다른 고객으로 풀거나, 큰 서비스의 한 기능이다
- DB에서 못 찾음: 후보 중에 해당하는 것이 없다
규칙: 후보 목록에 없는 이름은 쓰지 마라. 근거는 후보 번호로 댄다. reason_ko 는 한 문장.

[user]
해외 회사: {display_name} ({country}) — {one_liner_ko}
타깃: {target_customer_ko} / {customer_type}   카테고리: {category}   키워드: {keywords_ko}
후보 (KR 전문 검색 상위 8):
1. [{date} {source}] {title} — {summary 앞 150자}
…
```

응답: `{ "kr_similar": "있음"|"비슷함"|"DB에서 못 찾음", "match_ids": [int], "match_names": [str], "reason_ko": str }`

후보 검색: 대상 회사의 `keywords_ko`를 접두 검색으로 OR로 묶어 `items_fts`(KR 소스 행)에서 bm25 상위 8개를 찾는다. Claude API 백엔드로 바꾸면 모델이 아는 한국 서비스도 근거로 허용할 수 있다 (`from: knowledge` 표시).

### 8.6 처리 시간과 비용 (M1 기준 추정)

가정:
- 주 수집 700건 (중복 제거 후, 최근 7일) → 규칙 사전 폐기 40% → **A단계 420건** → 보존 45% → **B단계 189건**.
- 로컬 1건: A = 새 입력 800 + 출력 350 토큰, B = 900 + 200 토큰.
- M1 9B 4비트: 생성 약 17 토큰/초, 프롬프트 처리 약 200 토큰/초. **실측 전 추정치다.**
- API 1건: A = 2,600 + 550, B = 1,900 + 400 토큰.
- Batch API 50% 할인 가격: Haiku 5.5 $0.05/$0.25, Sonnet 5.5 $1/$5 (100만 토큰당, 2026-10 공시가). 환율 ₩1,400/$.

| 구성 (A 추출 + B 한국 비교) | Mac mini 시간 | 주 비용 | 월 비용 |
|---|---|---|---|
| **로컬 + 로컬 (시작점)** | **약 3.7시간** | $0 | 0원 |
| 로컬 + Sonnet 5.5 | 약 2.9시간 + 배치 대기 | $0.74 | 약 4,500원 |
| Haiku 5.5 + Haiku 5.5 | 배치 대기만 (보통 1시간 안) | $0.15 | 약 900원 |
| Haiku 5.5 + Sonnet 5.5 | 배치 대기만 | $0.85 | 약 5,200원 |
| Sonnet 5.5 + Sonnet 5.5 | 배치 대기만 | $2.98 | 약 18,000원 |

- 월요일 03:00에 시작하면 07:00 전에 시트가 채워진다.
- 전기는 주 0.1kWh 내외라 무시할 수 있다.
- 최초 12개월 적재는 LLM을 거치지 않으므로 LLM 비용·시간이 0이다 (수집 요청만 몇 시간).
- 진행 순서: **로컬 + 로컬**로 시작한다. 50건 점검에서 B단계 품질이 모자라면 **로컬 + Sonnet**(B만 API)으로 바꾼다. 둘 다 모자라면 **Haiku + Sonnet**. 바꾸는 것은 설정 두 줄이다.
- API 백엔드를 쓸 때: Batch API, 구조화 출력, 고정 시스템 프롬프트(캐싱), `stop_reason` 확인, `weekly_budget_usd`(기본 $5) 초과 시 제출 중단. 가격은 구현 시점에 다시 확인한다.

---

## 9. 결과 보기 방식

| | Google Sheets (추천) | Notion | 로컬 웹 UI |
|---|---|---|---|
| 매주 할 일 | 폰으로 시트 열고 ☑ | 폰으로 Notion 열고 ☑ | Mac mini 주소로 접속 (집 와이파이 또는 VPN) |
| 밖에서 보기 | ✔ | ✔ | ✗ 외부 접속을 따로 열어야 함 |
| 초기 설정 | 서비스 계정 키 + 시트 공유 (1회 10분) | 통합 토큰 + DB 공유 (1회 5분) | 없음 |
| 구현량 | 적음 | 중간 (속성 스키마, 페이지 ID 관리) | 많음 |
| 필터·정렬·메모 | 기본 기능으로 충분 | 좋음 (뷰·보드) | 직접 구현 |
| 약점 | 모양이 투박함 | API 초당 약 3회 제한, 행이 쌓이면 느려짐 | 밖에서 못 봄, 서버를 계속 띄워 둬야 함 |

**추천: Google Sheets.** "손이 가장 덜 가는" 기준은 매주 확인할 때의 수고다. 폰에서 바로 열리고, 체크박스와 필터가 기본 기능이라 화면을 만들 필요가 없다.

### 시트 구성 · "최신 1주일치만"

| 탭 | 내용 |
|---|---|
| 이번 주 | 매주 **통째로 새로 쓴다**. 쓰기 전에 지난 내용의 ☑·메모를 먼저 DB로 회수한다. 1행은 실행 요약(`W46 · 11/09 03:12 실행 · 신규 38곳 · 폐기 412 · 오류 0 · 비활성 소스 1`). 열: id(숨김) · ☑ 볼만함 · 메모 · 회사 · 국가 · 한 줄 설명 · 타깃 · 카테고리 · 공인 근거 · 투자(라운드/금액 USD/투자사) · 한국 유사 · 원문 링크(최대 3) · 과거 언급 수 |
| 관심 | ☑한 회사가 쌓인다. 주차·메모가 함께 남는다. 스크립트는 행 추가만 하고 고치지 않는다 |
| 소스 상태 | 소스별 상태, 마지막 성공, 연속 실패, 비활성 사유 |
| 폐기 샘플 | 이번 주 폐기분 중 무작위 20건 (사유, 제목, 링크). 자동 폐기를 믿어도 되는지 가끔 훑어보는 용도 |

- 지난주에 체크하지 못한 항목은 '이번 주' 탭에서 사라지지만 DB에는 남는다.
- 이전에 본 회사가 이번 주에 새 소식(예: YC 선정 뒤 시리즈 A)으로 다시 나오면 "과거 언급 수"와 공인 근거에 이전 기록이 함께 보인다.

---

## 10. 에러 처리와 로깅

### 격리
- **소스 단위**: 소스 하나의 예외는 `fetch_log`에 남기고 다음 소스로 넘어간다.
- **단계 단위**: 수집이 통째로 실패해도 이미 쌓인 항목의 LLM 처리와 게시는 진행한다.
- **행 단위**: LLM 응답 1건이 스키마에 맞지 않으면 1회 재시도한다. 3회 실패하면 `llm_error`로 두고 다음 건으로 간다.
- **사이클 단위**: 게시까지 끝나야 `cycle_done`을 기록한다. 끊기면 다음 깨움이 남은 단계부터 이어서 한다.

### 소스 장애와 자동 비활성화

| 상황 | 처리 |
|---|---|
| 일시 오류 (타임아웃, 5xx, 429, DNS) | 재시도 후에도 실패하면 이번 실행 실패 1회 |
| 영구 오류 (404, 410, 피드 아님, 파싱 실패) | 실패 1회 (사이트 점검일 수 있어 바로 끄지 않는다) |
| 조용한 고장 (crawl 2회 연속 0건) | 실패 1회 |
| robots 차단 | 실패로 세지 않고 바로 제외, 소스 상태 탭에 표시 |
| **연속 실패 3회** (설정값) | 자동 비활성화, WARNING 로그, 시트 요약 줄·소스 상태 탭에 표시. CSV의 `active`는 건드리지 않는다 |
| 비활성 소스 | 30일마다 1회 시험 요청을 보내 성공하면 자동 복구. `radar sources enable <id>`로 직접 켤 수도 있다 |
| Ollama 응답 없음 | 서비스를 1회 재시작. 그래도 안 되면 남은 항목은 `llm_pending`으로 두고 다음 깨움이 이어서 한다 |

실패는 실행당 1회로 센다 (한 실행 안의 재시도는 1회로 친다).

### 로그와 알림
- `data/logs/radar.log`: 주 단위로 파일을 바꾸고 12주 보관한다. 형식은 `시각 레벨 run_id 단계 source_id 메시지`.
- `radar status`: 최근 실행, 단계별 건수, 비활성 소스, 남은 LLM 작업. SSH로 확인한다.
- **DB 백업**: 주간 사이클 시작 전에 SQLite 백업 API로 `data/backups/radar-YYYYMMDD.db`를 만들고 8개를 보관한다.
- **알림**: Mac mini 앞에 사람이 없으므로 macOS 알림은 쓰지 않는다. 기본은 시트 맨 위 요약 줄이다. 선택으로 실패 때만 개인 Gmail로 메일을 보낸다 (앱 비밀번호, `smtplib`). Mac mini가 통째로 죽으면 메일도 안 오므로, **요약 줄의 실행 날짜가 오래됐으면 이상 신호**로 본다.

---

## 11. 단계별 구현 계획

각 Phase가 끝나면 그 상태로 Mac mini에서 매주 자동으로 끝까지 돈다. Phase 3까지의 결과는 `radar export`가 CSV로 만들어 iCloud Drive 폴더에 두므로 노트북이나 폰에서 연다. Phase 4부터는 시트로 본다.

### Phase 1 · tier 1 RSS·gnews → DB
- 범위
  - 새 레포를 만들고 `sources.csv`를 옮긴다 (+3열).
  - config · db · http(예절 전부) · rss · gnews · verify
  - 기사 중복, 최근 7일 창, 자동 비활성화
  - `backfill`(WordPress 과거 페이지) · `install` · `doctor` · `status` · `export`
- 대상: rss 18개(feed_only 5개 포함) + gnews 3개 = 21개
- 완료 기준
  - Mac mini에서 사람 손 없이 주간 사이클이 1회 끝났다.
  - 검증 보고서에 21개 소스의 상태가 모두 나온다.
  - 틀린 URL을 넣으면 3회 뒤 비활성화되고, 나머지 소스는 정상이다.
  - 두 번 돌려도 항목이 늘지 않는다 (멱등).
  - feed_only 원문 요청이 0건이다 (`fetch_log`로 확인).

### Phase 2 · crawl 소스
- 범위
  - 스파이크 1일: 6곳의 robots·데이터 위치·로그인 벽 확인.
  - 어댑터 등록부, `list_diff_html`, `annual_winners_page` (LLM 연결 전까지는 페이지 텍스트만 저장).
  - 전용 어댑터: YC Companies · YC Launches · Devpost(수상작 + 임계값 + 발표 대기) · J-Startup · PR TIMES · Startup Nation Finder
  - 12개월 적재, 조용한 고장 감지, fixture 테스트
- 완료 기준
  - 6개 어댑터가 fixture와 실제 수집을 모두 통과한다.
  - Devpost 비수상작이 DB에 0건이다.
  - 적재 뒤에는 매주 새 항목만 생긴다.

### Phase 3 · 규칙 필터 + 로컬 LLM
- 범위
  - `patterns.yaml` 규칙 사전 폐기
  - Ollama 백엔드 (+ 같은 인터페이스의 Claude API 백엔드)
  - 프롬프트 A·B, judge, mentions·companies, FTS5 KR 검색, 회사 병합, `rejudge`
  - 정답을 단 50건으로 qwen3.5:9b와 gemma4:e4b를 비교하고 M1 실측 속도를 기록한다. 참고로 같은 50건을 Haiku로도 돌린다 (약 1센트).
- 완료 기준
  - 1주치가 M1에서 6시간 안에 사람 손 없이 판정까지 끝난다.
  - 50건 중 잘못 폐기 ≤ 2건, 회사명 오류 ≤ 3건.
  - 도중에 Ollama를 죽여도 다음 실행이 이어서 한다.

### Phase 4 · 시트
- 범위
  - `radar sheet init`: 탭 4개, 체크박스, 필터 보기
  - '이번 주' 덮어쓰기 전에 ☑ 회수, '관심' 누적
  - 소스 상태·폐기 샘플 탭, 요약 줄, (선택) 실패 메일
- 완료 기준
  - 월요일 아침 시트에 이번 주 결과가 있다.
  - 폰에서 ☑한 것이 다음 주 '관심' 탭에 있다.
  - 설치 이후 사람이 실행한 명령이 0개다.

그 뒤 2주를 운영해 보고 `max_tier: 2`로 올린다. rss·gnews는 CSV만으로 늘어난다. crawl은 범용 어댑터 설정으로 먼저 해 보고, 안 되는 곳만 전용 어댑터를 만든다.

---

## 12. 결정이 필요한 열린 질문

| # | 질문 | 설계상 기본값 |
|---|---|---|
| 1 | Mac mini는 하루 종일 켜져 있지만 정전·OS 업데이트로 재시동되는 경우가 남는다. FileVault를 끄고 자동 로그인을 켤까? 켜 두면 재시동 뒤 한 번 직접 로그인할 때까지 수집이 멈춘다 | 자동 로그인 (FileVault 끔). 키 파일은 권한 600 |
| 2 | 로컬 모델이 품질 기준에 못 미치면 B단계만 Sonnet으로 바꿀까? (월 약 4,500원) | 예, B단계만 |
| 3 | 더브이씨(partial, 피드 없음)가 빠진다. 로그인 없이 보이는 공개 목록만 읽는 것은 허용할까? | 제외. KR 인덱스는 플래텀·벤처스퀘어·스타트업레시피·TIPS·Google News(ko)로 채운다 |
| 4 | 해커톤 임계값 "등록자 200명 또는 상금 $5,000"이 괜찮은가? | 그대로 시작하고 2주 뒤 양을 보고 조정 |
| 5 | 후기 단계·대형 라운드(Series C 이상 또는 $100M 이상)를 거를까? | 거르지 않는다. 시트 필터로만 본다 |
| 6 | 본문 보강(scope=full 소스에서 요약이 짧을 때 원문 앞부분 읽기)을 켤까? | 끈다. Phase 3 점검 결과를 보고 정한다 |
| 7 | 시트를 둘 Google 계정 | 개인 Gmail (회사 계정은 피한다) |
| 8 | 실패할 때 메일을 받을까? | 받는다 (실패 때만) |
| 9 | 사이클을 몇 주 놓쳤을 때도 "최신 7일치만" 처리하고 나머지는 적재만 하는 게 맞는가? | 맞다 (요청대로) |
| 10 | 주간 사이클 시작 때 `git pull`로 코드를 자동 갱신해도 되는가? (push한 코드가 바로 다음 주에 돈다) | 된다. 실패하면 현재 버전으로 계속 |
| 11 | gnews 확장: 어떤 국가 × 키워드 조합을 넣을까? (지금 tier 1은 en·ja·ko 3개) | Phase 1은 기존 행만 |
| 12 | 해커톤 수상 프로젝트(아직 회사가 아닌 것)를 같은 탭에 둘까, 별도 탭으로 뺄까? | 같은 탭, "프로젝트" 표시 |
