# framework.html 의 그림 1·1b·2·3 을 만드는 생성기. 실행하면 out.json 에 SVG 문자열이 담긴다 (framework.html 에 수동 삽입).
# SVG 생성기 — 격자 정렬된 박스/화살표/마름모
import html
def esc(s): return html.escape(s, quote=True)

class D:
    def __init__(s, w, h): s.w, s.h, s.el = w, h, []
    def box(s, x, y, w, h, title, lines=(), cls="", r=8):
        s.el.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>')
        s.el.append(f'<text class="t" x="{x+14}" y="{y+24}">{esc(title)}</text>')
        for i, l in enumerate(lines):
            s.el.append(f'<text class="s" x="{x+14}" y="{y+44+i*16}">{esc(l)}</text>')
    def pill(s, x, y, w, h, title, cls=""):
        s.el.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"/>')
        s.el.append(f'<text class="t" x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle">{esc(title)}</text>')
    def cbox(s, x, y, w, h, lines, cls="", r=8):
        s.el.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>')
        n=len(lines); y0=y+h/2-(n-1)*8
        for i,l in enumerate(lines):
            c="t" if i==0 else "s"
            s.el.append(f'<text class="{c}" x="{x+w/2}" y="{y0+i*16+5}" text-anchor="middle">{esc(l)}</text>')
    def diamond(s, cx, cy, w, h, lines, cls="dec"):
        s.el.append(f'<polygon class="box {cls}" points="{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"/>')
        n=len(lines); y0=cy-(n-1)*8
        for i,l in enumerate(lines):
            c="t" if i==0 else "s"
            s.el.append(f'<text class="{c}" x="{cx}" y="{y0+i*16+5}" text-anchor="middle">{esc(l)}</text>')
    def arrow(s, pts, label=None, lpos=None, dashed=False, anchor="middle", dy=-6):
        d="M"+" L".join(f"{x},{y}" for x,y in pts)
        da=' stroke-dasharray="5 4"' if dashed else ''
        s.el.append(f'<path class="arrow" d="{d}"{da}/>')
        if label:
            if lpos is None:
                (x1,y1),(x2,y2)=pts[0],pts[-1]; lpos=((x1+x2)/2,(y1+y2)/2)
            s.el.append(f'<text class="l" x="{lpos[0]}" y="{lpos[1]+dy}" text-anchor="{anchor}">{esc(label)}</text>')
    def label(s, x, y, text, cls="lay", anchor="start"):
        s.el.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(text)}</text>')
    def band(s, y, h):
        s.el.append(f'<rect class="band" x="0" y="{y}" width="{s.w}" height="{h}"/>')
    def svg(s, aria):
        head=(f'<svg viewBox="0 0 {s.w} {s.h}" role="img" aria-label="{esc(aria)}">'
              '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5C7A85"/></marker></defs>')
        return head+"".join(s.el)+"</svg>"

# ---------- 1. 아키텍처 ----------
A=D(1000,1410)
for y,h in [(0,200),(220,180),(420,130),(560,210),(790,220),(1030,210),(1260,140)]: A.band(y,h)
A.label(20,24,"① 소스 레지스트리  ·  커넥터 패밀리 8종 × 인스턴스 1,000+  ·  전 세계 193국")
fx=[20,158,296,434,572,710,848]; fw=130
fams=[("글로벌 통계 API",["Comtrade · WDI · FAO","GDELT · ePing  (≈10)"]),("국가별 정부·세관",["통계청 · 세관 · 중앙은행","193국 × 2  (≈390)"]),
      ("규제기관·관보",["식품청 · 할랄청 · 관보","193국 + 원문  (≈250)"]),("매체 RSS",["식품 전문지 · 현지 일간지","국가당 2~5  (≈400)"]),
      ("플랫폼 API",["YouTube · Reddit · Trends","TikTok CC  (5)"]),("리포트 · 경쟁사",["GAIN · KOTRA · KATI","경쟁사 IR · 상표 · 전시회"]),("롯데 자료·현장",["DART · IR","본선 CSV"])]
for i,(t,l) in enumerate(fams):
    A.box(fx[i],40,fw,80,t,l,cls="human" if i==6 else "db")
