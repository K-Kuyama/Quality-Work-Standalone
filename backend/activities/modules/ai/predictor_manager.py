'''
Created on 2025/08/21

@author: kuyamakazuhiro
'''

from datetime import datetime
from dateutil.tz import gettz
from django.conf import settings

import os
import sqlite3
#import pandas
import csv
import pickle
import threading
import shutil
import logging

from django.db.models import Value
from django.db.models.functions import Concat
from tenant_schemas.storage import TenantFileSystemStorage
from activities.models import ActivityPredictor, CategorizedActivity, Activity, AudioActivity
from activities.modules.ai.predictor import Predictor
from activities.modules.ai.util import labelToName, labelToNameforList, tokenize

from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder


logger = logging.getLogger('django')

# SQLiteへの接続
def conn_to_db(db_name):
    # 接続先データベース
    #db_name = 'db.sqlite3'
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Exception as e:
        print('Error: データベースに接続できませんでした')
        print(e)
        return None



class PredictorManager:

    # マネージャークラスであり、以下のスタティックメソッドを提供する
    # get_predictor
    # activate_predictor
    # delete_predictor
    # create_predictor

    _instance = None
    _lock = threading.Lock()
    #active_predictors = None
    db_file = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    # mecab = None
    janome_t = None
    predictors_dir = None

    def __init__(self):

        self.janome_t = self.__class__.janome_t
        self.active_predictors = self.__class__.active_predictors
        # predictorsフォルダを作る位置を設定する。マルチテナントの場合は、
        # テナントごとのフォルダにpredictorsディレクトリを作るために、
        # storage.path("predictors")でこのディレクトリの絶対パスを取得
        if settings.QT_MULTI:
            storage = TenantFileSystemStorage()
            self.predictors_dir = storage.path("predictors")
            logger.info(f"predictors dir -> {self.predictors_dir}")
        else :
            self.predictors_dir = os.path.join(settings.MEDIA_ROOT, "predictors")
        
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls.active_predictors = dict()
                cls.janome_t = Tokenizer()
                cls._instance = super().__new__(cls)
        return cls._instance


    def get_predictor(self, p_id):
        # すでにアクティブになっているpredictorがあるか調べる
        predictor = self.active_predictors.get(p_id)
        
        if not predictor:
             # なければファイルからロードする
            predictor = self.load_predictor(p_id)
            #logger.info(f"{p_id}:set predictor ->{predictor}")
             # アクティブになっているpredictorとして登録する
            self.active_predictors[p_id] = predictor
            #logger.info(f"{p_id}:set predictor ->{predictor}")
        return predictor
    

    def load_predictor(self, p_id):
        # データベースに登録されているpredictorの情報を基に
        # ファイルからPredictorを復元する
        try:
            predictor_info = ActivityPredictor.objects.get(p_id=p_id, using=True)
        except Exception as e:
            return None
        name = predictor_info.name
        location = os.path.join(self.predictors_dir, name)
        predictor = Predictor(location, name, self.janome_t)
        return predictor
    

    def activate_predictor(self, p_id, p_name):
        # 新たなpredictorをファイルからインスタンス化して、現在使えるPredictorとして登録する
        location = os.path.join(self.predictors_dir, p_name)
        predictor = Predictor(location, p_name, self.janome_t)
        self.active_predictors[p_id] = predictor



    def delete_predictor(self, p_id, p_name):
        ap = self.active_predictors.get(p_id)

        if not p_id or not p_name:
            return False
        else:
            p = ActivityPredictor.objects.get(p_id=p_id, name=p_name)
            module_name = p.name
            p.delete()
            self.delete_predictor_location(module_name)
            return True


    ######### pandas代替関数 ###############
    def read_csv(self, filepath):
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)  # list of dicts（例: [{'col1': 'A', 'col2': '1'}, ...]）

    def write_csv(self, filepath, rows, fieldnames=None):
        """
        rows: list of dict
        fieldnames: 列名（指定しない場合は最初の行のキーから自動取得）
        """
        if not rows:
            raise ValueError("書き込むデータが空です。")

        if fieldnames is None:
            fieldnames = list(rows[0].keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def read_sql_query(self, sql, connection, params=None):
        with connection as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)        
            rows = [dict(row) for row in cur.fetchall()]
        return rows  

    #############################################

    def create_predictor(self, p_id, start=None, end=None, data_source="Activity"):
        #与えられた条件でPredictorを新たに生成する

        # predictorの名前をつける
        current_time = datetime.now(gettz(settings.TIME_ZONE))
        module_name = str(p_id) + "-" + current_time.strftime("%Y%m%d%H%M%S")
        # predictorのモジュールを保存するディレクトリを作る
        location = self.create_predictor_location(module_name)
        # 学習データを作る
        learning_data = self.create_learning_data(p_id, start, end, data_source)
        #learning_data.to_csv(os.path.join(location, "large_data.csv"), index=False, header=False)
        self.write_csv(os.path.join(location, "large_data.csv"), learning_data)

        ## 学習・テストデータを読み込む
        #df = pandas.read_csv(os.path.join(location, "large_data.csv"))  # ファイル名を指定        
        #texts = df.iloc[:, 0].tolist()
        #labels = df.iloc[:, 1].tolist()

        rows = self.read_csv(os.path.join(location, "large_data.csv"))  # ファイル名を指定
        texts =  [r["title"] for r in rows]
        labels = [r["category_id"] for r in rows]

        # ====== 前処理 ======
        # ラベルを数値に変換
        le = LabelEncoder()
        labels_encoded = le.fit_transform(labels)
        label_classes = le.classes_      # ラベルとして含まれているカテゴリーIDのリスト
        #target_names = labelToName(df, le.classes_) #対応するラベル名のリスト
        target_names = labelToNameforList(rows, le.classes_) 
        # ラベルエンコーダーを保存しておく
        with open(os.path.join(location,'label.pickle'), 'wb') as web:
            pickle.dump(le , web)

        #形態素解析
        #mecab = MeCab.Tagger()
        tokenized_texts = [tokenize(self.janome_t, t) for t in texts]

        # ====== TF-IDFベクトル化 ======
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        X = vectorizer.fit_transform(tokenized_texts)

        #vectorizerの保存
        with open(os.path.join(location,'vectorizer.pickle'), 'wb') as web:
            pickle.dump(vectorizer , web)

        # ====== 学習データとテストデータに分割 ======
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels_encoded, test_size=0.3, random_state=42, stratify=labels
        )

        # ====== 多クラスロジスティック回帰 ======
        clf = LogisticRegression(
            # multi_class="multinomial",
            class_weight="balanced",    # 少数派のサンプルに対し重み付けを行う
            solver="lbfgs",              # multinomial対応ソルバー
            max_iter=1000
        )
        clf.fit(X_train, y_train)

        with open(os.path.join(location,'model.pickle'), 'wb') as web:
            pickle.dump(clf , web)

        # ====== 評価 ======
        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred, target_names = target_names)

        # データベースに情報を登録する
        pi = ActivityPredictor(p_id = p_id,
                                name = module_name, 
                                created_dtime = current_time,
                                data_start = start,
                                data_end = end,
                                num_of_labels = len(label_classes), 
                                num_of_learning_data = X_train.shape[0],
                                score = report, using = False)
        pi.save()
        return pi
    

   
    def create_predictor_location(self, module_name):
        #新しくディレクトリを作る。ディレクトリ名は <p_id>-<current time>

        if not os.path.isdir(self.predictors_dir):
            os.makedirs(self.predictors_dir)
        location = os.path.join(self.predictors_dir, module_name)
        os.makedirs(location)
        return location


    def delete_predictor_location(self, module_name):
        # 該当するPredictorに関するファイルを消去する
        location = os.path.join(self.predictors_dir, module_name)
        shutil.rmtree(location)


    def get_registered_activities(self, p_id):
        # データベースからカテゴリーに登録されたアクティビティ情報を取り出し以下の型のdictにする
        # {atitle:xxx, category_id:xxx, name:xxx}
        queryset = CategorizedActivity.objects.select_related(
                    "category").filter(
                        category__perspective_id=p_id
                        ).annotate(atitle=Concat('app', Value(' '), 'title'))
        rows = []
        for ac in queryset:
            rows.append({'atitle': ac.atitle,'category_id':ac.category.id, 'name':ac.category.name})
        return rows
    
    def get_audio_activities(self, start, end):
        # オーディオアクティビティを取り出し、文字列を加工しatitle属性に格納したdictのリストを返す
        queryset = AudioActivity.objects.all()
        a_activities = None
        if start == None:
            if end == None:
                a_activities = queryset
            else:
                a_activities = queryset.filter(start_time__lte=datetime.strptime(end, self.format_str))
        else:
            if end == None:
                a_activities = queryset.filter(start_time__gte=datetime.strptime(start, self.format_str))
            else:
                a_activities = queryset.filter(start_time__gte=datetime.strptime(start, self.format_str),
                                                start_time__lte=datetime.strptime(end, self.format_str))
        a_activity_rows = []
        app = ""
        title = ""
        for aac in a_activities:
            if aac.selected == 0:
                app = aac.start_app
                title = aac.start_title
            elif aac.selected == 1:
                app = aac.longest_app
                title = aac.longest_title
            else:
                app = aac.another_app
                title = aac.another_title
            a_activity_rows.append({'atitle':'audio_stream '+app+':'+title})
        return a_activity_rows

    def create_learning_data(self, p_id, start=None, end=None, data_source="Activity"):
        # CategorizedActivityとして登録されている項目とマッチするアクティビティを取り出し、
        # [アプリ名+タイトル, category-id, category名]からなる行のリストを作る
        # data_source が'Activity'の時は通常のCategorizedActivityテーブルを使い、'ActivityEval'の場合は
        # ategorizedActivityEvalテーブルを使う (このスイッチは今は使われていないが残してある)

        categorize_rows = self.get_registered_activities(p_id)

        if data_source == "CategorizedActivity":
            return categorize_rows
        
        else:
            queryset = Activity.objects.annotate(atitle=Concat('app', Value(' '), 'title'))
            activities = None
            if start == None:
                if end == None:
                    activities = queryset
                else:
                    activities = queryset.filter(start_time__lte=datetime.strptime(end, self.format_str))
            else:
                if end == None:
                    activities = queryset.filter(start_time__gte=datetime.strptime(start, self.format_str))
                else:
                    activities = queryset.filter(start_time__gte=datetime.strptime(start, self.format_str),
                                                 start_time__lte=datetime.strptime(end, self.format_str))
            activity_rows = []
            for ac in activities:
                activity_rows.append({'atitle': ac.atitle})
        
            # オーディオアクティビティを取り出し、これを追加する
            a_activity_rows = self.get_audio_activities(start, end)
            activity_rows.extend(a_activity_rows)

        rows = []
        for row in activity_rows:
            matched = next((r for r in categorize_rows if r['atitle']==row['atitle']), None)
            if matched:
                rows.append({'title': row['atitle'], 'category_id': matched['category_id'], 
                                        'name': matched['name']})
        #return df
        return rows
            
