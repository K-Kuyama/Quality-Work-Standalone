'''
Created on 2024/06/28

@author: kuyamakazuhiro
'''
import threading
import unicodedata
import re

from activities.models import Perspective, Category, CategorizedActivity, CategorizedKeyWord


def addEscape(string):
    dictionary = {
            "(": "\(",
            ")": "\)",
            "{": "\{",
            "}": "\}"
        }
    trans_table = string.maketrans(dictionary)
    escaped_string = string.translate(trans_table)
    return escaped_string


class DefinitionModel:
    _instance = None
    _lock = threading.Lock()
    perspective = None
    categories = []
    perspective_id = None

    def __init__(self):
        pass
#        print('init')

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                print('new')
                cls._instance = super().__new__(cls)

        return cls._instance
    
    def setPerspective(self, p_instance):
        self.perspective = p_instance
        self.perspective_id = p_instance['id']
        self.categories =[]
        for cat in p_instance['categories']:
            self.categories.append(CategoryDefinition(cat))
            
            
    def reSetPerspective(self):
        model_p = Perspective.objects.get(pk=self.perspective_id)
        p_instance = {"id": model_p.id, "name": model_p.name, "color": model_p.color, 
                      "use_def_color": model_p.use_def_color, "categories": self.createCategories(model_p.id)}
        #print(f"reset perspective : {p_instance}")
        self.setPerspective(p_instance)
        
    def createCategories(self, pid):
        models = Category.objects.all().filter(perspective=pid)
        #print(f"models from DB : {models}")
        c_list = []
        for model_c in models:
            c_instance = {"id": model_c.id, "perspective": model_c.perspective, "name": model_c.name,
                          "color": model_c.color, "activities": self.createActivities(model_c.id),
                          "key_words": self.createKeyWords(model_c.id)}
            c_list.append(c_instance)
        return c_list
        
    def createActivities(self, cid):
        models = CategorizedActivity.objects.all().filter(category=cid)
        a_list = []
        for model_a in models:
            a_instance = {"id": model_a.id, "category": model_a.category, "app": model_a.app,
                          "title": model_a.title }
            a_list.append(a_instance)
        return a_list
    
    def createKeyWords(self, cid):
        models = CategorizedKeyWord.objects.all().filter(category=cid)
        w_list = []
        for model_w in models:
            w_instance = {"id": model_w.id, "category": model_w.category, "word": model_w.word,
                          "positive": model_w.positive }
            w_list.append(w_instance)
        return w_list
            
        
    def getPerspective(self):
        return self.perspective
    
    def get_colors(self, app_str, title_str):
        # デフォルト色をセット
        # bg_color ="#17192d"
        bg_color ="#595857"
        str_color = "hsla(0,0%,100%,.7)"       
        cid = None
        eid = None
        cname = "undefined"
        
#        print(f"get_colors {self.categories}")
        c_info = dict()
        for c in self.categories:
            for ed in c.events:
                if ed['app']==app_str and ed['title']==title_str:
                    c_info['backgroundColor'] = c.color
                    c_info['stringColor'] = "#d8469b"
                    c_info['categoryId'] = c.id
                    c_info['eventId'] = ed['id']
                    c_info['categoryName'] = c.name
#                    print(f"get_color_by_event({app_str},{title_str}) vs {ed['title']} -> {c_info}")
                    return c_info
                
        for c in self.categories:
            rgx =c.getRegex()
#            dprint(f"RGX : {rgx}")
            if rgx: 
                if re.search(rgx, app_str+title_str):
                    bg_color = c.color
                    cid = c.id
                    cname = c.name
                    break
                else:
                    cid = None
                    cname = "undefined"
            else:
                cid = None
                cname = "undefined"
                
        c_info['backgroundColor'] = bg_color
        c_info['stringColor'] = str_color
        c_info['categoryId'] = cid
        c_info['eventId'] =  eid
        c_info['categoryName'] = cname
#        print(f"get_color_by_words({app_str},{title_str}) -> {c_info}")
        return c_info

    
    
    
class CategoryDefinition:
    
    def __init__(self, c_obj):
        self.id = c_obj['id']
        self.name = c_obj['name']
        self.color = c_obj['color']
        self.events = c_obj['activities']
        self.positive_words = []
        self.negative_words = []
        for word in c_obj['key_words']:
            if word['positive'] :
                self.positive_words.append(word['word'])
            else :
                self.negative_words.append(word['word'])
        
    def getRegex(self):
        if len(self.negative_words)==0 and len(self.positive_words)==0:
            return None
        nega_str = self.getNegativeRegex()
        posi_str = self.getPositiveRegex()

        if nega_str=="" and posi_str=="":
#            full_str ="$^"
            full_str = None
        else:
            full_str = f"^{nega_str}{posi_str}.*$"
#        print(full_str)
        return full_str

    def getNegativeRegex(self):
        if len(self.negative_words)==0 :
            nega_str=""
        else:
            nega_str="(?!.*("
            for w in self.negative_words:
                if not nega_str =="(?!.*(":
                    nega_str = nega_str+"|"
                nega_str = nega_str+self.appendCCString(w)
            nega_str = nega_str + "))"
        return nega_str

    def getPositiveRegex(self):
        if len(self.positive_words)==0:
            posi_str = ""
        else:
            posi_str=".*("
            for pw in self.positive_words:
                if not posi_str ==".*(":
                    posi_str = posi_str+"|"
                posi_str = posi_str+self.appendCCString(pw)
            posi_str = posi_str + ")"    
        return posi_str
    
    
    def appendCCString(self, org_str):
        # append combined character sequence string
        nfd_str = unicodedata.normalize('NFD',org_str)
        nfc_str = unicodedata.normalize('NFC',org_str)
        if nfd_str == nfc_str:
            return nfc_str
        else:
            return nfc_str+"|"+nfd_str


class ColorInfo:
    backgroundColor = ""
    stringColor = ""
    categoryName = ""
    categoryId = None
    eventId = None
    activities = []
    categories = []
    

