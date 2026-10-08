import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Search,FileSearch,GitCompare,Network,ShieldCheck,ArrowRight,BookOpen} from 'lucide-react';
import './style.css';
import './auth.css';
import {AuthProvider,SessionHeader} from './auth';
import './workbench.css';
import Workbench from './Workbench';
import DfpDossier from './DfpDossier';
import ComparisonWorkbench from './ComparisonWorkbench';

type Mode = 'individual'|'sector'|'multisector';
const labels: Record<Mode,string> = {individual:'Análise individual',sector:'Comparação setorial',multisector:'Análise multissetorial'};
const descriptions:Record<Mode,string> = {
  individual:'Investigue uma empresa, seus riscos, indicadores e as evidências que sustentam cada conclusão.',
  sector:'Compare empresas do mesmo setor usando benchmarks e fórmulas compatíveis.',
  multisector:'Analise diferentes setores sem criar rankings com métricas incompatíveis.'
};
const modes:Mode[]=['individual','sector','multisector'];
function App(){
 const [mode,setMode]=useState<Mode>('individual');
 const [query,setQuery]=useState('');
 return <div className="shell">
  <aside className="sidebar">
    <div className="brand"><span className="mark">▮▮▮</span><span><strong>FinSight</strong><small>Financial Due Diligence</small></span></div>
    <p className="eyebrow">WORKSPACE</p>
    {modes.map((m,i)=><button key={m} className={'nav '+(mode===m?'active':'')} onClick={()=>setMode(m)}>
      {i===0?<FileSearch size={18}/>:i===1?<GitCompare size={18}/>:<Network size={18}/>} {labels[m]}</button>)}
    <div className="sidebar-note">Aplicação sob medida<br/><span>Protótipo visual · Dados de demonstração</span></div>
  </aside>
  <main>
    <header><span className="eyebrow">FINANCIAL INTELLIGENCE / WORKBENCH</span><><span className="pill"><ShieldCheck size={15}/> Ambiente de análise</span><SessionHeader/></></header>
    <section className="hero">
      <div className="eyebrow">ANÁLISE • INTELIGÊNCIA • DECISÃO</div>
      <h1>Investigue empresas<br/><em>além dos números.</em></h1>
      <p>Informação só se torna uma conclusão quando existe contexto, metodologia e evidência.</p>
      <div className="search"><Search size={19}/><input aria-label="Empresa ou pergunta" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Busque uma empresa ou faça uma pergunta..."/><button onClick={()=>alert('Pesquisa real ainda não integrada. Este é um protótipo sem dados financeiros verificados.')}><ArrowRight size={18}/></button></div>
    </section>
    <div className="eyebrow section-label">ESCOLHA SEU MODO DE ANÁLISE</div>
    <section className="modes">{modes.map((m,i)=><button key={m} className={'mode '+(mode===m?'selected':'')} onClick={()=>setMode(m)}>
      <span className="mode-num">0{i+1}</span><h3>{labels[m]}</h3><p>{descriptions[m]}</p><ArrowRight size={20}/></button>)}</section>
    <section className="case">
      <div><span className="eyebrow">DOSSIÊ / {labels[mode].toUpperCase()}</span><h2>{mode==='individual'?'De números a uma tese verificável.':mode==='sector'?'Comparar exige critérios equivalentes.':'Contextos diferentes. Métricas responsáveis.'}</h2><p>{descriptions[mode]}</p>
      <div className="notice"><BookOpen size={19}/><span>Sem afirmações financeiras fabricadas: os relatórios só serão exibidos após integração, cálculo e verificação de fontes.</span></div></div>
      <div className="case-visual"><span>FINANCIAL DOSSIER</span><div className="visual-line"></div><strong>{mode==='individual'?'Evidência → cálculo → interpretação':mode==='sector'?'Setor → benchmark → comparação':'Setores → compatibilidade → contexto'}</strong><small>Experiência conceitual · Sem dados de mercado</small></div>
    </section>
    {mode==='individual'?<><DfpDossier/><Workbench/></>:<ComparisonWorkbench multisector={mode==='multisector'}/>}
    <footer>FinSight · Projeto em desenvolvimento · Engenharia financeira auditável</footer>
  </main>
 </div>
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><AuthProvider><App/></AuthProvider></React.StrictMode>);
