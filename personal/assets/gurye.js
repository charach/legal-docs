/* ============================================================
   2026 IRONMAN 구례 · 코스 데이터 + 레이스 시뮬레이터
   출처: KTS 카페 68020 (김형식, 2026-09-10) + 거리표 엑셀 "2026 distance-0815-korea"
   gurye_course.html · gurye_fuel.html 이 공유한다.
   ============================================================ */
(function (global) {
  "use strict";

  /* ---------- 대회 기본 ---------- */
  var RACE = {
    date: "2026-10-04",
    athletes: 1160,
    startFirst: 7 * 60,            // 07:00 (분, 자정 기준)
    startLast: 7 * 60 + 19,        // 07:19 롤링 스타트 종료
    rolling: "5명씩 5~6초 간격",
    sunrise: 6 * 60 + 27,          // 구례 10/4 일출 약 06:27
    sunset: 18 * 60 + 11,          // 일몰 약 18:11
    dusk: 18 * 60 + 37,            // 시민박명 끝 약 18:37
    swimKm: 3.8,
    swimLapM: 1900,
    bikeKm: 176.68,
    runKm: 42.02,
    runLapKm: 9.92,
    runLaps: 4,
    runFinalKm: 2.34,
    limitH: 17,                    // 개인 스타트 기준 17시간
    officialEnd: 24 * 60 + 20      // 공식 종료 24:20
  };

  /* ---------- 컷오프 (시계 시각) ---------- */
  var CUTOFFS = [
    { leg: "bike", km: 86.73,  clock: 13 * 60 + 45, name: "1차 컷오프 · 남도대교 턴 86.7km" },
    { leg: "bike", km: 150.48, clock: 16 * 60 + 40, name: "2차 컷오프 · 냉천교차로 구례출구 150.5km" },
    { leg: "run",  km: 31.9,   clock: 23 * 60,      name: "런 컷오프 · 파크골프 입구 31.9km" },
    { leg: "finish", km: 42.02, clock: 24 * 60 + 20, name: "공식 종료 24:20 (개인 17시간)" }
  ];

  /* ---------- 바이크 랜드마크 (누적 km) ----------
     type: start · turn(U턴) · aid · pn · cut · mark · node · t2 */
  var BIKE = [
    { km: 0,      name: "T1 출발 · 지리산 호수공원", type: "start" },
    { km: 3.55,   name: "산동교차로 (3.5km 오르막 끝, 우회전)", type: "node" },
    { km: 4.82,   name: "산수관 턴", type: "turn", u: 1 },
    { km: 6.09,   name: "산동교차로 (좌회전)", type: "node" },
    { km: 10.44,  name: "자연드림 입구 · 10K", type: "mark" },
    { km: 11.19,  name: "죽정 버스정류장 (용산로 진입)", type: "node" },
    { km: 13.2,   name: "용냇골카페 교차로", type: "node" },
    { km: 13.5,   name: "용방교차로 턴 ①", type: "turn", u: 2 },
    { km: 15.2,   name: "AS1 · 산업도로 (첫 보급소)", type: "aid", aid: 1 },
    { km: 16.9,   name: "광의교차로", type: "node" },
    { km: 18.1,   name: "한성산업", type: "node" },
    { km: 19.6,   name: "냉천교차로 구례출구 · 20K", type: "mark" },
    { km: 21.5,   name: "문척교차로 아래", type: "node" },
    { km: 21.76,  name: "산이고운아파트 턴 ①", type: "turn", u: 3 },
    { km: 23.08,  name: "구성교차로 (문척교 건너) · T자 순환 1회전 시작", type: "node", loop: "T1" },
    { km: 29.6,   name: "대평로터리 · 30K", type: "mark" },
    { km: 30.0,   name: "백운관 (간전 방향 진입)", type: "node" },
    { km: 34.03,  name: "논곡 턴 ①", type: "turn", u: 4 },
    { km: 36.03,  name: "수평(삼산)마을", type: "node" },
    { km: 38.5,   name: "대평로터리", type: "node" },
    { km: 38.99,  name: "AS2 · 양동마을 ① · 40K", type: "aid", aid: 2 },
    { km: 44.07,  name: "백운천 휴게소 (1회전 · PN 사용 불가)", type: "node" },
    { km: 47.27,  name: "남도대교 턴 ① · 50K", type: "turn", u: 5 },
    { km: 50.47,  name: "백운천 휴게소 · PN (1회전은 통과)", type: "node" },
    { km: 53.77,  name: "무수내 쉼터", type: "node" },
    { km: 56.04,  name: "대평로터리", type: "node" },
    { km: 58.74,  name: "AS3 · 오봉산가든 ① · 60K", type: "aid", aid: 3 },
    { km: 62.54,  name: "구성교차로 · 1회전 완료 (39.5km) → 2회전", type: "node", loop: "T2" },
    { km: 69.06,  name: "대평로터리 · 70K", type: "mark" },
    { km: 69.46,  name: "백운관", type: "node" },
    { km: 73.49,  name: "논곡 턴 ②", type: "turn", u: 6 },
    { km: 75.49,  name: "수평(삼산)마을", type: "node" },
    { km: 77.96,  name: "대평로터리", type: "node" },
    { km: 78.45,  name: "AS2 · 양동마을 ② · 80K", type: "aid", aid: 2 },
    { km: 83.53,  name: "백운천 휴게소", type: "node" },
    { km: 86.73,  name: "남도대교 턴 ② · 1차 컷오프 13:45", type: "turn", u: 7, cut: 0 },
    { km: 89.93,  name: "PN · 백운천 휴게소 (2회전 · 퍼스널니즈 사용) · 90K", type: "pn" },
    { km: 93.23,  name: "무수내 쉼터", type: "node" },
    { km: 95.5,   name: "대평로터리", type: "node" },
    { km: 98.2,   name: "AS3 · 오봉산가든 ② · 100K", type: "aid", aid: 3 },
    { km: 102.0,  name: "구성교차로 · 2회전 완료 → 문척교 건너 산이고운", type: "node", loop: "N1" },
    { km: 103.06, name: "문척교차로 아래", type: "node" },
    { km: 103.32, name: "산이고운아파트 턴 ②", type: "turn", u: 8 },
    { km: 103.58, name: "문척교차로 아래 (산업도로 진입)", type: "node" },
    { km: 105.68, name: "스카이바이크", type: "node" },
    { km: 107.88, name: "구례1교 턴 ① · 110K", type: "turn", u: 9 },
    { km: 110.08, name: "스카이바이크", type: "node" },
    { km: 112.18, name: "문척교차로", type: "node" },
    { km: 115.58, name: "한성산업", type: "node" },
    { km: 116.78, name: "광의교차로", type: "node" },
    { km: 120.18, name: "용방교차로 턴 ② · 120K · 산업도로 순환 1회전", type: "turn", u: 10, loop: "N2" },
    { km: 121.88, name: "AS1 ②", type: "aid", aid: 1 },
    { km: 123.38, name: "광의교차로", type: "node" },
    { km: 124.58, name: "한성산업", type: "node" },
    { km: 126.08, name: "냉천교차로 구례출구 (통과)", type: "node" },
    { km: 127.98, name: "문척교차로", type: "node" },
    { km: 130.08, name: "스카이바이크 · 130K", type: "mark" },
    { km: 132.28, name: "구례1교 턴 ②", type: "turn", u: 11 },
    { km: 134.48, name: "스카이바이크", type: "node" },
    { km: 136.58, name: "문척교차로", type: "node" },
    { km: 139.98, name: "한성산업 · 140K", type: "mark" },
    { km: 141.18, name: "광의교차로", type: "node" },
    { km: 144.58, name: "용방교차로 턴 ③ · 순환 2회전", type: "turn", u: 12, loop: "N3" },
    { km: 146.28, name: "AS1 ③", type: "aid", aid: 1 },
    { km: 147.78, name: "광의교차로", type: "node" },
    { km: 148.98, name: "한성산업 · 150K", type: "mark" },
    { km: 150.48, name: "냉천교차로 구례출구 · 2차 컷오프 16:40", type: "cut", cut: 1 },
    { km: 152.38, name: "문척교차로", type: "node" },
    { km: 154.48, name: "스카이바이크", type: "node" },
    { km: 156.68, name: "구례1교 턴 ③", type: "turn", u: 13 },
    { km: 158.88, name: "스카이바이크", type: "node" },
    { km: 160.98, name: "문척교차로 · 160K", type: "mark" },
    { km: 164.38, name: "한성산업", type: "node" },
    { km: 165.58, name: "광의교차로", type: "node" },
    { km: 168.98, name: "용방교차로 턴 ④ · 170K · 순환 3회전 끝 (마지막 U턴)", type: "turn", u: 14, loop: "N4" },
    { km: 170.68, name: "AS1 ④ (마지막 보급소)", type: "aid", aid: 1 },
    { km: 172.18, name: "광의교차로", type: "node" },
    { km: 173.38, name: "한성산업", type: "node" },
    { km: 174.88, name: "냉천교차로 구례출구 → 서시천 뚝방", type: "node" },
    { km: 176.6,  name: "정장교 좌회전 · 10km/h 이하 감속", type: "node" },
    { km: 176.68, name: "T2 하차선 (좌회전 후 80m)", type: "t2" }
  ];

  /* ---------- 런 1바퀴 (9.92km) ---------- */
  var RUN_LAP = [
    { km: 0,    name: "시작점 (T2 · 운동장 앞)", type: "start" },
    { km: 0.9,  name: "서시교 턴 · 랩밴드", type: "turn" },
    { km: 1.38, name: "AS1 · 황현선생 동상 앞", type: "aid", aid: 1 },
    { km: 1.48, name: "런 퍼스널니즈 (분수광장)", type: "pn" },
    { km: 1.8,  name: "시작점 앞 통과", type: "node" },
    { km: 2.14, name: "파크골프 앞", type: "node" },
    { km: 3.19, name: "AS2 · 광의대교 아래", type: "aid", aid: 2 },
    { km: 4.19, name: "광의교 서단", type: "node" },
    { km: 4.34, name: "사림마을 로터리 (도로 구간 1.2km 시작)", type: "node" },
    { km: 5.27, name: "AS3", type: "aid", aid: 3 },
    { km: 5.48, name: "KBS 로터리 턴", type: "turn" },
    { km: 6.62, name: "사림마을 로터리", type: "node" },
    { km: 6.77, name: "광의교 서단", type: "node" },
    { km: 6.95, name: "꽃강 턴", type: "turn" },
    { km: 7.31, name: "광의교 동단", type: "node" },
    { km: 7.69, name: "AS4", type: "aid", aid: 4 },
    { km: 8.16, name: "광의대교", type: "node" },
    { km: 9.06, name: "갑동굴다리 앞", type: "node" },
    { km: 9.33, name: "AS5", type: "aid", aid: 5 },
    { km: 9.54, name: "정장교 서단", type: "node" },
    { km: 9.58, name: "파크골프 앞", type: "node" },
    { km: 9.92, name: "시작점 · 1바퀴 완료", type: "lap" }
  ];
  var RUN_FINAL = [
    { km: 0.9,  name: "서시교 앞 턴 (마지막)", type: "turn" },
    { km: 1.38, name: "AS1 (21번째 보급소)", type: "aid", aid: 1 },
    { km: 1.48, name: "런 퍼스널니즈 (마지막 통과)", type: "pn" },
    { km: 1.8,  name: "시작점 앞", type: "node" },
    { km: 2.14, name: "파크골프 앞 → 운동장 진입", type: "node" },
    { km: 2.34, name: "피니시 · 공설운동장", type: "finish" }
  ];

  /* 런 전체 랜드마크 전개 */
  function runAll() {
    var out = [];
    for (var lap = 0; lap < RACE.runLaps; lap++) {
      RUN_LAP.forEach(function (p) {
        if (lap > 0 && p.km === 0) return;
        var o = Object.assign({}, p);
        o.km = +(lap * RACE.runLapKm + p.km).toFixed(2);
        o.lap = lap + 1;
        if (p.type === "lap") o.name = "시작점 · " + (lap + 1) + "바퀴 완료";
        if (p.type === "aid") o.name = "AS" + p.aid + " (" + (lap + 1) + "바퀴)";
        if (p.type === "pn") o.name = "런 퍼스널니즈 (" + (lap + 1) + "바퀴)";
        if (o.km >= 31.85 && o.km <= 31.95) { o.type = "cut"; o.name = "파크골프 앞 · 런 컷오프 23:00 (31.9km)"; }
        out.push(o);
      });
    }
    RUN_FINAL.forEach(function (p) {
      var o = Object.assign({}, p);
      o.km = +(RACE.runLaps * RACE.runLapKm + p.km).toFixed(2);
      o.lap = 5;
      out.push(o);
    });
    return out;
  }

  /* ---------- 보급소 품목 ---------- */
  var AID_BIKE_ORDER = ["물통 버리는 곳", "물", "물", "게토레이", "게토레이", "바나나 ½", "에너지젤", "게토레이", "게토레이", "물", "물", "화장실"];
  var AID_RUN_ORDER = ["스펀지", "물", "게토레이 · 콜라", "음식 (오렌지·바나나·비스킷·젤·소금·포도당정)", "게토레이 · 콜라", "물", "물품 (선크림·바세린·에어파스)", "화장실", "스펀지"];

  /* ---------- 시계 포맷 ---------- */
  function hhmm(min) {
    if (min == null || isNaN(min)) return "—";
    var m = Math.round(min);
    var h = Math.floor(m / 60), mm = m % 60;
    return (h < 10 ? "0" : "") + h + ":" + (mm < 10 ? "0" : "") + mm;
  }
  function dur(min) {
    if (min == null || isNaN(min)) return "—";
    var neg = min < 0; min = Math.abs(min);
    var m = Math.round(min);
    var h = Math.floor(m / 60), mm = m % 60;
    return (neg ? "−" : "") + h + ":" + (mm < 10 ? "0" : "") + mm;
  }
  function pace(sPerKm) {
    var m = Math.floor(sPerKm / 60), s = Math.round(sPerKm % 60);
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  /* ---------- 시뮬레이터 ----------
     p = {
       startOffset (분, 0~19), swimPace (초/100m), t1 (분),
       bikeSpeed (km/h, 이동 평속), uturnLoss (초/개), aidLoss (초/개), pnStop (분),
       t2 (분), runPace (초/km, 뛰는 구간), walkPace (초/km), runMin, walkMin,
       fade (바퀴당 %, 0~10), aidWalk (초/보급소)
     } */
  var DEFAULT = {
    startOffset: 12, swimPace: 158, t1: 10,
    bikeSpeed: 28, uturnLoss: 12, aidLoss: 20, pnStop: 1,
    t2: 10, runPace: 360, walkPace: 540, runMin: 4, walkMin: 1,
    fade: 3, aidWalk: 10
  };

  function runCyclePace(p) {
    // 걷뛰 평균 페이스 (초/km)
    var distKm = (p.runMin * 60) / p.runPace + (p.walkMin * 60) / p.walkPace;
    return ((p.runMin + p.walkMin) * 60) / distKm;
  }

  function simulate(input) {
    var p = Object.assign({}, DEFAULT, input || {});
    var start = RACE.startFirst + p.startOffset;         // 시계(분)
    var swimMin = (RACE.swimKm * 1000 / 100) * p.swimPace / 60;
    var swimEnd = swimMin;
    var t1End = swimEnd + p.t1;

    // 바이크
    var bikeMarks = [];
    var u = 0, a = 0, pnDone = false;
    BIKE.forEach(function (b) {
      var t = b.km / p.bikeSpeed * 60;                  // 분
      t += u * p.uturnLoss / 60 + a * p.aidLoss / 60 + (pnDone ? p.pnStop : 0);
      var el = t1End + t;
      bikeMarks.push(Object.assign({}, b, { elapsed: el, clock: start + el, legT: t }));
      if (b.type === "turn") u++;
      if (b.type === "aid") a++;
      if (b.type === "pn") pnDone = true;
    });
    var bikeEnd = bikeMarks[bikeMarks.length - 1].elapsed;
    var t2End = bikeEnd + p.t2;

    // 런
    var base = runCyclePace(p);
    var runMarks = [];
    var all = runAll();
    var aidCount = 0;
    all.forEach(function (r) {
      var t = 0, remain = r.km, lap = 0;
      while (remain > 0) {
        var lapLen = Math.min(remain, RACE.runLapKm);
        var lapPace = base * Math.pow(1 + p.fade / 100, lap);
        t += lapLen * lapPace / 60;
        remain -= lapLen; lap++;
      }
      t += aidCount * p.aidWalk / 60;
      var el = t2End + t;
      runMarks.push(Object.assign({}, r, { elapsed: el, clock: start + el, legT: t }));
      if (r.type === "aid") aidCount++;
    });
    var finish = runMarks[runMarks.length - 1].elapsed;

    // 컷오프 여유
    var cuts = CUTOFFS.map(function (c) {
      var arrive;
      if (c.leg === "bike") arrive = start + t1End + interp(BIKE, bikeMarks, c.km);
      else if (c.leg === "run") arrive = start + t2End + interpRun(runMarks, c.km);
      else arrive = start + finish;
      return Object.assign({}, c, { arrive: arrive, margin: c.clock - arrive });
    });

    return {
      p: p, start: start,
      swimMin: swimMin, swimEnd: swimEnd, t1End: t1End,
      bike: bikeMarks, bikeMin: bikeEnd - t1End, bikeEnd: bikeEnd, t2End: t2End,
      run: runMarks, runMin: finish - t2End, runPaceAvg: base, finish: finish,
      finishClock: start + finish, cutoffs: cuts,
      sunsetElapsed: RACE.sunset - start,
      limitClock: start + RACE.limitH * 60
    };
  }
  function interp(list, marks, km) {
    for (var i = 1; i < marks.length; i++) {
      if (marks[i].km >= km) {
        var a = marks[i - 1], b = marks[i];
        var f = (km - a.km) / (b.km - a.km || 1);
        return a.legT + f * (b.legT - a.legT);
      }
    }
    return marks[marks.length - 1].legT;
  }
  function interpRun(marks, km) {
    for (var i = 1; i < marks.length; i++) {
      if (marks[i].km >= km) {
        var a = marks[i - 1], b = marks[i];
        var f = (km - a.km) / (b.km - a.km || 1);
        return a.legT + f * (b.legT - a.legT);
      }
    }
    return marks[marks.length - 1].legT;
  }

  /* 누적 km → 경과 분 (바이크), 애니메이션용 */
  function bikeKmToElapsed(sim, km) { return sim.t1End + interp(BIKE, sim.bike, km); }
  function bikeElapsedToKm(sim, el) {
    var m = sim.bike;
    if (el <= m[0].elapsed) return 0;
    for (var i = 1; i < m.length; i++) {
      if (m[i].elapsed >= el) {
        var a = m[i - 1], b = m[i];
        var f = (el - a.elapsed) / (b.elapsed - a.elapsed || 1);
        return a.km + f * (b.km - a.km);
      }
    }
    return RACE.bikeKm;
  }
  function runElapsedToKm(sim, el) {
    var m = sim.run;
    if (el <= sim.t2End) return 0;
    var prevKm = 0, prevEl = sim.t2End;
    for (var i = 0; i < m.length; i++) {
      if (m[i].elapsed >= el) {
        var f = (el - prevEl) / (m[i].elapsed - prevEl || 1);
        return prevKm + f * (m[i].km - prevKm);
      }
      prevKm = m[i].km; prevEl = m[i].elapsed;
    }
    return RACE.runKm;
  }

  /* ---------- 폴리라인 유틸 (SVG 애니메이션) ---------- */
  function polyLen(pts) {
    var L = [0];
    for (var i = 1; i < pts.length; i++) {
      var dx = pts[i][0] - pts[i - 1][0], dy = pts[i][1] - pts[i - 1][1];
      L.push(L[i - 1] + Math.sqrt(dx * dx + dy * dy));
    }
    return L;
  }
  function pointAt(pts, L, f) {
    var target = f * L[L.length - 1];
    for (var i = 1; i < L.length; i++) {
      if (L[i] >= target) {
        var a = pts[i - 1], b = pts[i];
        var t = (target - L[i - 1]) / (L[i] - L[i - 1] || 1);
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
      }
    }
    return pts[pts.length - 1];
  }

  global.GURYE = {
    RACE: RACE, CUTOFFS: CUTOFFS, BIKE: BIKE, RUN_LAP: RUN_LAP, RUN_FINAL: RUN_FINAL,
    runAll: runAll, AID_BIKE_ORDER: AID_BIKE_ORDER, AID_RUN_ORDER: AID_RUN_ORDER,
    DEFAULT: DEFAULT, simulate: simulate, runCyclePace: runCyclePace,
    bikeKmToElapsed: bikeKmToElapsed, bikeElapsedToKm: bikeElapsedToKm, runElapsedToKm: runElapsedToKm,
    hhmm: hhmm, dur: dur, pace: pace, polyLen: polyLen, pointAt: pointAt,
    load: function (key, fallback) { try { var v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; } },
    save: function (key, v) { try { localStorage.setItem(key, JSON.stringify(v)); } catch (e) {} }
  };
})(window);
