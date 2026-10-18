"""Select exact locale variants. Missing versions never silently play another language."""
from .policy import normalize_locale
from .messages import message
class LocalizedCatalog:
    def __init__(self, records):
        self.rows={}
        for row in records:
            key=(row['content_key'],normalize_locale(row['locale']))
            if key in self.rows:raise ValueError('duplicate_variant')
            self.rows[key]=row
    def select(self,key,locale,*,age,allowed_modules,allow_drafts=False):
        locale=normalize_locale(locale);row=self.rows.get((key,locale))
        if row is None:return {'action':'unavailable','text':message('content_missing',locale),'locale':locale}
        if row['review_status']!='reviewed' and not(allow_drafts and row['review_status']=='draft'):raise ValueError('content_not_reviewed')
        if row['module'] not in allowed_modules or not row['age'][0]<=age<=row['age'][1]:raise ValueError('content_not_allowed')
        return {'action':'ready','content':row,'locale':locale}
