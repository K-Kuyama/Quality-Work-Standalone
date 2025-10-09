'''
Created on 2025/08/24

@author: kuyamakazuhiro
'''

# カテゴリーidのリストから対応するカテゴリー名に変換する。
# pandas DataFrame用
def labelToName(df, labels):
    result_list = []
    for label in labels:
        matched = df[df.iloc[:, 1] == label]
        name = matched.iloc[0, 2]
        result_list.append(name)
    return result_list

# 辞書リスト用
def labelToNameforList(rows, labels):
    result_list = []
    for label in labels:
        matched = next((r for r in rows if r['category_id'] == label), None)
        result_list.append(matched['name'])
    return result_list


#文章から助詞、助動詞、記号は省き、品詞ごとの分ち書きにする。
'''
def tokenize(mecab, text):
    # 分けてノードごとにする
    node = mecab.parseToNode(text)
    terms = []
    while node:
        # 単語
        term = node.surface
        # 品詞
        pos = node.feature.split(',')[0]
        # もし品詞が条件と一致してたら
        if pos not in ["助詞", "助動詞", "記号"]:
            terms.append(term)
        node = node.next
    # 文字列連結
    text_result = ' '.join(terms)
    return text_result
'''

def tokenize(janome_t, text):
    terms = []
    # Janomeのtokenizerで分かち書きする
    for token in janome_t.tokenize(text):
        term = token.surface           # 形態素（単語）
        pos = token.part_of_speech.split(',')[0]  # 品詞の大分類（名詞, 動詞, 助詞, 記号など）

        # MeCab版と同じく助詞・助動詞・記号は除外
        if pos not in ["助詞", "助動詞", "記号"]:
            terms.append(term)

    # 空白区切りで返す
    text_result = ' '.join(terms)
    return text_result


def evaluation_report(t_vals, p_vals, index):
    precision_info = count_correct(p_vals, t_vals)
    recall_info = count_correct(t_vals, p_vals)
    i=0
    report = []
    for id in precision_info.keys():
        pr = precision_info[id][1] / precision_info[id][0] #precisionを計算
        rc = recall_info[id][1] / recall_info[id][0] #recallを計算
        f1 = 0
        if pr != 0 or rc != 0:
            f1 = (2*pr*rc)/(pr+rc)
        item={'id':id,
            'category':index[int(id)],
            'precision':pr,
            'pr_base':[precision_info[id][1],precision_info[id][0]],
            'recall':rc, 
            'rc_base': [recall_info[id][1],recall_info[id][0]],
            'f1_score':f1,
            'support':recall_info[id][0]
            }
        report.append(item)
    return report


def count_correct(a_vals, b_vals):   
    # 同じ長さのリストa_valsとb_valsの内容がマッチした数を数える
    # precision_info[キー] =[アイテムの全体数, マッチした数]
    i=0
    precision_info = dict()
    while i <len(a_vals):
        id = a_vals[i]
        if id not in precision_info.keys():
            if(a_vals[i] == b_vals[i]):
                precision_info[id]=[1,1]
            else:
                precision_info[id]=[1,0]
        else:
            precision_info[id][0] += 1
            if(a_vals[i] == b_vals[i]):
                precision_info[id][1] += 1
        i += 1

    return precision_info 



