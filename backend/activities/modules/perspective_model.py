'''
Created on 2024/08/06

@author: kuyamakazuhiro
'''
import unicodedata
import re
from rest_framework import generics
from activities.models import Category, CategorizedActivity, CategorizedKeyWord, Perspective
from activities.serializers.user_definition_serializers import _PerspectiveSerializer

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


class ModelCreator:
    
    @staticmethod
    def create(pid):
        perspective = Perspective.objects.get(pk=pid)
        #print(vars(perspective))
        model_name = perspective.categorize_model
        if(model_name =="InputValueModel"):
            return InputValueModel()
        else:
            return PerspectiveModel(pid)
        
class InputValueModel():
    

    
    def __init__(self):
        self.zappingColor = "#7fffff"
        self.creationColor = "#7f7fff"
        self.infoGatheringColor = "#7fbfff"
    
        self.duration_threshold = 10
        self.strokes_threshold = 10
        self.distance_threshold = 1000

    
    def get_colors(self, obj):
        c_info = dict()
        c_info['stringColor'] = "#d8469b"
        c_info['eventId'] = None
        distance = (obj.distance_x**2 + obj.distance_y**2)**0.5
        if(obj.duration < self.duration_threshold):
            if(obj.strokes < self.strokes_threshold and distance < self.distance_threshold):
                c_info['backgroundColor'] = self.zappingColor
                c_info['categoryName'] = "ザッピング"
                c_info['categoryId'] = 19
            else:
                c_info['backgroundColor'] = self.creationColor
                c_info['categoryName'] = "アウトプット"
                c_info['categoryId'] = 21
        else:
            if(obj.strokes < self.strokes_threshold and distance < self.distance_threshold):
                c_info['backgroundColor'] = self.infoGatheringColor
                c_info['categoryName'] = "インプット"
                c_info['categoryId'] = 20
            else:
                c_info['backgroundColor'] = self.creationColor
                c_info['categoryName'] = "アウトプット"
                c_info['categoryId'] = 21
        return c_info               
        
        

class PerspectiveModel(generics.RetrieveAPIView):
    serializer_class = _PerspectiveSerializer   
    perspective = None
    categories = []
    perspective_id = None 

    def __init__(self, p_id):
        self.perspective_id =p_id
        #print(f"perspective Model {self.perspective_id}")
        cdics = self.createCategories(p_id)
        self.categories = []
        for cat in cdics:
            self.categories.append(CategoryDefinition(cat))


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


    def get_colors(self, obj):
        # デフォルト色をセット
        bg_color ="#17192d"
        #bg_color ="#595857"
        str_color = "hsla(0,0%,100%,.7)"       
        cid = None
        eid = None
        cname = "undefined"
        
#        print(f"get_colors {self.categories}")
        c_info = dict()
        for c in self.categories:
            for ed in c.events:
                if ed['app']==obj.app and ed['title']==obj.title:
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
                if re.search(rgx, obj.app+obj.title):
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
    

    
    