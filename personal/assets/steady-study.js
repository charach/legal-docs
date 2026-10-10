const {weeks,homeRanges,koreanRanges}=window.PLAN;
const start=Date.UTC(2026,9,12), end=Date.UTC(2027,0,30), days=['일','월','화','수','목','금','토'];
const iso=d=>new Date(d).toISOString().slice(0,10);
const short=d=>{const t=new Date(d);return (t.getUTCMonth()+1)+'/'+t.getUTCDate()};
document.getElementById('weeks').innerHTML=weeks.map((w,i)=>'<article class="week"><span class="number">WEEK '+String(i+1).padStart(2,'0')+'</span><h3>'+w[0]+'</h3><p>'+w[1]+'</p><time>'+short(start+i*604800000)+' — '+short(Math.min(end-(i===15?86400000:0),start+i*604800000+518400000))+'</time></article>').join('');
document.getElementById('home').innerHTML=homeRanges.map(([a,b,t])=>'<li><b>'+t+'</b><span>'+short(start+(a-1)*604800000)+'~'+short(Math.min(Date.UTC(2027,0,29),start+(b-1)*604800000+518400000))+'</span></li>').join('');
document.getElementById('korean').innerHTML=koreanRanges.map(r=>'<tr>'+r.map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('');
let records={};let storageOK=true;try{records=JSON.parse(localStorage.getItem('steady-study-v1')||'{}')}catch{storageOK=false}
if(!records||typeof records!=='object'||Array.isArray(records))records={};
const picker=document.getElementById('date');
const seoul=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());const part=t=>seoul.find(p=>p.type===t).value;
const now=part('year')+'-'+part('month')+'-'+part('day');
picker.value=now<'2026-10-12'?'2026-10-12':now>'2027-01-30'?'2027-01-30':now;
function render(){
const date=picker.value,stamp=Date.parse(date+'T00:00:00Z');
if(!Number.isFinite(stamp)||stamp<start||stamp>end)return;
const day=new Date(stamp).getUTCDay(),wi=Math.min(15,Math.floor((stamp-start)/604800000)),last=stamp>=Date.UTC(2027,0,25),final=date==='2027-01-30';
document.getElementById('day-title').textContent=short(stamp)+' ('+days[day]+') · '+(wi+1)+'주차';
let tasks=[];
if(final){tasks=[['기사','최종 모의고사 또는 시험 응시','실제 시험일이면 응시하고, 아니면 최종 점검 후 복습을 이어가세요.']]}
else if(day===0){tasks=[['휴식','보충 또는 휴식','밀린 공부가 있을 때만 최대 90분. 충분히 쉬어도 괜찮아요.']]}
else{
const base=[0,65,65,60,65,60,60][day];const korean=(day%2===1?'화법과 작문':'언어와 매체');const km=last?10:([1,2,4].includes(day)?25:20);
tasks.push(['기사','정보처리기사 · '+(last?base+([1,2,4].includes(day)?15:10):base)+'분',weeks[wi][0]+' — '+(day===5?'이번 주 오답 재풀이':day===6?'누적 문제 풀이':weeks[wi][1])]);
tasks.push(['국어',korean+' · '+km+'분',last?'표시한 문제와 개념 복습':wi<4?(korean==='화법과 작문'?'지문 묶음 1개, 선지의 근거 확인':'개념 확인 후 관련 문제 3~5개'):wi<8?'다음 단원을 목차 순서대로':day>=5?'이번 주 오답 재풀이':'다음 새 문제와 해설 확인']);
if([3,5,6].includes(day)){const h=homeRanges.find(r=>wi+1>=r[0]&&wi+1<=r[1]);tasks.push(['독서','살림책 · 10분',h[2]+' — 읽던 곳부터 소제목 2~4개'])}}
const target=document.getElementById('tasks');target.replaceChildren();
tasks.forEach(([id,title,desc])=>{const label=document.createElement('label');label.className='task';const input=document.createElement('input');input.type='checkbox';input.checked=!!records[date+'-'+id];const body=document.createElement('span'),b=document.createElement('b'),small=document.createElement('small');b.textContent=title;small.textContent=desc;body.append(b,small);label.append(input,body);target.append(label);input.addEventListener('change',()=>{records[date+'-'+id]=input.checked;try{localStorage.setItem('steady-study-v1',JSON.stringify(records))}catch{storageOK=false}update()})});
function update(){document.getElementById('done-count').textContent=[...target.querySelectorAll('input')].filter(i=>i.checked).length+' / '+tasks.length+' 완료'+(storageOK?'':' · 기록 저장 불가')}update()
}
picker.addEventListener('change',render);render();