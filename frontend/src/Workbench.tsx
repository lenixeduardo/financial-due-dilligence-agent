import {useState, type ChangeEvent} from 'react';
import {FileUp, Search, ShieldAlert, FileText} from 'lucide-react';
import {useAuth,userAuthMode,authHeaders} from './auth';

type Passage={evidence_id:string;source_url:string;publisher:string;page:number;excerpt:string};
type SearchResult={question:string;status:string;passages:Passage[];interpretation:string|null};
type IngestResult={file_sha256:string;pages:number;new_chunks:number;status:string};

const apiBase='/api';
async function callApi<T>(path:string, headers:Record<string,string>, data:unknown):Promise<T>{
  const res=await fetch(apiBase+path,{method:'POST',headers:{'Content-Type':'application/json',...headers},body:JSON.stringify(data)});
  const payload=await res.json().catch(()=>({detail:'Resposta inválida do servidor'}));
  if(!res.ok) throw new Error(typeof payload.detail==='string'?payload.detail:'Falha na API ('+res.status+')');
  return payload as T;
}
function toBase64(file:File):Promise<string>{
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=()=>{const value=reader.result; if(typeof value!=='string') return reject(new Error('Não foi possível ler o arquivo'));resolve(value.split(',')[1]??'');};
    reader.onerror=()=>reject(new Error('Erro de leitura'));
    reader.readAsDataURL(file);
  });
}
export default function Workbench(){
  const {session}=useAuth();
  const [workspace,setWorkspace]=useState('local');
  const [key,setKey]=useState('');
  const [company,setCompany]=useState('');
  const [sourceUrl,setSourceUrl]=useState('');
  const [publisher,setPublisher]=useState('');
  const [version,setVersion]=useState('');
  const [file,setFile]=useState<File|null>(null);
  const [question,setQuestion]=useState('');
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const [ingested,setIngested]=useState<IngestResult|null>(null);
  const [result,setResult]=useState<SearchResult|null>(null);
  const activeWorkspace=userAuthMode?(session?.workspace??''):workspace;
  const authorized=userAuthMode?!!session:!!key;
  const canEdit=!userAuthMode||session?.role==='analyst'||session?.role==='admin';
  const path='/v1/workspaces/'+encodeURIComponent(activeWorkspace.trim());
  async function upload(){
    setError('');setIngested(null);
    if(!file || file.size>8*1024*1024){setError('Selecione PDF, TXT ou CSV com até 8 MB.');return;}
    setBusy(true);
    try{
      const base64_content=await toBase64(file);
      const data=await callApi<IngestResult>(path+'/documents/ingest',authHeaders(session,key),
        {company_id:company.trim(),filename:file.name,base64_content,source_url:sourceUrl.trim(),publisher:publisher.trim(),document_version:version.trim()});
      setIngested(data);
    }catch(e){setError(e instanceof Error?e.message:'Erro inesperado');}finally{setBusy(false);}
  }
  async function search(){
    setError('');setResult(null);setBusy(true);
    try{
      setResult(await callApi<SearchResult>(path+'/analysis/evidence',authHeaders(session,key),{company_id:company.trim(),question:question.trim()}));
    }catch(e){setError(e instanceof Error?e.message:'Erro inesperado');}finally{setBusy(false);}
  }
  return <section className="workbench" aria-label="Dossiê financeiro com evidências">
    <div className="workbench-title"><span className="eyebrow">DOSSIÊ / DOCUMENTOS REAIS</span><h2>Investigação com evidências</h2>
    <p>Importe um documento autorizado e pesquise passagens identificadas por origem e página. Nenhuma conclusão por IA é apresentada como validada.</p></div>
    <div className="notice"><ShieldAlert size={19}/><span>Somente uso local. A chave é mantida em memória nesta aba e enviada à API de desenvolvimento. Não exponha esse sistema na internet nem envie documentos sigilosos.</span></div>
    <div className="workbench-grid">
      <div className="workbench-panel">
        <h3><FileUp size={18}/> Importar documento</h3>
        {!userAuthMode&&<label>Workspace<input value={workspace} onChange={e=>setWorkspace(e.target.value)} placeholder="local"/></label>}
        {!userAuthMode&&<label>Chave local da API<input type="password" autoComplete="off" value={key} onChange={e=>setKey(e.target.value)} placeholder="FINSIGHT_WORKSPACE_API_KEY"/></label>}
        <label>Identificador da empresa<input value={company} onChange={e=>setCompany(e.target.value)} placeholder="empresa-001"/></label>
        <label>Fonte oficial (HTTPS)<input type="url" value={sourceUrl} onChange={e=>setSourceUrl(e.target.value)} placeholder="https://..."/></label>
        <label>Emissor<input value={publisher} onChange={e=>setPublisher(e.target.value)} placeholder="Relações com investidores"/></label>
        <label>Versão / exercício<input value={version} onChange={e=>setVersion(e.target.value)} placeholder="2025-FY"/></label>
        <label>Documento (PDF, TXT ou CSV)<input type="file" accept=".pdf,.txt,.csv" onChange={(e:ChangeEvent<HTMLInputElement>)=>setFile(e.target.files?.[0]??null)}/></label>
        <button className="workbench-action" disabled={busy||!authorized||!canEdit||!company||!sourceUrl||!publisher||!version||!file} onClick={upload}>{busy?'Processando…':'Indexar documento'}</button>
        {ingested&&<p role="status" className="workbench-success">Indexado: {ingested.pages} página(s), {ingested.new_chunks} trecho(s) novos. Verificação documental pendente.</p>}
      </div>
      <div className="workbench-panel">
        <h3><Search size={18}/> Consultar evidências</h3>
        <label>Pergunta<input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Receita operacional em 2025"/></label>
        <button className="workbench-action" disabled={busy||!authorized||!company||!question.trim()} onClick={search}>Buscar nos documentos</button>
        {error&&<p role="alert" className="workbench-error">{error}</p>}
        {result&&<div role="status" className="workbench-results">
          <p><strong>{result.passages.length} passagem(ns) encontradas</strong> · {result.status==='insufficient_evidence'?'Evidência insuficiente':'Exigem revisão humana'}</p>
          {result.passages.map((p,i)=><article className="evidence-card" key={p.evidence_id+'-'+i}>
            <div><FileText size={15}/><strong>{p.publisher} · página {p.page}</strong></div>
            <p>{p.excerpt}</p>
            <a href={p.source_url} target="_blank" rel="noopener noreferrer">Consultar fonte declarada</a>
            <small>Identificador: {p.evidence_id}</small>
          </article>)}
          {result.passages.length===0&&<p>Nenhum trecho correspondente. Não é possível emitir uma conclusão fundamentada.</p>}
        </div>}
      </div>
    </div>
  </section>;
}
