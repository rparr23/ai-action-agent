import type {ActionType,Task} from './types';
const BASE=import.meta.env.VITE_API_URL||'http://localhost:8000';
async function request<T>(path:string,init?:RequestInit):Promise<T>{const res=await fetch(`${BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...init?.headers}});if(!res.ok){const body=await res.json().catch(()=>({detail:'Request failed'}));throw new Error(body.detail||'Request failed')}return res.json()}
export const createTask=(prompt:string,action_type:ActionType)=>request<Task>('/tasks',{method:'POST',body:JSON.stringify({prompt,action_type})});
export const decide=(task:Task,decision:'approve'|'reject')=>request<Task>(`/tasks/${task.id}/${decision}`,{method:'POST',body:JSON.stringify({fingerprint:task.proposed_action?.fingerprint})});

