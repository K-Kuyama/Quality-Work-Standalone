import sqlite3
from datetime import datetime
from activities.models import Activity, Perspective, Category, CategorizedKeyWord, CategorizedActivity



class DataExporter:
    # 現在のデータベースに書き込みを行うクラス

    def __init__(self):

        self.connection = None
        self.cursor = None
        self.fd = None
        self.encoding = "utf-8"
        self.target = ["activities.Activity", "activities.Perspective", "activities.Category",
                "activities.CategorizedKeyWord", "activities.CategorizedActivity"]
        
        self.attributes ={
            "Activity":["id", "start_time", "duration", "distance_x", "distance_y", 
                        "strokes", "scrolls", "app", "title"],
            "Perspective":["id", "name", "color", "use_def_color", "categorize_model"],
            "Category":["id", "name", "color", "perspective"],
            "CategorizedActivity":["id", "app", "title", "category"],
            "CategorizedKeyWord":["id", "word", "positive", "category"]
        }
    
    def getClassName(self, target):
        return target.split(".")[1]
    
    def getTableName(self, target):
        target_list = target.split(".")
        return target_list[0].lower() +"_"+target_list[1].lower()

    def connect(self, db_file):
        # ソースデータベースファイルとのコネクションを開く
        self.connection = sqlite3.connect(db_file)
        self.cur = self.connection.cursor()

    # 使われていないので削除
    # def setTempFile(self, out_file):
    #    self.fd = open(out_file, 'a', encoding=self.encoding, errors='none')

    def writeTableData(self, target, attributes, replace_flag):
        # targetで指定したテーブルをソース側ファイルから読み込み現在のデータベースに書き込む

        table_name = self.getTableName(target)
        class_name = self.getClassName(target)

        cls = globals()[class_name]
        if replace_flag:
            #該当テーブルのデータを全て消去
            cls.objects.all().delete()
        try:
            #ソースとなるデータベースから全データを読み込む
            select_sql = "SELECT * FROM "+ table_name
            self.cur.execute(select_sql)
            result_set = self.cur.fetchall()
            if len(result_set)>0:
                #読み込んだデータを一旦オブジェクトに変換して現在のデータベースに保存
                print(f"result length {len(result_set[0])}, attr length {len(attributes)}")
                if len(result_set[0]) == len(attributes):
                    for result in result_set:
                        instance = cls()
                        for i in range(len(attributes)):
                            if not replace_flag and i == 0:
                                pass
                            else:
                                if attributes[i] == "start_time":
                                    st = datetime.strptime(result[i]+" +00:00", "%Y-%m-%d %H:%M:%S.%f %z")
                                    setattr(instance, attributes[i], st)
                                elif attributes[i] == "perspective":
                                    #print(f"->[i] : {result}")
                                    p = Perspective.objects.get(id=result[i])
                                    setattr(instance, attributes[i], p)
                                elif attributes[i] == "category":
                                    #print(f"->[i] : {result}")
                                    c = Category.objects.get(id=result[i])
                                    setattr(instance, attributes[i], c)
                                elif attributes[i] == "positive":
                                    f = False
                                    if result[i] == 1:
                                        f = True
                                    setattr(instance, attributes[i], f)
                                else:   
                                    setattr(instance, attributes[i], result[i])
                        instance.save()
        #except sqlite3.Error as e:
        except Exception as e:
            print(f"{table_name}: error {e}")
            return "Error : "+repr(e)
        return "Complete"

    def close(self):
        self.connection.close()