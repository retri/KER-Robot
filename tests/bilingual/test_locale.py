import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'shared'))
from lumira_locale import LanguageSession,message
from lumira_locale.policy import service_plan
from lumira_locale.service import BilingualService
from lumira_locale.messages import PAIRS
from lumira_locale.content import LocalizedCatalog
class LanguageTests(unittest.TestCase):
 def setUp(self):self.s=LanguageSession('u',1);self.n=0
 def say(self,text,**kw):
  self.n+=1;return self.s.decide(text,actor='u',epoch=1,sequence=self.n,**kw)
 def test_korean(self):self.assertEqual(self.say('오늘 이야기 들려줘').locale,'ko-KR')
 def test_english(self):self.assertEqual(self.say('Please tell me a story').locale,'en-US')
 def test_automatic_switch(self):
  self.say('오늘 이야기 들려줘');self.assertEqual(self.say('Please tell me a story').locale,'en-US')
 def test_ambiguous_asks(self):self.assertEqual(self.say('123').action,'clarify')
 def test_name_not_english(self):self.assertEqual(self.say('Samsung').action,'clarify')
 def test_unknown_latin(self):self.assertEqual(self.say('bonjour mon ami').action,'clarify')
 def test_mixed_asks(self):self.assertEqual(self.say('오늘은 please tell me a story').action,'clarify')
 def test_answer_to_clarification(self):
  self.say('123');self.assertEqual(self.say('English').locale,'en-US')
 def test_explicit_overrides(self):self.assertEqual(self.say('한국어 문장',explicit='en').locale,'en-US')
 def test_explicit_command_lock(self):
  self.say('please speak english');self.assertEqual(self.say('안녕하세요').locale,'en-US')
 def test_quote_is_not_command(self):
  d=self.say('"please speak english"');self.assertEqual(d.action,'clarify');self.assertEqual(self.s.mode,'auto')
 def test_short_context(self):
  self.say('안녕하세요');self.assertEqual(self.say('okay').locale,'ko-KR')
 def test_auto_after_fixed(self):
  self.say('please speak english');self.s.set_auto();self.assertEqual(self.say('안녕하세요').locale,'ko-KR')
 def test_media_does_not_switch(self):
  self.say('안녕하세요');self.assertEqual(self.say('Please tell me a story',source='media').action,'ignore');self.assertEqual(self.s.locale,'ko-KR')
 def test_partial_does_not_switch(self):self.assertEqual(self.say('hello',final=False).action,'ignore')
 def test_speaker_isolated(self):
  with self.assertRaises(ValueError):self.s.decide('hi',actor='other',epoch=1,sequence=1)
 def test_stale_epoch(self):
  with self.assertRaises(ValueError):self.s.decide('hi',actor='u',epoch=0,sequence=1)
 def test_duplicate_turn(self):
  self.say('hello')
  with self.assertRaises(ValueError):self.s.decide('hi',actor='u',epoch=1,sequence=1)
 def test_low_confidence(self):self.assertEqual(self.say('hello',scores={'en':.51,'ko':.49}).action,'clarify')
 def test_unsupported_language(self):self.assertEqual(self.say('bonjour',scores={'fr':.99,'en':.01}).action,'clarify')
 def test_conflicting_audio(self):self.assertEqual(self.say('안녕하세요',scores={'en':.99,'ko':.01}).action,'clarify')
 def test_invalid_score(self):
  with self.assertRaises(ValueError):self.say('hello',scores={'en':float('nan')})
  self.assertEqual(self.s.last_seq,-1)
 def test_voice_missing(self):self.assertEqual(service_plan('en',{'stt':['en-US'],'llm':['en-US'],'ui':['en-US']})['action'],'unavailable')
 def test_screen_mode(self):self.assertEqual(service_plan('en',{'llm':['en-US'],'ui':['en-US']},channel='screen')['action'],'ready')
 def test_content_locale_separate(self):self.assertEqual(service_plan('ko',{'llm':['ko-KR'],'ui':['ko-KR']},channel='screen',content_locale='en')['content_locale'],'en-US')
 def test_messages_both_locales(self):
  for key in PAIRS:
   for loc in ('ko-KR','en-US'):self.assertTrue(message(key,loc,answer='2'))
 def test_missing_content_no_silent_fallback(self):
  c=LocalizedCatalog([]);self.assertEqual(c.select('story','en',age=7,allowed_modules=['story'])['action'],'unavailable')
 def test_pending_blocks_old_output(self):
  first=self.say('hello');self.say('123abc');self.assertFalse(self.s.output_is_current('u',1,first.revision))
 def test_new_user_no_language_leak(self):
  self.say('hello');other=LanguageSession('v',2);self.assertIsNone(other.locale)
