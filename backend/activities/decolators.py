# デコレータを有効にするかどうかをconditionによって決めるデコレータ
def attach_decorator(condition, decorator):
    return decorator if condition else lambda x: x

