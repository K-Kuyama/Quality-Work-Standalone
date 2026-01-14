import abc
import sqlite3
#from system.DataExporter import DataExporter


class MigratorManager:

    @classmethod
    def getMigrator(self,old, new):
        if old == 0 and new == 3:
            return Migrator0to3()
        else:
            raise RuntimeError(f"No migrator for {old}->{new}")

class Migrator:

    def __init__(self, old, new):
        self.target_table =[]        

    def migrate(self, conn):
        raise NotImplementedError()
    
class Migrator0to3(Migrator):
    '''
    Schema version 3用のマイグレーション
    '''
    def __init__(self):
        self.modified_target = ("activities.Perspective", "activities.Category")

        self.target_tables = [
            {
                'name': "activities.Activity",
                'args':["id", "start_time", "duration", "distance_x", "distance_y", "strokes", "scrolls", "app", "title"],
                'args_str': "id, start_time, duration, distance_x, distance_y, strokes, scrolls, app, title",
            },
            {
                'name': "activities.Perspective",
                'args':["id", "name", "color", "use_def_color", "categorize_model", "index"],
                'args_str': """id, name, color, use_def_color, categorize_model, "index" """,
            },
            {
                'name': "activities.Category",
                'args':["id", "name", "color", "perspective_id", "index"],
                'args_str': """id, name, color, perspective_id, "index" """,
            },
            {
                'name': "activities.CategorizedActivity",
                'args':["id", "app", "title", "category_id"],
                'args_str': "id, app, title, category_id",
            },
            {
                'name': "activities.CategorizedKeyWord",
                'args':["id", "word", "positive", "category_id"],
                'args_str': "id, word, positive, category_id",
            },
            {
                'name': "activities.AudioActivity",
                'args':["id", "start_time", "end_time", "duration", "start_app", "start_title",
                                        "longest_app", "longest_title", "another_app", "another_title",
                                        "selected", "show_policy"],
                'args_str': "id, start_time, end_time, duration, start_app, start_title,longest_app, longest_title, another_app, another_title,selected, show_policy",
            },
            {
                'name': "activities.ActivityPredictor",
                'args':["id", "p_id", "name", "created_dtime", 
                                            "num_of_labels", "num_of_learning_data", "score", "using", "data_start", "data_end"],
                'args_str': """id, p_id, name, created_dtime, num_of_labels, num_of_learning_data, score, "using", data_start, data_end""",
            },
            {
                'name': "activities.SystemSettings",
                'args':["id", "role", "audio_activity_policy", "duration_threshold",
                                        "strokes_threshold", "distance_threshold"],
                'args_str': "id, role, audio_activity_policy, duration_threshold, strokes_threshold, distance_threshold",
            },        
        ] 

    def migrate(self, old_path, new_path):
        '''
        de = DataExporter()
        de.connect(old_path)
        try:
            for table in self.target_tables:
                de.writeTableData(table['name'], table['args'], table['replace'])
        except Exception as e:
            print(e)
        '''
        old_conn = sqlite3.connect(old_path)
        new_conn = sqlite3.connect(new_path)
        try:
            for table in self.target_tables:
                self.migrate_table(table, old_conn, new_conn)
        except Exception:
            raise
        finally:
            old_conn.close()
            new_conn.close()

    def getTableName(self, target):
        target_list = target.split(".")
        return target_list[0].lower() +"_"+target_list[1].lower()
    
    def create_query_str(self, att_len):
        q_str = ""
        for i in range(att_len):
            if i == att_len-1:
                q_str = q_str +"?"
            else:
                q_str = q_str +"?, "
        return q_str
    
    def convert_to_t(self, tp, add_flag):
        t_list = list(tp)
        if add_flag:
            t_list.append(None)
        return tuple(t_list)


    def migrate_table(self, table, old, new):
        # table:[target, attributes, replace_flag]
        target = table['name']
        attributes = table['args']
        att_str = table['args_str']
        table_name = self.getTableName(target)
        o_cur = old.cursor()
        n_cur = new.cursor()


        #テーブルのデータを全て消去
        delete_sql = "DELETE FROM "+ table_name
        n_cur.execute(delete_sql)
        new.commit()

        #既存テーブルからデータを取得
        select_sql = "SELECT * FROM "+ table_name
        try:
            o_cur.execute(select_sql)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                print(f"{table_name} is not supported by old version. Skip it.")
                return False
        result_set = o_cur.fetchall()

        if len(result_set) > 0:
            # 新しいテーブルにカラムが追加されている場合は、別処理を行う
            att_len = len(attributes)
            add_flag = False
            if len(result_set[0]) == len(attributes):
                pass
            elif target in self.modified_target and len(result_set[0]) == len(attributes)-1:
                add_flag = True
            else:
                return "Error : attribute length not match"
        
            for result in result_set:
                insert_sql = "INSERT INTO " + table_name + "(" + att_str + ") VALUES (" + self.create_query_str(att_len) + ")"
                tv = self.convert_to_t(result, add_flag)
                #print(f"->{insert_sql}")
                #print(f"=>{tv}")
                n_cur.execute(insert_sql, tv)

            new.commit()


            


    