A.el.append('<rect class="box db" x="20" y="132" width="960" height="36" rx="6"/>')
A.el.append('<text class="t" x="34" y="155">source_registry 테이블</text>')
A.el.append('<text class="s" x="200" y="155">family · country · instance_url · parser_config · schedule · license · reliability_prior · status(active|failing|blacklisted) · added_by · approved_at   —   1,000+ 행</text>')
A.label(20,244,"② 수집 에이전트 4종 + 발굴 에이전트  (LLM + 툴, 스케줄 실행 · 레지스트리 행을 순회)")
ax=[20,215,410,605]; aw=185
agents=[("무역·거시 수집 · 월",["fetch_*(family, instance)","parse_dart · load_csv(현장)","→ 정규화 (코드·통화·연도)"]),
        ("뉴스 신호 추출 · 일",["search_gdelt · fetch_rss","해시 비교 → 새 기사만","extract_signal → JSON  ①"]),
        ("SNS·이커머스 · 주",["yt · reddit · trends · market","샘플링 → classify_theme  ②","집계만 저장"]),
        ("법령 수집 · 변경 시",["fetch_reg(country) · 관보 감시","diff_vs_previous → 변경만","chunk_by_article"])]
for i,(t,l) in enumerate(agents):
    A.box(ax[i],260,aw,120,t,l,cls="llm")
A.box(800,260,180,120,"소스 발굴 에이전트  ⑦",["국가 × 패밀리 빈칸 탐색","후보 URL → 유형·접근 판정","시험 수집 → 사람 승인 후 등록"],cls="llm")
for x,lab in [(112,"통계 · 국가별 · 롯데"),(307,"RSS · 리포트 · 경쟁사"),(502,"플랫폼 API"),(697,"규제기관 · 관보")]:
    A.arrow([(x,168),(x,260)],lab,lpos=(x+6,218),anchor="start")
