import {useState} from 'react';
import {GitCompare, Plus, Trash2, ShieldAlert} from 'lucide-react';
import './comparison.css';
import {useAuth,userAuthMode,authHeaders} from './auth';

type Sector='bank'|'retail'|'software'|'industrial';
type Metric='roe'|'operating_margin'|'net_debt_ebitda'|'npl_ratio'|'recurring_revenue_ratio';
type Row={id:number;company_id:string;sector:Sector;value:string;source_ids:string};
type Result={metric:string;period:string;comparison_type:string;methodology:string;ranked:boolean;
  evidence_status:string;notice:string;results:{company_id:string;sector:string;value:string;source_ids:string[]}[]};
const labels:Record<Metric,string>={
  roe:'ROE',operating_margin:'Margem operacional',net_debt_ebitda:'Dívida líquida / EBITDA',
  npl_ratio:'Inadimplência (NPL)',recurring_revenue_ratio:'Receita recorrente'
};
const sectors:Record<Sector,string>={bank:'Bancos',retail:'Varejo',software:'Software',industrial:'Indústria'};
const allowed:Record<Metric,Sector[]>={
  roe:['bank','retail','software','industrial'],
  operating_margin:['retail','software','industrial'],
  net_debt_ebitda:['retail','software','industrial'],
  npl_ratio:['bank'],
  recurring_revenue_ratio:['software']
};
const initial:Row[]=[{id:1,company_id:'',sector:'retail',value:'',source_ids:''},
  {id:2,company_id:'',sector:'retail',value:'',source_ids:''}];
