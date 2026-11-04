# ttomstudio.com

GitHub Pages(Jekyll)로 서빙하는 정적 사이트. 빌드 없음.

## 폴더

```
/
├── index.html            사이트 첫 화면
├── personal/             개인 페이지 — 규칙·데이터 설명은 personal/README.md
├── travel/               여행 일정·비교
├── portfolio/            시스템 설계 포트폴리오 (ai_video_service_architecture.md = 아키텍처 페이지 원본 메모)
├── cs/                   CS 교재
├── food/                 푸드 R&D 노트
├── vocal_warm/           앱 개인정보처리방침·계정 삭제 안내 (스토어에 URL 등록 — 옮기지 말 것)
│
├── assets/               사이트 공용 파일
│   ├── css/  summer.css (공용 디자인 시스템) · gromit.css (그로밋 장식)
│   ├── js/   gromit-cursor.js (따라오는 그로밋 포인터)
│   └── img/  사이트의 모든 이미지
│       ├── favicon/      탭 파비콘 3종 (전 페이지 공통)
│       ├── gromit/       그로밋 얼굴 아이콘 3종 · 마우스 포인터 4종
│       ├── app-icons/    홈화면 아이콘 (180·512px, personal/assets/*.webmanifest 가 참조)
│       ├── exercises/    근력 동작 사진 (동작별 0.jpg · 1.jpg)
│       ├── gurye/        구례 대회 공식 코스도 · 완주 배지
│       └── sohn/         손기정 마라톤 공식 코스도
│
├── _layouts/default.html .md 페이지용 Jekyll 레이아웃
└── CNAME · _config.yml
```

## 규칙

- **이미지는 `assets/img/<주제>/` 한곳에만 둔다.** 섹션 폴더 안에 이미지를 두지 않는다. 하위 폴더 페이지에서는 `../assets/img/...`.
- **페이지(.html) URL은 옮기지 않는다.** 홈화면 바로가기와 외부 링크가 URL로 물려 있다.
- 섹션 폴더 안의 `assets/`는 그 섹션 전용 코드·매니페스트, `data/`는 데이터(JSON · 데이터 JS · 원본 엑셀).
- 공개 저장소다. 사내 자료·개인 원본은 커밋하지 말고 `.gitignore`에 넣는다.

## 로컬에서 열기

```bash
python3 -m http.server 8000   # 저장소 루트에서
# http://localhost:8000/personal/index.html
```

하위 폴더에서 서버를 띄우면 `../assets/`의 CSS·이미지가 빠진다. `file://`로 열면 `fetch`가 막혀 JSON 기반 페이지가 비어 보인다.
