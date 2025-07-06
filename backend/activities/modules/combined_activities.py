from datetime import datetime, timedelta
from activities.models import Activity, AudioActivity
from django.conf import settings
from dateutil.tz import gettz
import pprint
from logging import getLogger,StreamHandler,DEBUG, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

def none_to_str(str):
    if str:
        return str
    else:
        return ""

def get_app(au):
    if au.selected == 0:
        return none_to_str(au.start_app)
    elif au.selected == 1:
        return none_to_str(au.longest_app)
    elif au.selected == 2:
        return none_to_str(au.another_app)
    else:
        return None
    
def get_title(au):
    if au.selected == 0:
        return none_to_str(au.start_title)
    elif au.selected == 1:
        return none_to_str(au.longest_title)
    elif au.selected == 2:
        return none_to_str(au.another_title)
    else:
        return None
        

def get_combined_activities(start_time, end_time, audio_policy):
    #print(f"audio_policy = {audio_policy}")
    # 指定時間の間のwindowイベントとaudioイベントを結合して、windowイベントのリストとして出力
    q_activities = Activity.objects.filter(start_time__gte=start_time, start_time__lte=end_time
                                        ).exclude(title="blank").order_by("start_time")
    activities =[]
    for act in q_activities:
        activities.append(act)
    
    if audio_policy == 0:
        return activities
    else:
        audios = AudioActivity.objects.filter(start_time__gte=start_time, start_time__lte=end_time
                                            ).order_by("start_time")
        
        a_activities = []
        policies = []
        for au in audios:
            #print(f"{au.selected} : {au.longest_app} : {au.longest_title}")
            act = Activity()
            act.start_time = au.start_time
            act.duration = au.duration
            act.distance_x = None
            act.distance_y = None
            act.strokes = None
            act.scrolls = None
            act.app = "audio_stream"
            act.title = get_app(au)+":"+get_title(au)
            a_activities.append(act)
            policies.append(au.show_policy)
        #print(f"audio : {audio_policy}")
        if audio_policy == 1:
            return combined_activities(a_activities, activities)
        elif audio_policy ==2:
            return combined_activities(activities, a_activities)
        else:
            return combine_individual_activities(activities, a_activities, policies)
    

def create_activity(activity, start_time, duration):
    #与えられたactivityを基に、指定されたstart_time, durationを持つオブジェクトを新たに生成して返す
    logger.debug(f"create_activity:{start_time},{duration}")
    act = None
    if duration > 0:
        act = Activity()
        act.start_time = start_time
        act.duration = duration
        act.distance_x = activity.distance_x
        act.distance_y = activity.distance_y
        act.strokes = activity.strokes
        act.scrolls = activity.scrolls
        act.app = activity.app
        act.title = activity.title    
        #activity.start_time = start_time
        #activity.duration = duration
    return act


def combine_individual_activities(q_activities, a_activities, policies):

    activities =[]
    for act in q_activities:
        activities.append(act)

    result = []
    i = 0
    j = 0

    logger.debug(f"length of a_activities = {len(a_activities)}")
    logger.debug(f"length of activities = {len(activities)}")

    while i < len(a_activities):
        #print(f"roop [i] {i}")
        aac = a_activities[i]
        head = aac.start_time
        tail = aac.start_time + timedelta(seconds = aac.duration)
        if policies[i] == 0:    #Audio優先
            while j < len(activities):
                ac = activities[j]
                start = ac.start_time
                end = ac.start_time + timedelta(seconds = ac.duration)

                if(start > tail):
                    logger.debug("-0-")
                    #act = create_activity(bk, head, bk.duration)
                    result.append(aac)
                    head = tail
                    i += 1
                    break
                elif(start > head and tail >= start and end > tail):
                    logger.debug("-1-")
                    logger.debug(f"head:{head.astimezone(gettz(settings.TIME_ZONE))}, tail:{tail.astimezone(gettz(settings.TIME_ZONE))}")
                    logger.debug(f"start:{start.astimezone(gettz(settings.TIME_ZONE))}, end:{end.astimezone(gettz(settings.TIME_ZONE))}")
                    act = create_activity(ac, tail, (end - tail).seconds)
                    if act:
                        activities[j]= act
                    else:
                        j +=1
                    result.append(aac)
                    head = tail
                    start = tail
                    #result.append(fr)
                    #j += 1
                    i += 1
                    #head = end
                    break
                elif(start > head and tail >= end):
                    logger.debug("-2-")
                    j += 1
                elif(head >= start and end > tail):
                    logger.debug("-3-")
                    act = create_activity(ac, start, (head - start).seconds)
                    if act:
                        result.append(act)
                    result.append(aac)
                    head = tail
                    ac = create_activity(ac, tail, (end - tail).seconds)
                    if ac:
                        activities[j]= ac
                    else:
                        j += 1
                    i += 1
                    break
                elif(head >= start and end > head and tail >= end):
                    logger.debug("-4-")
                    act = create_activity(ac, start, (head - start).seconds)
                    if act:
                        result.append(act)
                    j += 1
                    head = end
                elif(head >= end):
                    logger.debug("-5-")
                    act = create_activity(ac, start, (end - start).seconds)
                    if act:
                        result.append(act)
                    j += 1

            if not head == tail:
                logger.debug(f"head:{head.astimezone(gettz(settings.TIME_ZONE))}, tail:{tail.astimezone(gettz(settings.TIME_ZONE))}")
                logger.debug(f"start:{start.astimezone(gettz(settings.TIME_ZONE))}, end:{end.astimezone(gettz(settings.TIME_ZONE))}")
                result.append(create_activity(aac, head, (tail - head).seconds))
                i += 1


        elif policies[i] == 1:    #Window優先
            while j < len(activities):
                ac = activities[j]
                start = ac.start_time
                end = ac.start_time + timedelta(seconds = ac.duration)

                if(start > tail):
                    logger.debug("-0-")
                    act = create_activity(aac, head, (tail - head).seconds)
                    if act:
                        result.append(act)
                    head = tail
                    i += 1
                    break
                elif(start > head and tail >= start and end > tail):
                    logger.debug("-1-")
                    act = create_activity(aac, head, (start - head).seconds)
                    if act:
                        result.append(act)
                    head = tail
                    #result.append(fr)
                    #j += 1
                    i += 1
                    break
                elif(start > head and tail >= end):
                    logger.debug("-2-")
                    act = create_activity(aac, head, (start - head).seconds)
                    if act:
                        result.append(act)
                    result.append(ac)
                    head = end
                    j += 1
                elif(head >= start and end > tail):
                    logger.debug("-3-")
                    i += 1
                    break
                elif(head >= start and end > head and tail >= end):
                    logger.debug("-4-")
                    result.append(ac)
                    j += 1
                    head = end
                elif(head >= end):
                    logger.debug("-5-")
                    result.append(ac)
                    j += 1 

            if not head == tail:
                act = create_activity(aac, head, (tail - head).seconds)
                if act:
                    result.append(act)
                i += 1

        elif policies[i] == 2:    #Audio無効
            i += 1

    #残りの処理
    if j < len(activities):
        while j<len(activities):
            logger.debug("-6-")
            result.append(activities[j])
            j += 1

    #デバッグ用
    #print("-----------")
    #for ac in result:
    #    print(f"{ac.start_time}:{ac.duration}:{ac.app}")
    #print("-----------")

    return result


