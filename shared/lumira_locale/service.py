"""Language-aware orchestration for a trusted host. Adapters are injected by deployment.
This module does not itself connect to cloud, audio devices, UI or robot motors.
"""
from dataclasses import asdict
from .policy import LanguageSession, service_plan
from .messages import message
class BilingualService:
    def __init__(self, session, capabilities, provider=None):
        self.session=session;self.capabilities=capabilities;self.provider=provider
    def turn(self,text,*,actor,epoch,sequence,explicit=None,scores=None,source='user',final=True,cloud_allowed=False):
        # Identity and event validation happen even for local safety commands.
        if actor!=self.session.actor or epoch!=self.session.epoch:raise ValueError('stale_session')
        if type(sequence) is not int or sequence<=self.session.last_seq:raise ValueError('stale_turn')
        if type(cloud_allowed) is not bool:raise ValueError('invalid_consent')
        if source=='user' and final is True and isinstance(text,str) and text.strip().casefold() in ('stop','정지','멈춰','help','help me','도와줘'):
            self.session.last_seq=sequence
            locale='en-US' if text.strip().isascii() else 'ko-KR'
            stop=text.strip().casefold() in ('stop','정지','멈춰')
            return {'action':'stop_request' if stop else 'help_request','locale':locale,'text':message('stopped' if stop else 'guardian',locale),'executed':False}
        d=self.session.decide(text,actor=actor,epoch=epoch,sequence=sequence,explicit=explicit,scores=scores,source=source,final=final)
        if d.action!='respond':return {**asdict(d),'text':d.prompt,'io_executed':False}
        plan=service_plan(d.locale,self.capabilities)
        if plan['action']!='ready':return plan
        if self.provider is None or not cloud_allowed:
            return {**plan,'text':message('offline',d.locale),'backend':'local_template'}
        response=self.provider({'text':text,'locale':d.locale,'system_instruction':plan['llm_instruction'],'epoch':epoch,'turn':sequence,'language_revision':d.revision})
        if not self.session.output_is_current(actor,epoch,d.revision) or self.session.last_seq!=sequence:raise ValueError('stale_output')
        if not isinstance(response,dict) or response.get('locale')!=d.locale or not isinstance(response.get('text'),str) or not 0<len(response['text'])<=8000:raise ValueError('provider_locale_contract')
        return {**plan,'text':response['text'],'backend':'injected_provider','language_revision':d.revision}