export default function ComparisonWorkbench({multisector}:{multisector:boolean}){
 const {session}=useAuth();
 const [rows,setRows]=useState<Row[]>(initial);
 const [metric,setMetric]=useState<Metric>('roe');
 const [period,setPeriod]=useState('2025-FY');
 const [workspace,setWorkspace]=useState('local');
 const effectiveWorkspace=userAuthMode?(session?.workspace??''):workspace;
 const [apiKey,setApiKey]=useState('');
 const authorized=userAuthMode?!!session:!!apiKey;
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [result,setResult]=useState<Result|null>(null);
 function update(id:number,field:keyof Omit<Row,'id'>,value:string){
   setRows(previous=>previous.map(r=>r.id===id?{...r,[field]:value}:r));setResult(null);
 }
 async function submit(){
   setError('');setResult(null);
   const names=new Set(rows.map(r=>r.company_id.trim().toLowerCase()));
   if(names.size!==rows.length || names.has('')){setError('Informe identificadores únicos para todas as empresas.');return;}
   if(!multisector&&new Set(rows.map(r=>r.sector)).size!==1){setError('Selecione o mesmo setor para todas as empresas.');return;}
   if(rows.some(r=>!allowed[metric].includes(r.sector))){setError('O indicador selecionado não é aplicável a todos os setores.');return;}
   if(rows.some(r=>!r.value.trim()||!Number.isFinite(Number(r.value))||!r.source_ids.trim())){setError('Preencha valores numéricos e referências de documentos.');return;}
   if(!/^\d{4}-(FY|Q[1-4])$/.test(period)){setError('Use o período AAAA-FY ou AAAA-Q1...Q4.');return;}
   setBusy(true);
   try{
     const observations=rows.map(r=>({company_id:r.company_id.trim(),sector:r.sector,metric,period,
       value:r.value.trim(),formula_version:'manual-v1',source_ids:r.source_ids.split(',').map(s=>s.trim()).filter(Boolean)}));
     const response=await fetch('/api/v1/workspaces/'+encodeURIComponent(effectiveWorkspace.trim())+'/comparisons/validate',
       {method:'POST',headers:{'Content-Type':'application/json',...authHeaders(session,apiKey)},body:JSON.stringify({observations})});
     const body=await response.json();
     if(!response.ok)throw new Error(typeof body.detail==='string'?body.detail:'API rejeitou os dados ('+response.status+')');
     setResult(body as Result);
   }catch(e){setError(e instanceof Error?e.message:'Não foi possível realizar a comparação.');}
   finally{setBusy(false);}
 }
 return <section className="comparison-workbench">
   <div className="eyebrow">VALIDAÇÃO FINANCEIRA / {multisector?'MULTISSETORIAL':'SETORIAL'}</div>
   <h2>Comparação com metodologia explícita.</h2>
   <p>Preencha indicadores e referências documentais. O motor valida a compatibilidade, mas <strong>não verifica automaticamente os números informados</strong>.</p>
   <div className="notice"><ShieldAlert size={19}/><span>Ambiente local. Os resultados são entradas do usuário não verificadas. Não há ranking ou recomendação financeira.</span></div>
   <div className="comparison-controls">
     {!userAuthMode&&<label>Workspace<input value={workspace} onChange={e=>setWorkspace(e.target.value)}/></label>}
     {!userAuthMode&&<label>Chave de acesso<input type="password" autoComplete="off" value={apiKey} onChange={e=>setApiKey(e.target.value)}/></label>}
     <label>Indicador<select value={metric} onChange={e=>{setMetric(e.target.value as Metric);setResult(null);}}>{Object.entries(labels).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
     <label>Período<input value={period} onChange={e=>setPeriod(e.target.value)} placeholder="2025-FY"/></label>
   </div>
   <div className="comparison-rows">{rows.map((r,i)=><div className="comparison-row" key={r.id}>
      <strong>Empresa {i+1}</strong>
      <label>Identificador<input value={r.company_id} onChange={e=>update(r.id,'company_id',e.target.value)} placeholder="empresa-001"/></label>
      <label>Setor<select value={r.sector} onChange={e=>update(r.id,'sector',e.target.value)}>{Object.entries(sectors).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
      <label>Valor<input type="number" step="any" value={r.value} onChange={e=>update(r.id,'value',e.target.value)} placeholder="12.50"/></label>
      <label>IDs das fontes<input value={r.source_ids} onChange={e=>update(r.id,'source_ids',e.target.value)} placeholder="documento-001"/></label>
      <button className="remove-row" title="Remover empresa" aria-label={'Remover empresa '+(i+1)} disabled={rows.length<=2} onClick={()=>setRows(v=>v.filter(x=>x.id!==r.id))}><Trash2 size={17}/></button>
   </div>)}</div>
   <div className="comparison-actions">
     <button onClick={()=>{setRows(v=>[...v,{id:Math.max(...v.map(x=>x.id))+1,company_id:'',sector:multisector?'software':v[0].sector,value:'',source_ids:''}]);setResult(null);}} disabled={rows.length>=50}><Plus size={16}/> Adicionar empresa</button>
     <button className="comparison-primary" disabled={busy||!authorized||!effectiveWorkspace.trim()} onClick={submit}><GitCompare size={16}/>{busy?'Validando…':'Validar comparação'}</button>
   </div>
   {error&&<p role="alert" className="workbench-error">{error}</p>}
   {result&&<div className="comparison-result" role="status">
     <div className="eyebrow">RESULTADO • ENTRADAS NÃO VERIFICADAS</div>
     <h3>{labels[result.metric as Metric]??result.metric} · {result.period}</h3>
     <p>{result.comparison_type==='cross_sector'?'Comparação entre setores com metodologia comum.':'Comparação no mesmo setor.'} Nenhum ranking foi gerado.</p>
     <div className="comparison-table"><div className="comparison-table-head"><strong>Empresa</strong><strong>Setor</strong><strong>Valor informado</strong></div>
       {result.results.map((r,i)=><div className="comparison-table-row" key={r.company_id+'-'+i}>
         <span>{r.company_id}<small>Fontes declaradas: {r.source_ids.join(', ')}</small></span>
         <span>{sectors[r.sector as Sector]??r.sector}</span><strong>{r.value}</strong>
       </div>)}
     </div><p className="comparison-disclaimer">{result.notice}</p>
   </div>}
 </section>;
}