A.arrow([(890,260),(890,168)],"행 추가 (승인 후)",lpos=(884,218),anchor="end",dashed=True)
for x in (112,307,502,697): A.el.append(f'<path class="arrow" d="M{x},380 L{x},412" style="marker-end:none"/>')
A.el.append('<path class="arrow" d="M112,412 L697,412" style="marker-end:none"/>')
A.arrow([(135,412),(135,460)])
A.label(400,406,"모든 수집 결과 → 게이트  (원문 + 파싱값 + 출처 id)",cls="l")
A.label(160,444,"②b 품질 게이트  ·  저장 전에 전부 통과  (규칙·교차 검증은 프로그램, 심사관만 LLM)")
A.box(20,460,230,66,"1 규칙 검사  (프로그램)",["스키마 · 단위 · 범위 · 전월 ±50% · 중복"],cls="code")
A.box(270,460,230,66,"2 교차 검증  (프로그램)",["미러 통계 · 두 소스 일치율 · 환산"],cls="code")
A.box(520,460,250,66,"3 데이터 심사관  (LLM ⑧)",["출처 신뢰 · 정의 일치 · 시의성 · 충돌 해결"],cls="llm")
A.box(790,460,190,66,"4 사람  (C등급·충돌만)",["승인 · 기각 · 소스 블랙리스트"],cls="human")
A.arrow([(250,493),(270,493)]); A.arrow([(500,493),(520,493)]); A.arrow([(770,493),(790,493)])
A.label(510,542,"불일치·신규만 →",cls="l",anchor="middle"); A.label(780,542,"C·충돌만 →",cls="l",anchor="middle")
A.label(20,584,"③ 저장소  (세 층 · 덮어쓰기 없음 · 모든 행에 confidence A/B/C + validity_flags)")
A.box(20,600,280,150,"원문 저장소",["PDF · HTML · CSV 원본 그대로","source(id, url, family, instance,","  fetched_at, license, reliability)","용도: 출처 클릭 시 원문 확인"],cls="db")
A.box(330,600,340,150,"사실 테이블  (Postgres)",["fact(country, block, metric, value, period,","  source_id, confidence, flags[], as_of)","signal · sns_aggregate · country_card","insight_report · review_label · quarantine"],cls="db")
A.box(700,600,280,150,"벡터 색인  (pgvector)",["regulation_chunk(country, category,","  article_ref, text, effective_from,","  source_id, embedding)","+ BM25 색인 (하이브리드)"],cls="db")
A.arrow([(135,526),(135,600)],"원문 + 등급",lpos=(141,566),anchor="start")
A.arrow([(440,526),(440,600)],"fact · signal · sns 행 + confidence",lpos=(434,570),anchor="end")
A.arrow([(640,526),(640,570),(560,570),(560,600)],"C → quarantine",lpos=(566,566),anchor="start",dashed=True)
A.arrow([(720,526),(720,580),(840,580),(840,600)],"청크 + embedding",lpos=(846,576),anchor="start")
A.label(20,814,"④ 처리")
A.box(20,830,270,160,"스코어링 엔진  (코드)",["6축 z-점수 → 0~5 → 가중합","가중치 세트 4개 × 전 국가 순위","민감도 ±20%, 순위 안정성","C등급 값은 가중치 절반 · 결측은 0"],cls="code")
A.box(360,830,280,160,"인사이트 에이전트  · 월 1회",["이번 달 vs 지난달 스냅샷 diff","순위 변동 · 새 규제 · 2σ 급등 신호","Tier 승격·강등 제안 (193 → 40 → 12)","근거 문단 생성 (fact/signal id만)"],cls="llm")
A.box(700,830,280,160,"법령 RAG 에이전트",["국가당 고정 5문항(관세·인증·","라벨·등록·첨가물) → 조문 인용","시행일·수집일 검사 → '확인 필요'","답변 → 진입 장벽 축 점수 0~5"],cls="llm")
A.arrow([(400,750),(400,790),(155,790),(155,830)],"SELECT fact WHERE as_of = 이번 달",lpos=(280,786))
A.el.append('<path class="arrow" d="M500,750 L500,830" marker-start="url(#ah)"/>')
A.label(506,776,"읽기: 두 달 스냅샷 · signal",cls="l"); A.label(506,792,"쓰기: insight_report · country_card",cls="l")
A.arrow([(840,750),(840,830)],"hybrid search (국가·품목 필터)",lpos=(846,790),anchor="start",dy=0)
A.arrow([(720,830),(720,770),(640,770),(640,750)],"장벽 축 점수 → fact 행",lpos=(726,818),anchor="start",dy=0)
A.arrow([(290,910),(360,910)],"점수·순위",lpos=(325,902))
A.label(20,1054,"⑤ 출력 · 사람")
A.box(20,1070,270,150,"국가 카드 · TOP3 대시보드",["가중치 슬라이더 → 즉시 재계산","축별 점수, 근거 문단, 출처 링크","Tier 필터 (193 / 40 / 12)"],cls="")
A.box(360,1070,280,150,"월간 diff 리포트",["1 순위 변동  2 새 규제  3 급등 신호","4 실적 대비  5 추천 액션 3개","6 데이터 상태 (실패·격리·C등급·신규 소스)"],cls="")
A.box(700,1070,280,150,"담당자 검토",["가중치·후보국·Tier 조정","신호·데이터 승인 / 기각 + 사유","신규 소스 승인 → 레지스트리"],cls="human")
A.arrow([(155,990),(155,1070)],"점수·근거",lpos=(161,1034),anchor="start")
A.arrow([(500,990),(500,1070)],"리포트 초안",lpos=(506,1034),anchor="start")
A.arrow([(640,1145),(700,1145)],"검토 요청",lpos=(670,1136))
A.arrow([(840,1070),(840,990)],None)
A.label(846,1022,"승인/기각 + 사유",cls="l"); A.label(846,1038,"→ review_label (few-shot)",cls="l")
A.arrow([(840,1220),(840,1240),(10,1240),(10,910),(20,910)],"가중치·Tier 변경 → ④ 스코어링부터 재계산 (수집 재실행 없음)",lpos=(420,1236),dashed=True)
A.label(20,1284,"⑥ 평가  (매 배포 · CI)")
A.box(20,1300,230,90,"백테스트",["2021~23 → 2024~25","수출 급증국 재현율"],cls="")
A.box(270,1300,230,90,"RAG 정답셋",["12개국 × 5문항","조문 일치율"],cls="")
A.box(520,1300,230,90,"신호 추출 정밀도",["샘플 50건 수작업 채점","유형·방향 ≥ 0.85"],cls="")
A.box(770,1300,210,90,"심사관 정밀도",["사람 라벨 200건 대비","A/B/C 일치 ≥ 0.9"],cls="")
arch=A.svg("소스 레지스트리(7패밀리·1,000+ 인스턴스·193국)의 행을 수집 에이전트 4종이 순회하고 발굴 에이전트가 행을 추가한다. 모든 수집 결과는 품질 게이트(규칙 검사·교차 검증·LLM 데이터 심사관·사람)를 거쳐 세 층 저장소에 등급과 함께 쌓이고, 스코어링·인사이트·법령 RAG가 그 위에서 돌아 대시보드와 월간 diff 리포트를 만들며, 담당자의 조정과 라벨이 되돌아온다.")