#以下はSQL文を直に発行してデータを取り出すV3.0で使っていたコードだが、postgreSQLにも対応するために
# ORMを使うように変更したので、今後は使わない。
'''
    def create_learning_data(self, p_id, start=None, end=None, data_source="Activity"):
        # CategorizedActivityとして登録されている項目とマッチするアクティビティを取り出し、
        # [アプリ名+タイトル, category-id, category名]からなる行のリストを作る
        # data_source が'Activity'の時は通常のCategorizedActivityテーブルを使い、'ActivityEval'の場合は
        # ategorizedActivityEvalテーブルを使う (このスイッチは今は使われていないが残してある)

        conn = conn_to_db(self.db_file)
        
        sql_str = "SELECT app||' '||title AS atitle, category_id, name FROM  activities_categorizedactivity INNER JOIN activities_category ON activities_categorizedactivity.category_id = activities_category.id WHERE perspective_id = ?"
        if data_source == "ActivityEval":
            sql_str = "SELECT app||' '||title AS atitle, category_id, name FROM  activities_categorizedactivityeval INNER JOIN activities_category ON activities_categorizedactivityeval.category_id = activities_category.id WHERE perspective_id = ?"
        #categorize_df = pandas.read_sql_query(sql_str, conn, params=(p_id,))
        categorize_rows = self.read_sql_query(sql_str, conn, params=(p_id,))

        if data_source == "CategorizedActivity":
            return categorize_rows
        
        else:
            sql_str2 = "SELECT app||' '||title AS atitle FROM activities_activity"
            #activity_df = None
            activity_rows = None
            if start == None:
                if end == None:
                    #activity_df = pandas.read_sql_query(sql_str2, conn)
                    activity_rows = self.read_sql_query(sql_str2, conn)
                else:
                    condition_str = " WHERE datetime(start_time, 'localtime') < datetime(?, 'localtime')"
                    #activity_df = pandas.read_sql_query(sql_str2+condition_str, conn, params=(end,))
                    activity_rows = self.read_sql_query(sql_str2+condition_str, conn, params=(end,))
            else:
                if end == None:
                    condition_str = " WHERE datetime(start_time, 'localtime') >= datetime(?, 'localtime')"
                    #activity_df = pandas.read_sql_query(sql_str2+condition_str, conn, params=(start,))
                    activity_rows = self.read_sql_query(sql_str2+condition_str, conn, params=(start,))
                else:
                    condition_str = " WHERE (datetime(start_time, 'localtime') BETWEEN datetime(?, 'localtime') AND datetime(?, 'localtime'))"
                    #activity_df = pandas.read_sql_query(sql_str2+condition_str, conn, params=(start, end))
                    activity_rows = self.read_sql_query(sql_str2+condition_str, conn, params=(start, end))

            #df = pandas.DataFrame()
            #i=0
            #for index, row in activity_df.iterrows():
            #    matched = categorize_df[categorize_df['atitle']==row['atitle']]
            #    if not matched.empty:
            #        new_rows = pandas.DataFrame({'title': row['atitle'], 'category_id': matched.iloc[0]['category_id'], 
            #                                'name': matched.iloc[0]['name']}, index=[i])
            #        df = pandas.concat([df, new_rows])
            #        i += 1
            rows = []
            for row in activity_rows:
                matched = next((r for r in categorize_rows if r['atitle']==row['atitle']), None)
                if matched:
                    rows.append({'title': row['atitle'], 'category_id': matched['category_id'], 
                                            'name': matched['name']})
            #return df
            return rows
'''