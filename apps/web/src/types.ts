export type ActionType='send_email'|'create_ticket'|'schedule_meeting';
export type Task={id:string;prompt:string;status:string;plan:string[];summary:string;sources:{title:string;url:string;excerpt:string}[];proposed_action:null|{type:ActionType;arguments:Record<string,unknown>;risk:string;fingerprint:string};trace:{timestamp:string;event:string;detail:string;status:string}[];result:Record<string,unknown>|null};