# ---------- 2. 월간 실행 플로우차트 ----------
F=D(1000,1560)
cx=360; W=400; H=56; X=cx-W/2
def P(y,lines,cls=""): F.cbox(X,y,W,H,lines,cls)
def DM(y,lines): F.diamond(cx,y+H/2+6,W+40,H+40,lines)
def V(y1,y2,label=None): F.arrow([(cx,y1),(cx,y2)],label,lpos=(cx+8,(y1+y2)/2+4),anchor="start",dy=0)
F.pill(X,20,W,44,"스케줄 트리거 · 매월 1일 02:00 (수동 실행 가능)")
V(64,100)
P(100,["레지스트리 순회: 수집 에이전트 4종 병렬","해시 비교로 바뀐 인스턴스만 (원문 저장)"],"llm")
V(156,200)
DM(200,["품질 게이트 통과?","규칙 → 교차 검증 → LLM 심사관 ⑧ → C등급·충돌은 사람"])
F.arrow([(cx+W/2+20,231),(700,231)],"아니오",lpos=(640,225))
F.cbox(700,205,270,52,["격리(quarantine) 또는 C등급","지난달 값 유지, 소스 상태 기록"],"")
F.arrow([(835,257),(835,300),(cx+W/2,300)])
V(262+ (H+40)/2 - 22 ,320,"예")
P(320,["사실 테이블 insert  (as_of = 이번 달)","덮어쓰기 없음 → 시계열 스냅샷"],"db")
V(376,410)
P(410,["지표 산출  6축 × 12개국","z-점수 → 0~5 압축"],"code")
V(466,500)
P(500,["법령 RAG  국가당 5문항 질의","답변 → 진입 장벽 축 점수"],"llm")
V(556,590)
P(590,["스코어링  가중치 세트 4개 × 순위","민감도 ±20%, 순위 안정성 계산"],"code")
V(646,690)
DM(690,["지난달 대비 변화 있나?","TOP3 변동 · 3계단 이동 · 새 규제 · 2σ 신호"])
F.arrow([(cx+W/2+20,721),(700,721)],"아니오",lpos=(640,715))
F.cbox(700,695,250,52,["'변동 없음' 한 줄 리포트","데이터 상태 표만 첨부"],"")
F.arrow([(950,721),(985,721),(985,1168),(cx+W/2,1168)])
V(752,810,"예")
P(810,["근거 문단 생성  (LLM)","fact · signal · regulation_chunk id만 참조"],"llm")
V(866,910)
DM(910,["검증 통과?","모든 문장에 [출처 id] · 숫자가 테이블과 일치"])
F.arrow([(cx+W/2+20,941),(700,941)],"아니오",lpos=(640,935))
F.cbox(700,915,270,52,["재생성  (최대 2회)","실패 문장만 다시"],"llm")
F.arrow([(835,915),(835,890),(cx+W/2,890),(cx+W/2,866)],dashed=False)
F.label(850,885,"다시 ⑨로",cls="l")
F.cbox(700,985,270,44,["2회 실패 → 사람 검토 플래그"],"human")
F.arrow([(835,967),(835,985)])
F.arrow([(700,1007),(cx+W/2+30,1007),(cx+W/2+30,1040),(cx+W/2,1040)])
V(972,1040,"예")
P(1040,["월간 diff 리포트 조립","순위 변동 · 규제 · 신호 · 액션 3개 · 데이터 상태"],"")
V(1096,1140)
P(1140,["담당자 검토","가중치·후보국 조정, 신호 승인/기각 + 사유"],"human")
V(1196,1240)
DM(1240,["가중치나 후보국을 바꿨나?"])
F.arrow([(cx-W/2-20,1271),(60,1271),(60,618),(X,618)],"예 → 스코어링부터 재계산 (수집 재실행 없음)",lpos=(70,1266),anchor="start")
V(1302,1360,"아니오")
P(1360,["country_card · insight_report 저장","기각 사유 → review_label → 다음 달 few-shot"],"db")
V(1416,1460)
F.pill(X,1460,W,44,"승인된 리포트 발송 · 대시보드 갱신")
F.label(990,1540,"마름모 = 분기 · 보라 = LLM 단계 · 회색 = 결정론적 코드 · 붉은 = 사람",cls="l",anchor="end")
flow=F.svg("월간 실행 흐름: 스케줄 트리거 → 수집 → 검증 분기 → as-of insert → 지표·RAG·스코어링 → 변화 유무 분기 → 근거 생성 → 출처 검증 분기(재생성 최대 2회) → diff 리포트 → 담당자 검토 → 가중치 변경 시 스코어링부터 재계산 → 저장·발송")

