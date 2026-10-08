import {useState} from 'react';
type Indicator={company_code:string;period:string;scope:string;metric_code:string;formula_version:string;dataset_sha256:string};
type Event={id:number;period:string;scope:string;metric_code:string;dataset_sha256:string;decision:string;reviewer:string;justification:string;created_at:string;event_hash:string};
export default function ReviewPanel({workspace,apiKey,company,rows}:{workspace:string;apiKey:string;company:string;rows:Indicator[]}){
 const [selected,setSelected]=useState(0);
 const [reviewer,setReviewer]=useState('');
 const [reviewKey,setReviewKey]=useState('');
 const [decision,setDecision]=useState<'approved'|'rejected'>('rejected');
 const [justification,setJustification]=useState('');
 const [events,setEvents]=useState<Event[]>([]);
 const [error,setError]=useState('');
 const [busy,setBusy]=useState(false);
 const [message,setMessage]=useState('');
 const base='/api/v1/workspaces/'+encodeURIComponent(workspace)+'/cvm/';
 async function call(url:string,init:RequestInit={}){
  const r=await fetch(base+url,{...init,headers:{'X-Workspace-Key':apiKey,...init.headers}});
  const data=await r.json();
  if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:'Erro de revisão');
  return data;
 }
 async function refresh(){
  if(!company)return;
  const data=await call(encodeURIComponent(company)+'/reviews');
  setEvents(data.events);
 }
 async function submit(){
  const row=rows[selected];
  if(!row)return;
  setError('');setMessage('');setBusy(true);
  try{
   await call('indicators/reviews',{method:'POST',headers:{'Content-Type':'application/json','X-Review-Key':reviewKey},
    body:JSON.stringify({company_code:row.company_code,period:row.period,scope:row.scope,
      metric_code:row.metric_code,formula_version:row.formula_version,dataset_sha256:row.dataset_sha256,
      reviewer:reviewer.trim(),decision,justification:justification.trim()})});
   await refresh();setMessage('Decisão registrada no histórico local. Identidade do revisor não verificada.');
   setJustification('');
  }catch(e){setError(e instanceof Error?e.message:'Falha ao registrar');}
  finally{setBusy(false);}
 }
 return <section className="dfp-review"><h3>Revisão humana</h3>
  <p>Registre uma decisão sobre uma versão específica do indicador. O histórico não substitui autenticação individual nem certificação contábil.</p>
  <label>Indicador e versão<select value={Math.min(selected,Math.max(0,rows.length-1))} onChange={e=>setSelected(Number(e.target.value))}>
   {rows.map((r,i)=><option key={r.metric_code+r.dataset_sha256+i} value={i}>{r.metric_code} · {r.period} · {r.dataset_sha256.slice(0,12)}</option>)}
  </select></label>
  <label>Chave de permissão para revisão<input type="password" autoComplete="off" value={reviewKey} onChange={e=>setReviewKey(e.target.value)} placeholder="FINSIGHT_REVIEW_API_KEY"/></label>
  <label>Identificador declarado do revisor<input value={reviewer} onChange={e=>setReviewer(e.target.value)} placeholder="reviewer-01"/></label>
  <label>Decisão<select value={decision} onChange={e=>setDecision(e.target.value as 'approved'|'rejected')}>
   <option value="rejected">Rejeitar</option><option value="approved">Aprovar revisão manual</option>
  </select></label>
  <label>Justificativa<textarea rows={3} minLength={15} maxLength={2000} value={justification} onChange={e=>setJustification(e.target.value)} placeholder="Descreva as contas e documentos conferidos"/></label>
  <div className="dfp-actions">
   <button disabled={!apiKey||!reviewKey||busy||!rows.length||reviewer.trim().length<3||justification.trim().length<15} onClick={submit}>Registrar decisão</button>
   <button disabled={!apiKey||busy||!company} onClick={()=>{setError('');refresh().catch(e=>setError(String(e)));}}>Atualizar histórico</button>
  </div>
  {error&&<p role="alert" className="workbench-error">{error}</p>}
  {message&&<p role="status" className="workbench-success">{message}</p>}
  <h4>Histórico de decisões ({events.length})</h4>
  {events.map(event=><article className="dfp-review-event" key={event.id}>
   <strong>#{event.id} · {event.decision==='approved'?'Revisão aprovada':'Rejeitado'}</strong>
   <p>{event.metric_code} · {event.period} · Revisor declarado: {event.reviewer}</p>
   <p>{event.justification}</p><small>{event.created_at} · Hash do evento: {event.event_hash}</small>
  </article>)}
 </section>;
}