def combined_activities(fronts, backs):
    # fronts優先で結合を行う

    result = []
    i = 0
    j = 0
    #print(f" length of fronts :{len(fronts)}")
    #print(f" length of backs :{len(backs)}")
    while i < len(backs):
        logger.debug(f"roop [i] {i}")
        bk = backs[i]
        head = bk.start_time
        tail = bk.start_time + timedelta(seconds = bk.duration)
        

        while j < len(fronts):
            logger.debug(f"roop [j] {j}")
            fr = fronts[j]
            start = fr.start_time
            end = fr.start_time + timedelta(seconds = fr.duration)
            logger.debug(f"bk:{i}: {bk.title} head:{head} tail:{tail}")
            logger.debug(f"fr:{j}: {fr.title} start:{start} end:{end}")
            if(start > tail):
                logger.debug("-0-")
                #act = create_activity(bk, head, bk.duration)
                logger.debug(f"-> {bk.start_time} : {bk.duration} : {bk.title}")
                act = create_activity(bk, head, (tail - head).seconds)
                if act:
                    logger.debug(f"-> {act.start_time} : {act.duration} : {act.title}")
                    result.append(act)
                i += 1
                break
            elif(start > head and tail >= start and end > tail):
                logger.debug("-1-")
                act = create_activity(bk, head, (start - head).seconds)
                if act:
                    logger.debug(f"-> {act.start_time} : {act.duration} : {act.title}")
                    result.append(act)
                #result.append(fr)
                #j += 1
                i += 1
                head = end
                break
            elif(start > head and tail >= end):
                logger.debug("-2-")
                act = create_activity(bk, head, (start - head).seconds)
                if act:
                    logger.debug(f"-> {act.start_time} : {act.duration} : {act.title}")
                    result.append(act)
                result.append(fr)
                head = end
                j += 1
            elif(head >= start and end > tail):
                logger.debug("-3-")
                i += 1
                break
            elif(head >= start and end > head and tail >= end):
                logger.debug("-4-")
                logger.debug(f"-> {fr.start_time} : {fr.duration} : {fr.title}")
                result.append(fr)
                j += 1
                bk = create_activity(bk, end, (tail - end).seconds)
                if bk:
                    backs[i] = bk
                    head = end
                else:
                    i += 1
                    break
                
            elif(head >= end):
                logger.debug("-5-")
                logger.debug(f"-> {fr.start_time} : {fr.duration} : {fr.title}")
                result.append(fr)
                j += 1

            #jのループは終了している場合でiのループが残っている場合iを処理
            #print(f"j-loop finished j:{j} >= {len(fronts)} and i:{i} < {len(backs)}")
            if j >= len(fronts) and i <len(backs):
                act = create_activity(bk, head, (tail - head).seconds)
                if act:
                    logger.debug(f"-> {act.start_time} : {act.duration} : {act.title}")
                    result.append(act)
                i += 1
        
        if j >= len(fronts):  
            while i < len(backs):
                bk=backs[i]
                logger.debug(f"-> {bk.start_time} : {bk.duration} : {bk.title}")
                result.append(bk)
                i += 1
            
    #print("exit from the roop.")
    
    logger.debug(f"i:{i}")   
    while i < len(backs):
        bk=backs[i]
        logger.debug(f"-> {bk.start_time} : {bk.duration} : {bk.title}")
        result.append(bk)
        i += 1

    #ここは通らない？
    logger.debug(f"j:{j}")
    while j < len(fronts):
        fr = fronts[j]
        result.append(fr)
        j += 1
    #デバッグ用
    #print("-----------")
    #for ac in result:
    #    print(f"{ac.start_time}:{ac.duration}:{ac.app}")
    #print("-----------")
    return result