# ---------- 3. 질의 처리 플로우 ----------
Q=D(1000,640)
Q.cbox(20,250,200,120,["사용자 질문","\"UAE에 빼빼로 수출하려면","할랄 인증 필요해? 관세는?","추천 순위는?\""],"human")
Q.diamond(330,310,180,120,["의도 분류","수치 · 규정 · 추천"])
Q.arrow([(220,310),(240,310)])
# lanes
Q.box(460,40,300,120,"수치 질의  → SQL 툴",["query_fact(country, metric)","fact 테이블만 읽기 (as_of 최신)","값 + 단위 + 출처 id + as_of 반환"],cls="code")
Q.box(460,250,300,120,"규정 질의  → RAG 툴",["hybrid_search(국가·품목 필터, k=8)","effective_from · fetched_at 검사","조문 인용 답변, 오래되면 '확인 필요'"],cls="llm")
Q.box(460,460,300,120,"추천 질의  → 스코어링 결과",["country_card 최신 스냅샷 조회","가중치 세트별 순위 · 안정성","근거 문단 (fact/signal id 포함)"],cls="code")
Q.arrow([(330,250),(330,100),(460,100)],"수치",lpos=(395,94))
Q.arrow([(420,310),(460,310)],"규정",lpos=(440,300))
Q.arrow([(330,370),(330,520),(460,520)],"추천",lpos=(395,514))
Q.cbox(800,250,180,120,["합성 + 인용 검증","출처 id 없는 문장 폐기","숫자 ↔ 테이블 재대조","'확인 필요' 표시 유지"],"llm")
Q.arrow([(760,100),(800,100),(800,250)])
Q.arrow([(760,310),(800,310)])
Q.arrow([(760,520),(800,520),(800,370)])
Q.arrow([(890,370),(890,440)])
Q.cbox(800,440,180,120,["응답","할랄: 필수 [GSO 2055-1 §4.2]","관세: 5% [GCC CET · 확인 필요]","순위: 2위 (4세트 중 3) [card#…]"],"")
Q.label(20,600,"툴은 각각 한 저장소만 읽는다. 수치는 사실 테이블, 규정은 벡터 색인, 추천은 country_card. LLM이 숫자를 지어낼 경로가 없다.",cls="l")
query=Q.svg("질의 처리 흐름: 사용자 질문을 수치·규정·추천으로 분류해 각각 SQL 툴·RAG 툴·스코어링 결과 조회로 보내고, 합성 단계에서 출처 인용을 검증한 뒤 응답한다.")

import json
json.dump({"arch":arch,"flow":flow,"query":query},open("out.json","w"),ensure_ascii=False)
print(len(arch),len(flow),len(query))

