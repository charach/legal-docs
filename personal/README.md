# personal/

개인용 정적 페이지 모음. 검색 비노출(`noindex`), 빌드 없이 정적 서빙.

## 구조

```
personal/
├── index.html              🏠 허브 — 카드 목록 + D-day
├── exercise.html           🏊 아이언맨 훈련 캘린더        (본인)
├── career_roadmap.html     🚀 커리어 전환 로드맵          (본인)
├── grad_schools.html       🏛 직장인 특수대학원 42곳 비교  (함께)
├── ai_grad_prep.html       🎓 AI 대학원 입시 학습 로드맵   (아내)
├── interview_prep.html     🎤 AI 대학원 면접 질문은행      (아내)
├── study_calendar.html     📅 오늘 할 일 + 월간 학습 달력  (아내)
│
├── data/                   페이지가 fetch 하는 원본 데이터
│   ├── study_plan.json       로드맵·주차별 계획·강의·지원 후보
│   └── interview_bank.json   면접 질문 201문항·학교 프로필·출처
│
└── assets/
    ├── *.webmanifest       페이지별 PWA 매니페스트 (홈화면 설치용)
    └── icons/              홈화면 아이콘 PNG (180·512px)
```

**HTML은 이 폴더 최상단에 고정한다.** 홈화면에 설치된 바로가기가 URL로 물려
있어서 파일을 옮기면 전부 깨진다.

## 데이터가 페이지를 만든다

`ai_grad_prep.html` · `interview_prep.html` · `study_calendar.html` 세 페이지는
HTML에 내용이 없다. `data/*.json`을 `fetch` 해서 그린다.

- 로드맵·주차 계획·강의 목록·지원 후보를 고치려면 → `data/study_plan.json`
- 면접 질문·학교별 면접 정보·출처를 고치려면 → `data/interview_bank.json`
- `study_calendar.html`과 `ai_grad_prep.html`은 체크 상태를 공유한다
  (localStorage 키 `aiGradPlan.v2`)

## 로컬에서 열기

`file://` 로 직접 열면 브라우저 보안 정책 때문에 `fetch`가 막혀 JSON을 못 읽는다.

```bash
cd personal && python3 -m http.server 8000
# http://localhost:8000/index.html
```

GitHub Pages에 올라가면 그냥 동작한다.

## 홈화면 아이콘

페이지마다 색·이모지·앱 이름이 다르다. `assets/*.webmanifest` 와
`<link rel="apple-touch-icon">` 이 함께 결정한다 — 파비콘만 바꿔선 안 바뀐다.

| 페이지 | 아이콘 | 색 | 앱 이름 |
|---|---|---|---|
| index | 🏠 | `#0f2740` | 개인 |
| exercise | 🏊 | `#0284c7` | 훈련 |
| career_roadmap | 🚀 | `#7c3aed` | 커리어 |
| grad_schools | 🏛 | `#d97706` | 대학원 |
| ai_grad_prep | 🎓 | `#4f46e5` | 로드맵 |
| interview_prep | 🎤 | `#be123c` | 면접 |
| study_calendar | 📅 | `#0f766e` | 오늘 |

아이콘을 바꾼 뒤에는 홈화면에서 **한 번 지우고 다시 추가**해야 한다. iOS가 캐시한다.

아이콘 PNG는 Chrome 헤드리스로 생성했다 (그라데이션 배경 + 이모지 → 180·512px 스크린샷).
