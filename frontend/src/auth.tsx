import React,{createContext,useContext,useState,type ReactNode} from 'react';
import {ShieldCheck,LogOut} from 'lucide-react';
export const userAuthMode=import.meta.env.VITE_FINSIGHT_AUTH_MODE==='users';
type Session={token:string;workspace:string;username:string;role:string};
type AuthState={session:Session|null;setSession:(s:Session|null)=>void};
const AuthContext=createContext<AuthState|null>(null);
export function useAuth(){
 const ctx=useContext(AuthContext);
 if(!ctx)throw new Error('AuthProvider missing');
 return ctx;
}
export function authHeaders(session:Session|null,key:string):Record<string,string>{
 return userAuthMode?session?{'Authorization':'Bearer '+session.token}:{}:{'X-Workspace-Key':key};
}
export function AuthProvider({children}:{children:ReactNode}){
 const [session,setSession]=useState<Session|null>(null);
 return <AuthContext.Provider value={{session,setSession}}>
   {userAuthMode&&!session?<Login/>:children}
 </AuthContext.Provider>;
}
function Login(){
 const {setSession}=useAuth();
 const [workspace,setWorkspace]=useState('local');
 const [username,setUsername]=useState('');
 const [password,setPassword]=useState('');
 const [error,setError]=useState('');
 const [busy,setBusy]=useState(false);
 async function submit(e:React.FormEvent){
  e.preventDefault();setError('');setBusy(true);
  try{
   const r=await fetch('/api/v1/auth/login',{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify({workspace_id:workspace,username,password})});
   if(!r.ok)throw new Error('Credenciais inválidas ou autenticação indisponível.');
   const result=await r.json();
   const me=await fetch('/api/v1/auth/me?workspace_id='+encodeURIComponent(workspace),
     {headers:{'Authorization':'Bearer '+result.access_token}});
   if(!me.ok)throw new Error('Não foi possível verificar a sessão.');
   const profile=await me.json();
   setSession({token:result.access_token,workspace,username:profile.username,role:profile.role});
   setPassword('');
  }catch(err){setError(err instanceof Error?err.message:'Erro no login');}
  finally{setBusy(false);}
 }
 return <main className="auth-login"><form onSubmit={submit}>
  <ShieldCheck size={28}/><h1>FinSight</h1><p>Acesso ao ambiente de análise financeira</p>
  <label>Workspace<input required value={workspace} onChange={e=>setWorkspace(e.target.value)} /></label>
  <label>Usuário<input required autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)}/></label>
  <label>Senha<input required type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)}/></label>
  <button type="submit" disabled={busy}>{busy?'Autenticando…':'Entrar'}</button>
  {error&&<p role="alert">{error}</p>}
 </form></main>;
}
export function SessionHeader(){
 const {session,setSession}=useAuth();
 if(!userAuthMode||!session)return null;
 const token=session.token;
 async function logout(){
  try{await fetch('/api/v1/auth/logout',{method:'POST',headers:{'Authorization':'Bearer '+token}});}
  finally{setSession(null);}
 }
 return <span className="session-user"><span>{session.username} · {session.role}</span>
 <button onClick={logout} aria-label="Encerrar sessão"><LogOut size={15}/></button></span>;
}
