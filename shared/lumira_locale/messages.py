"""Common UI, dialogue, safety and service messages. Keys are language independent."""
PAIRS = {
 'choose_language': ('한국어와 영어 중 어떤 언어로 이야기할까요?', 'Would you prefer Korean or English?'),
 'retry': ('잘 듣지 못했어요. 다시 말씀해 주시겠어요?', 'I did not catch that. Could you say it again?'),
 'correct': ('잘했어요!', 'Well done!'),
 'finished': ('끝까지 해 봤네요. 잘했어요.', 'You finished the activity. Well done.'),
 'answer': ('함께 배워 봐요. 정답은 {answer}예요.', 'Let us learn together. The answer is {answer}.'),
 'guardian': ('가까이에 있는 보호자에게 도움을 요청해 주세요.', 'Please ask a nearby parent or caregiver for help.'),
 'choose_activity': ('준비된 활동에서 골라 주세요.', 'Please choose one of the available activities.'),
 'offline': ('연결 없이 기본 안내를 도와드릴게요.', 'I can help with basic guidance while offline.'),
 'connection': ('연결이 원활하지 않습니다. 기본 안내를 도와드릴게요.', 'The connection is unavailable. I can help with basic guidance.'),
 'deny': ('그 요청은 도와드릴 수 없습니다.', 'I cannot help with that request.'),
 'crisis': ('지금 주변의 믿을 수 있는 사람에게 도움을 요청해 주세요. 저는 연락을 대신 실행하지 않았습니다.', 'Please ask someone you trust nearby for help now. I have not contacted anyone for you.'),
 'medical': ('정확한 판단은 의료 전문가와 상의해 주세요.', 'Please consult a healthcare professional for an assessment.'),
 'guidance': ('기본 안내부터 도와드릴게요.', 'Let us start with basic guidance.'),
 'content_missing': ('이 콘텐츠의 한국어 버전이 준비되지 않았어요. 다른 콘텐츠를 고를까요?', 'An English version of this content is not available. Would you like another activity?'),
 'capability_missing': ('이 언어의 음성 기능이 준비되지 않았어요. 화면 안내로 계속할까요?', 'Voice support for this language is unavailable. Would you like to continue on screen?'),
 'stopped': ('중단 요청을 보냈습니다. 기기 확인을 기다립니다.', 'A stop was requested. Waiting for confirmation from the device.'),
 'listening': ('듣고 있어요.', 'I am listening.'),
 'thinking': ('잠시 생각하고 있어요.', 'Let me think.'),
 'network': ('연결 상태를 확인하고 있어요.', 'Checking the connection.'),
 'language_ko': ('한국어', 'Korean'), 'language_en': ('영어', 'English'),
 'start': ('시작', 'Start'), 'stop': ('중단', 'Stop'), 'back': ('뒤로', 'Back'),
 'next': ('다음', 'Next'), 'settings': ('설정', 'Settings'),
 'request_rejected': ('요청을 처리할 수 없어요. 입력과 권한을 확인해 주세요.', 'The request could not be processed. Please check the input and permissions.'),
}
def message(key, locale, **values):
    if locale not in ('ko-KR', 'en-US'): raise ValueError('unsupported_locale')
    return PAIRS[key][0 if locale == 'ko-KR' else 1].format(**values)
