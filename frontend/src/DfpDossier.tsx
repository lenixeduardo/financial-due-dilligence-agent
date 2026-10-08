import {useState} from 'react';
import {FileArchive, FileDown, FileCheck2} from 'lucide-react';
import './dfp-dossier.css';
import ReviewPanel from './ReviewPanel';

type Indicator={metric_code:string;period:string;scope:string;value_decimal:string;formula_version:string;dataset_sha256:string;account_codes:string;status:string;company_code:string};
type Computed={metric_code:string;period:string;scope:string;value:string;formula_version:string;source_sha256:string;account_codes:string[];status:string};
const names:Record<string,string>={operating_margin:'Margem operacional',net_margin:'Margem líquida',current_ratio:'Liquidez corrente'};
const formulas:Record<string,string>={operating_margin:'DRE 3.05 ÷ DRE 3.01',net_margin:'DRE 3.11 ÷ DRE 3.01',current_ratio:'BPA 1.01 ÷ BPP 2.01'};
type Report={status:string;company_code:string;generated_at:string;review_status:'not_reviewed';indicators:Indicator[]};
function readBase64(file:File):Promise<string>{return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>{const value=reader.result;if(typeof value==='string')resolve(value.split(',')[1]??'');else reject(new Error('Falha de leitura'));};reader.onerror=()=>reject(new Error('Falha de leitura'));reader.readAsDataURL(file);});}
export default function DfpDossier(){
 const [workspace,setWorkspace]=useState('local');
 const [key,setKey]=useState('');
 const [company,setCompany]=useState('');
 const [year,setYear]=useState('2025');
 const [file,setFile]=useState<File|null>(null);
 const [rows,setRows]=useState<Indicator[]>([]);
 const [message,setMessage]=useState('');
 const [error,setError]=useState('');
 const [busy,setBusy]=useState(false);
 const base='/api/v1/workspaces/'+encodeURIComponent(workspace.trim());
 async function request(path:string, options:RequestInit={}){
  const response=await fetch(base+path,{...options,headers:{'X-Workspace-Key':key,...options.headers}});
  const json=await response.json().catch(()=>({detail:'Resposta inválida'}));
  if(!response.ok)throw new Error(typeof json.detail==='string'?json.detail:'Erro na API ('+response.status+')');
  return json;
 }
 async function refresh(){
   const data=await request('/cvm/'+encodeURIComponent(company.trim())+'/indicators');
   setRows(data.indicators as Indicator[]);
 }
 async function load(){
  setError('');setMessage('');setBusy(true);
  try{await refresh();setMessage('Indicadores consultados. A origem ainda precisa de revisão.');}
  catch(e){setError(e instanceof Error?e.message:'Erro inesperado');}
  finally{setBusy(false);}
 }
 async function process(){
  setError('');setMessage('');
  if(!file||!file.name.toLowerCase().endsWith('.zip')||file.size>32*1024*1024){setError('Selecione um ZIP DFP de até 32 MB.');return;}
  if(!/^\d{1,8}$/.test(company.trim())||!/^20\d{2}$/.test(year)){setError('Código CVM ou exercício inválido.');return;}
  setBusy(true);
  try{
    const zip_base64=await readBase64(file);
    const data=await request('/cvm/dfp/indicators',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({company_code:company.trim(),year:Number(year),zip_base64})}) as {status:string;stored:number;computed:Computed[]};
    await refresh();
    setMessage(data.status==='insufficient_data'?'Nenhum registro elegível encontrado.':data.computed.length+' indicador(es) calculado(s), '+data.stored+' registro(s) novo(s). Revisão de fonte pendente.');
  }catch(e){setError(e instanceof Error?e.message:'Falha no processamento');}
  finally{setBusy(false);}
 }
 function download(){
  const report:Report={status:'research_draft_not_verified',company_code:company.trim(),generated_at:new Date().toISOString(),review_status:'not_reviewed',indicators:rows};
  const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const anchor=document.createElement('a');anchor.href=url;anchor.download='finsight-dfp-'+company.trim()+'.json';anchor.click();
  URL.revokeObjectURL(url);
 }
 const canQuery=!!key&&/^\d{1,8}$/.test(company.trim())&&!!workspace.trim();
 return <section className="dfp-dossier" aria-label="Dossiê DFP CVM">
   <span className="eyebrow">DEMONSTRATIVOS / CVM / DFP</span><h2>Dossiê de indicadores contábeis</h2>
   <p>Calcule indicadores sobre arquivos DFP fornecidos por você. Resultados são preliminares e preservam a fórmula, o exercício e o hash do arquivo.</p>
   <div className="dfp-fields">
    <label>Workspace<input value={workspace} onChange={e=>setWorkspace(e.target.value)}/></label>
    <label>Chave da API<input type="password" autoComplete="off" value={key} onChange={e=>setKey(e.target.value)}/></label>
    <label>Código CVM<input value={company} onChange={e=>{setCompany(e.target.value);setRows([]);}} inputMode="numeric" placeholder="1234"/></label>
    <label>Exercício<input value={year} onChange={e=>setYear(e.target.value)} inputMode="numeric" placeholder="2025"/></label>
    <label className="dfp-upload">ZIP DFP<input type="file" accept=".zip,application/zip" onChange={e=>setFile(e.target.files?.[0]??null)}/></label>
   </div>
   <div className="dfp-actions">
    <button disabled={busy||!canQuery||!file} onClick={process}><FileArchive size={17}/>{busy?'Processando…':'Calcular a partir do ZIP'}</button>
    <button disabled={busy||!canQuery} onClick={load}><FileCheck2 size={17}/>Consultar indicadores</button>
    <button disabled={rows.length===0} onClick={download}><FileDown size={17}/>Exportar dossiê JSON</button>
   </div>
   {error&&<p role="alert" className="workbench-error">{error}</p>}
   {message&&<p role="status" className="workbench-success">{message}</p>}
   <div className="dfp-disclaimer">Revisão humana e reconciliação com demonstrações oficiais obrigatórias. A exportação não é parecer de auditoria.</div>
   {rows.length>0&&<div className="dfp-results">
     <h3>Indicadores disponíveis <small>Não verificados</small></h3>
     {rows.map((r,i)=><article key={r.metric_code+r.period+r.scope+r.dataset_sha256+i} className="dfp-result">
       <div><span>{names[r.metric_code]??r.metric_code}</span><strong>{r.value_decimal}</strong></div>
       <p>Fórmula: {formulas[r.metric_code]??r.account_codes} · Período: {r.period} · {r.scope==='consolidated'?'Consolidado':'Individual'}</p>
       <small>Fórmula: {r.formula_version} · Conta(s): {r.account_codes} · SHA-256: {r.dataset_sha256}</small>
       <small>Status: {r.status}</small>
     </article>)}
   </div>}
   <ReviewPanel workspace={workspace} apiKey={key} company={company} rows={rows}/>
 </section>;
}