# ---------- 4. 소프트웨어 아키텍처 ----------
S=D(1000,1080)
for y,h in [(0,130),(150,140),(310,310),(640,160),(820,190),(1010,70)]: S.band(y,h)
S.label(20,24,"클라이언트")
S.box(20,40,300,70,"웹 대시보드  (프로그램)",["국가 카드 · 슬라이더 · 출처 링크 · 검토 화면"])
S.box(350,40,300,70,"월간 리포트 수신",["이메일 · 사내 메신저 (Markdown/PDF)"])
S.box(680,40,300,70,"CLI · 노트북  (개발·평가)",["수동 실행, 백테스트, 평가셋 채점"])
S.label(20,174,"API 서버  ·  FastAPI  (프로그램, LLM 직접 호출 없음)")
S.box(20,190,960,80,"엔드포인트",["GET /cards?category   POST /score {weights}   POST /ask {question}   POST /review {signal_id, verdict, reason}   GET /report/{month}   POST /jobs/run"],cls="code")
S.label(560,254,"사내 SSO · 역할: 담당자(쓰기) / 열람(읽기)  ·  /score 는 1초 내 동기 응답, /ask 는 스트리밍",cls="l")
S.arrow([(170,110),(170,190)],"HTTPS / JSON",lpos=(176,154),anchor="start")
S.arrow([(500,190),(500,110)],"월 1회 발송",lpos=(506,154),anchor="start")
S.arrow([(830,110),(830,190)],"CLI → 같은 모듈 직접 호출",lpos=(836,154),anchor="start")
# 워커
S.label(20,334,"스케줄러 워커  ·  APScheduler + 작업 큐  (프로그램)")
S.el.append('<rect class="box" x="20" y="344" width="460" height="260" rx="10" stroke-dasharray="6 4"/>')
S.label(36,368,"잡 5종: 월간 수집 · 일간 뉴스 · 주간 SNS · 규제 감시 · 월간 인사이트",cls="l")
steps=[("커넥터","프로그램 · 레지스트리 순회",""),("정규화","프로그램",""),("규칙·교차 검증","프로그램",""),("데이터 심사관","LLM ⑧","llm"),
       ("신호·테마","LLM ①②","llm"),("지표·스코어링","프로그램",""),("근거 생성","LLM ④⑥","llm"),("인용 검증 · 조립","프로그램","")]
for i,(t,k,c) in enumerate(steps):
    r,cidx=divmod(i,4); x=36+cidx*112; y=390+r*74
    S.cbox(x,y,100,50,[t,k],c if c else "code")
    if cidx<3: S.arrow([(x+100,y+25),(x+112,y+25)])
S.arrow([(372+50,440),(372+50,452),(86,452),(86,464)])
S.label(36,560,"재시도 3회 · 멱등 (국가·지표·as_of 키) · 실패 소스는 C등급 표시 · LLM 단계는 런타임에 위임",cls="l")
S.label(36,580,"인스턴스 1,000+ 순회 ≈ 2시간 (병렬 20) · LLM은 바뀐 것·불일치만 → 월 수만 건, 소형 모델 배치",cls="l")
# 런타임
S.label(510,334,"에이전트 런타임  ·  OpenAI Agents SDK  (라이브러리, 워커와 API가 함께 사용)")
S.el.append('<rect class="box" x="510" y="344" width="470" height="260" rx="10" stroke-dasharray="6 4"/>')
S.box(526,364,212,120,"에이전트 정의  (LLM)",["① 뉴스 신호  ② SNS 테마  ③ 법령 RAG","④ 근거 작성  ⑤ 질의 라우터  ⑥ 인사이트","⑦ 소스 발굴  ⑧ 데이터 심사관","각각 system prompt + 출력 스키마"],cls="llm")
S.box(752,364,212,120,"툴 레지스트리  (프로그램)",["query_fact · hybrid_search","score(weights) · fetch_*","순수 함수, 부작용 없음","툴 = 핵심 모듈의 얇은 래퍼"],cls="code")
S.box(526,498,438,90,"가드레일  (프로그램)",["structured output 스키마 검증 · 인용 검증기(출처 id 존재? 숫자 = 테이블?)","재시도 최대 2회 · 토큰·비용 한도 · 모든 툴 호출 트레이스 기록"],cls="code")
S.arrow([(632,484),(632,498)]); S.arrow([(858,484),(858,498)])
S.arrow([(480,415),(510,415)],"LLM 단계 위임",lpos=(495,404))
S.arrow([(230,270),(230,344)],"POST /jobs/run · /score",lpos=(236,312),anchor="start")
S.arrow([(700,270),(700,344)],"/ask · /review",lpos=(706,312),anchor="start")
# 핵심 모듈
S.label(20,664,"핵심 모듈  ·  Python 패키지  (전부 프로그램 · LLM 없음 · 단위 테스트 대상)")
mods=[("커넥터 8종","httpx · 재시도"),("정규화","pandas · ISO 코드"),("지표 계산","pandas · z-점수"),("스코어링","numpy · 가중합"),
      ("백테스트","과거 as_of 재생"),("청킹·검색","BM25 + 벡터"),("인용 검증기","정규식 + SQL"),("리포트 빌더","Jinja2 · diff")]