class ServiceTests(unittest.TestCase):
 def setUp(self):
  self.s=LanguageSession('u',1);self.c={k:['ko-KR','en-US'] for k in ('stt','llm','tts','ui')}
 def test_provider_receives_locale(self):
  calls=[]
  def provider(r):calls.append(r);return {'locale':r['locale'],'text':'Hello there.'}
  out=BilingualService(self.s,self.c,provider).turn('Please tell me a story',actor='u',epoch=1,sequence=1,cloud_allowed=True)
  self.assertEqual(calls[0]['locale'],'en-US');self.assertEqual(out['tts_locale'],'en-US')
 def test_no_consent_no_provider(self):
  def fail(r):raise AssertionError('must not call')
  out=BilingualService(self.s,self.c,fail).turn('Please tell me a story',actor='u',epoch=1,sequence=1)
  self.assertEqual(out['backend'],'local_template')
 def test_stop_bypasses_ambiguity(self):
  out=BilingualService(self.s,{}).turn('stop',actor='u',epoch=1,sequence=1)
  self.assertEqual(out['action'],'stop_request');self.assertFalse(out['executed'])
 def test_help_bypasses_ambiguity(self):self.assertEqual(BilingualService(self.s,{}).turn('help me',actor='u',epoch=1,sequence=1)['action'],'help_request')
 def test_wrong_language_contract(self):
  with self.assertRaises(ValueError):BilingualService(self.s,self.c,lambda r:{'locale':'ko-KR','text':'안녕'}).turn('Please tell me a story',actor='u',epoch=1,sequence=1,cloud_allowed=True)
 def test_switch_during_generation(self):
  def provider(r):self.s.decide('한국어로 해줘',actor='u',epoch=1,sequence=2);return {'locale':'en-US','text':'Hello'}
  with self.assertRaises(ValueError):BilingualService(self.s,self.c,provider).turn('Please tell me a story',actor='u',epoch=1,sequence=1,cloud_allowed=True)
if __name__=='__main__':unittest.main()

class ExistingRuntimeTests(unittest.TestCase):
 def setUp(self):
  import importlib.util
  path=Path(__file__).resolve().parents[2]/'Epic-02/runtime/core.py'
  spec=importlib.util.spec_from_file_location('dialogue_locale_test',path);self.core=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.core)
 def test_safety_english(self):self.assertEqual(self.core.SafetyPolicy().review('adult','harm','en-US')['safe_reply'],'I cannot help with that request.')
 def test_recovery_english(self):
  def fail():raise RuntimeError()
  self.assertIn('connection',self.core.Recovery().complete('t',[fail],locale='en-US')['text'])
 def test_gateway_requires_locale_adapter(self):
  g=self.core.Gateway({'openai_sample':lambda *a:{'text':'안녕하세요','usage_tokens':1}})
  with self.assertRaises(self.core.Rejected):g.complete('openai_sample','t',locale='en-US')
 def test_gateway_passes_locale(self):
  seen=[]
  def adapter(turn,limit,locale):seen.append(locale);return {'text':'Hello','usage_tokens':1}
  g=self.core.Gateway({'openai_sample':lambda *a:None},{'openai_sample':adapter})
  self.assertEqual(g.complete('openai_sample','t',locale='en-US')['text'],'Hello');self.assertEqual(seen,['en-US'])
