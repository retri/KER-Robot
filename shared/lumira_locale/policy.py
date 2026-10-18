"""Session-scoped language decisions. Scores must describe the active user's final turn.
Text evidence is a conservative heuristic, NOT a calibrated speech language detector.
Nationality, face, age, location and media playback are deliberately not inputs.
"""
from dataclasses import dataclass
import math, re, unicodedata
from .messages import message
SUPPORTED = ('ko-KR', 'en-US')
def normalize_locale(value):
    aliases = {'ko':'ko-KR','ko-kr':'ko-KR','en':'en-US','en-us':'en-US','en-gb':'en-US'}
    if not isinstance(value,str) or value.lower() not in aliases: raise ValueError('unsupported_locale')
    return aliases[value.lower()]
@dataclass(frozen=True)
class Decision:
    action: str
    locale: str | None
    reason: str
    revision: int
    prompt: str | None = None

# Only full utterances are commands; mentions in stories, quotes or instructions are not.
COMMANDS = {
 '한국어로 말해 줘':'ko-KR','한국어로 말해줘':'ko-KR','한국어로 해줘':'ko-KR',
 '영어로 말해 줘':'en-US','영어로 말해줘':'en-US','영어로 해줘':'en-US',
 'speak korean':'ko-KR','please speak korean':'ko-KR','speak in korean':'ko-KR',
 'speak english':'en-US','please speak english':'en-US','speak in english':'en-US',
}
SHORT = {'ok','okay','yes','no','네','예','응','아니','좋아','123'}
EN_WORDS = set('i you we my your the a an is are am can could would please what how why tell show like want have do let hello hi thanks thank good morning afternoon evening story music play read help stop english today tomorrow me it this that'.split())
def evidence(text):
    cleaned = re.sub(r'https?://\S+|`[^`]*`|"[^"]*"|“[^”]*”', ' ', text)
    ko = len(re.findall(r'[가-힣]', cleaned))
    words = re.findall(r"[a-zA-Z]+", cleaned.lower())
    # Latin letters alone do not prove English (names, French, product codes).
    english = len(set(words) & EN_WORDS)
    if ko >= 2 and english >= 2: return None, 'mixed'
    if ko >= 2: return 'ko-KR', 'text_korean'
    if english >= 2 and len(words) >= 3: return 'en-US', 'text_english'
    if cleaned.strip().lower() in {'hello','hi','thanks','thank you','good morning'}: return 'en-US', 'greeting'
    return None, 'ambiguous'
class LanguageSession:
    def __init__(self, actor, epoch, preferred=None, mode='auto'):
        if not isinstance(actor,str) or not actor or type(epoch) is not int or epoch<0: raise ValueError('invalid_session')
        if mode not in ('auto','fixed'): raise ValueError('invalid_mode')
        self.actor, self.epoch = actor, epoch
        self.locale = normalize_locale(preferred) if preferred else None
        if mode=='fixed' and not self.locale: raise ValueError('fixed_requires_locale')
        self.mode, self.revision, self.pending, self.last_seq = mode, 0, False, -1
    def decide(self, text, *, actor, epoch, sequence, final=True, source='user', explicit=None, scores=None):
        if actor!=self.actor or epoch!=self.epoch: raise ValueError('stale_session')
        if type(sequence) is not int or sequence<=self.last_seq: raise ValueError('stale_turn')
        if type(final) is not bool or source not in ('user','media','background'): raise ValueError('invalid_source')
        if not isinstance(text,str) or len(text)>4000: raise ValueError('invalid_text')
        if not final or source!='user': return Decision('ignore', self.locale, 'non_user_or_partial', self.revision)
        text=unicodedata.normalize('NFKC',text).strip()
        selected=normalize_locale(explicit) if explicit is not None else COMMANDS.get(text.casefold().rstrip('.!?'))
        if self.pending and selected is None:
            selected={'한국어':'ko-KR','korean':'ko-KR','영어':'en-US','english':'en-US'}.get(text.casefold())
        # Validate all supplied evidence before mutating state.
        detected,reason=evidence(text)
        if scores is not None:
            if not isinstance(scores,dict) or not scores: raise ValueError('invalid_scores')
            for key,v in scores.items():
                if not isinstance(key,str) or type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1: raise ValueError('invalid_scores')
            ranked=sorted(scores.items(),key=lambda kv:kv[1],reverse=True)
            top,score=ranked[0];margin=score-(ranked[1][1] if len(ranked)>1 else 0)
            # Thresholds are development settings, requiring speech evaluation before release.
            if score>=.85 and margin>=.2:
                try: candidate=normalize_locale(top)
                except ValueError: candidate=None
                if candidate and (detected is None or detected==candidate) and reason!='mixed':
                    detected,reason=candidate,'language_model_score'
                else: detected,reason=None,'conflicting_or_unsupported'
            else: detected,reason=None,'uncertain_audio'
        self.last_seq=sequence
        if selected:
            self.mode='fixed'; return self._accept(selected,'explicit')
        if self.mode=='fixed': return self._accept(self.locale,'user_fixed')
        if text.casefold().rstrip('.!?') in SHORT and self.locale: return self._accept(self.locale,'short_context')
        if detected: return self._accept(detected,reason)
        # Ask in both languages; a prior locale only controls ordering, not the answer.
        self.pending=True
        order=SUPPORTED if self.locale!='en-US' else tuple(reversed(SUPPORTED))
        return Decision('clarify',None,reason,self.revision,' / '.join(message('choose_language',l) for l in order))
    def _accept(self,locale,reason):
        if self.locale!=locale:self.revision+=1
        self.locale=locale;self.pending=False
        return Decision('respond',locale,reason,self.revision)
    def set_auto(self):
        self.mode='auto';self.pending=False
    def output_is_current(self, actor, epoch, revision):
        return actor==self.actor and epoch==self.epoch and revision==self.revision and not self.pending

def service_plan(locale, capabilities, *, channel='voice', content_locale=None):
    locale=normalize_locale(locale)
    if channel not in ('voice','screen'):raise ValueError('invalid_channel')
    stages=('stt','llm','tts','ui') if channel=='voice' else ('llm','ui')
    missing=[stage for stage in stages if locale not in capabilities.get(stage,())]
    if missing:return {'action':'unavailable','locale':locale,'missing':missing,'text':message('capability_missing',locale)}
    return {'action':'ready','response_locale':locale,'ui_locale':locale,'stt_locales':list(SUPPORTED),
            'tts_locale':locale,'content_locale':normalize_locale(content_locale) if content_locale else locale,
            'llm_instruction':f'Respond in {"Korean" if locale=="ko-KR" else "English"}. Preserve quoted lesson text in its original language.',
            'io_executed':False}