for i,(t,sub) in enumerate(mods):
    x=36+i*118; S.cbox(x,684,108,66,[t,sub],"code")
S.arrow([(250,604),(250,684)],"직접 import",lpos=(256,648),anchor="start")
S.arrow([(858,588),(858,684)],"툴이 호출",lpos=(864,648),anchor="start")
# 저장소·외부
S.label(20,844,"저장소 · 설정 · 외부")
S.box(20,860,230,120,"PostgreSQL + pgvector",["fact · signal · sns_aggregate","regulation_chunk(embedding)","country_card · insight_report","review_label · as_of 스냅샷"],cls="db")
S.box(270,860,180,120,"객체 저장소",["원문 PDF·HTML·CSV","S3 또는 로컬 디스크","source_id ↔ 경로"],cls="db")
S.box(470,860,180,120,"설정 · 평가셋  (Git)",["weights.yaml (세트 4개)","regulation_questions.yaml","eval/ 정답셋 60문항"],cls="db")
S.el.append('<rect class="box" x="670" y="860" width="140" height="120" rx="8" stroke-dasharray="5 4"/>')
S.el.append('<text class="t" x="684" y="884">외부 데이터 API</text>')
for i,l in enumerate(["Comtrade · WDI","GDELT · RSS","YouTube · Reddit","Trends · KATI"]): S.el.append(f'<text class="s" x="684" y="{904+i*16}">{l}</text>')
S.el.append('<rect class="box llm" x="830" y="860" width="150" height="120" rx="8" stroke-dasharray="5 4"/>')
S.el.append('<text class="t" x="844" y="884">LLM API</text>')
for i,l in enumerate(["Responses API (생성)","  호출 지점 ①~⑧","Embeddings (벡터)","  청크·질의 임베딩"]): S.el.append(f'<text class="s" x="844" y="{904+i*16}">{l}</text>')
S.arrow([(135,750),(135,860)],"SQL 읽기/쓰기",lpos=(141,810),anchor="start")
S.arrow([(360,750),(360,860)],"원문 저장·조회",lpos=(366,810),anchor="start")
S.arrow([(560,750),(560,860)],"가중치·질문 로드",lpos=(566,810),anchor="start")
S.arrow([(90,750),(90,790),(740,790),(740,860)],"커넥터 → HTTP",lpos=(600,786))
S.arrow([(632,588),(632,620),(995,620),(995,840),(905,840),(905,860)],"생성 호출 (에이전트만)",lpos=(905,834),anchor="end")
S.arrow([(680,750),(680,800),(880,800),(880,860)],"임베딩 호출 (청킹·검색만)",lpos=(780,796))
S.el.append('<rect class="box" x="20" y="1020" width="960" height="44" rx="8" stroke-dasharray="6 4"/>')
S.label(36,1047,"운영: CI 평가 러너 (백테스트 · RAG 정답셋 · 신호 정밀도, PR마다) · 툴 호출 트레이스/로그 · 월 LLM 비용 리포트 · 시크릿은 환경변수",cls="l")
soft=S.svg("소프트웨어 아키텍처: 클라이언트, FastAPI 서버, 스케줄러 워커, OpenAI Agents SDK 런타임(에이전트 6종은 LLM, 툴과 가드레일은 프로그램), LLM 없는 핵심 모듈 8종, PostgreSQL·객체 저장소·설정, 외부 데이터 API와 LLM API. 생성 호출은 에이전트에서만, 임베딩은 청킹·검색에서만 나간다.")

# ---------- 5. 커버리지 깔때기 ----------
U=D(1000,300)
tiers=[(20,0,"Tier 0 · 193국 전부",["글로벌 API만 (Comtrade·WDI·GDELT·ePing)","자동 스크리닝 · 사람 손 안 탐","비용 ≈ 0, 월 1회"]),
       (360,20,"Tier 1 · 상위 40국",["+ 국가별 정부·세관·규제기관·관보","+ 매체 RSS 2~5 · GAIN·KOTRA 리포트","법령 RAG 5문항 · 월 1회"]),
       (640,40,"Tier 2 · 12국 심층",["+ SNS·커뮤니티·이커머스 신호","+ 현장 데이터 결합 · 거점 거리","주간 갱신 · 담당자 지정"]),
       (860,60,"TOP3",["추천 +","근거"])]
