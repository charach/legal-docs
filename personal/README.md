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
    ├── summer.css          공용 디자인 시스템 (모든 페이지가 이걸 먼저 로드)
    ├── *.webmanifest       페이지별 PWA 매니페스트 (홈화면 설치용)
    └── icons/              홈화면 아이콘 PNG (180·512px)
```

## 디자인 규칙

"이른 아침의 바닷가". 더하지 말고 빼는 방향. 새 요소를 만들 때도 이 선을 넘지 않는다.

| 역할 | 값 |
|---|---|
| 배경 | `#FAFDFD` |
| 본문 | `#1A2E35` |
| 보조 | `#5C7A85` |
| 포인트 | `#0E7C94` — 링크와 CTA에만, 화면의 5% 이하 |
| 구분선 | `#E4EFF1` |

- 서체는 Pretendard. 헤드라인 600 / `letter-spacing: -0.02em`, 본문 16px / `line-height: 1.7`
- 콘텐츠 폭 1080px, 좌우 24px, 섹션 간격 데스크톱 140px · 모바일 80px
- 반경은 카드 8px, 버튼 6px. **알약형(9999px) 금지**
- 그림자는 `0 1px 3px rgba(26,46,53,.06)` 하나만
- **그라데이션·이모지·글로우·글래스모피즘 금지.** 아이콘도 꼭 필요할 때만
- hover는 `0.2s ease`로 색이 조금 깊어지는 정도. 확대·바운스 없음
- 스크롤 등장은 `.rise` 클래스 하나(opacity + 8px, 1회)로 통일

새 색을 추가하기 전에 이 다섯 개로 표현할 방법이 없는지 먼저 확인할 것.
데이터(JSON)에도 이모지를 넣지 않는다 — 페이지가 그대로 렌더링한다.

### 예외: 그로밋

아내 페이지 세 곳에만 「월레스와 그로밋」 GIF를 둔다. 절제 기조와는 어긋나는
요소라 **작게(168px), 섹션 끝의 `.closing` 자리에만, 흑백 배경 위에** 올려 균형을 맞췄다.

- `study_calendar` — 그날 상태에 따라 바뀐다. 마감·면접 같은 `hard` 앵커가 있는
  날은 `dday`, `goal` 앵커가 있는 날은 `goal`이 진도 상태(쉬는 날 / 진행 중 / 다 끝냄)를
  덮어쓴다. `anchorState()` 참고
- `ai_grad_prep` — 04 강의와 자료 / 07 합격 후에 할 것 / 08 흔한 함정
- `interview_prep` — 02 전략 / 06 아직 확인 못 한 것 / 모의 연습 마지막 문항
- 목록은 `data/gromit.json`. Giphy(Aardman 공식 채널)에서 **핫링크**하므로
  저장소에 파일을 두지 않는다. 네트워크가 없으면 이미지만 비고 레이아웃은 유지된다
  (`aspect-ratio` 지정)
- 달력만 `gromit.json`을 `fetch` 하고 나머지 두 페이지는 URL을 HTML에 직접 쓴다.
  GIF를 바꾸려면 JSON과 HTML을 함께 고칠 것

**한 섹션에 하나, 페이지당 셋까지.** 넷째를 넣고 싶어지면 대신 기존 하나를
빼는 게 맞다. 새로 고를 때는 `giphy.com/wallaceandgromit`(공식 채널)에서만
가져오고, 실제로 열어 본 뒤 `alt`를 장면 그대로 적는다.

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

이모지를 쓰지 않고 **글자로 구분한다.** 바탕은 팔레트 세 가지(잉크·포인트·연한 배경)만
돌려쓰고, 라벨이 서로 달라서 홈화면에서 구별된다.

| 페이지 | 라벨 | 바탕 | 앱 이름 |
|---|---|---|---|
| index | P | 잉크 | 개인 |
| study_calendar | 오늘 | 포인트 | 오늘 |
| ai_grad_prep | 로드맵 | 연한 배경 | 로드맵 |
| interview_prep | 면접 | 잉크 | 면접 |
| grad_schools | 대학원 | 연한 배경 | 대학원 |
| exercise | 훈련 | 포인트 | 훈련 |
| career_roadmap | 커리어 | 연한 배경 | 커리어 |

`assets/*.webmanifest` 와 `<link rel="apple-touch-icon">` 이 함께 결정한다 —
파비콘만 바꿔선 홈화면 아이콘이 안 바뀐다.

아이콘을 바꾼 뒤에는 홈화면에서 **한 번 지우고 다시 추가**해야 한다. iOS가 캐시한다.

PNG는 Chrome 헤드리스로 생성했다 (HTML 한 장을 180·512px로 스크린샷).