for i,(x,dy,t,l) in enumerate(tiers):
    w=[320,260,200,120][i]; h=200-dy*2
    U.box(x,40+dy,w,h,t,l,cls=["db","","llm","human"][i] if i!=1 else "")
    if i<3: U.arrow([(x+w,140),(x+w+20,140)])
U.label(180,268,"승격: 점수 상위 · 급등 신호 · 담당자 지정  |  강등: 3개월 연속 하위 · 소스 실패",cls="l")
U.label(500,290,"매달 인사이트 에이전트가 승격·강등을 제안하고 담당자가 확정한다. 깊이는 다르지만 193국 전부가 매달 점수를 받는다.",cls="l")
funnel=U.svg("커버리지 깔때기: 193국 전부를 글로벌 API로 스크리닝(Tier 0), 상위 40국에 국가별 소스와 법령 RAG를 붙이고(Tier 1), 12국은 SNS·이커머스·현장 데이터로 심층 분석(Tier 2)해 TOP3를 낸다. 매달 승격·강등.")

# ---------- 6. 품질 게이트 상세 ----------
G=D(1000,330)
G.cbox(20,60,120,80,["수집 결과","원문 + 파싱값","+ 출처 id"],"db")
G.arrow([(140,100),(170,100)],"100%",lpos=(155,34))
G.box(170,40,190,120,"1 규칙 검사  (코드)",["스키마 · 단위 · 범위","전월 대비 ±50% · 중복","통화·연도 누락"],cls="code")
G.arrow([(360,100),(390,100)],"95% 통과",lpos=(375,34))
G.box(390,40,200,120,"2 교차 검증  (코드)",["미러 통계: 관세청 ↔ Comtrade","두 소스 일치율 · 단위 환산","정의 태그 비교 (소매/도매)"],cls="code")
G.arrow([(590,100),(620,100)],"불일치·신규 10~15%만",lpos=(605,34))
G.box(620,40,210,120,"3 데이터 심사관  (LLM ⑧)",["출처 신뢰 · 정의 일치 · 시의성","충돌 시 채택 소스 + 사유","→ A/B/C · flags[] · reason"],cls="llm")
G.arrow([(830,100),(860,100)],"C등급·충돌 1~2%",lpos=(845,34))
G.cbox(860,60,120,80,["4 사람","승인 · 기각","블랙리스트"],"human")
G.arrow([(265,160),(265,200)],"탈락 → quarantine",lpos=(271,184),anchor="start")
G.arrow([(490,160),(490,200)],"일치 → A등급 저장",lpos=(496,184),anchor="start")
G.arrow([(725,160),(725,200)],"A/B 저장 · C 격리",lpos=(731,184),anchor="start")
G.arrow([(920,140),(920,200)],"라벨 → 심사관 평가셋",lpos=(914,184),anchor="end")
G.el.append('<rect class="box db" x="20" y="200" width="960" height="60" rx="8"/>')
G.el.append('<text class="t" x="34" y="224">사실 테이블 · quarantine</text>')
G.el.append('<text class="s" x="34" y="244">모든 행: value · source_id · confidence(A/B/C) · validity_flags[] · judge_reason · judged_at   —   스코어링은 C등급 가중치 절반, quarantine 은 읽지 않음</text>')
G.label(20,300,"LLM은 \"값이 얼마인가\"를 정하지 않는다. \"어느 값을 믿을 것인가\"와 \"왜\"만 정한다. 비율은 예상치이며 운영 후 실측으로 교체한다.",cls="l")
gate=G.svg("품질 게이트 4단: 규칙 검사와 교차 검증(코드)을 통과한 값은 A등급으로 바로 저장되고, 불일치·신규 10~15%만 LLM 데이터 심사관이 출처 신뢰·정의 일치·시의성·충돌 해결을 판정해 A/B/C 등급과 사유를 붙이며, C등급과 충돌 1~2%만 사람이 본다.")

import json
o=json.load(open("out.json")); o["soft"]=soft; o["funnel"]=funnel; o["gate"]=gate; json.dump(o,open("out.json","w"),ensure_ascii=False); print("soft",len(soft))
