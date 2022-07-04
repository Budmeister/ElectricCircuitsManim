from manim import *

def occur_at(start_time, length, total_length, rate_func=None):
    if rate_func is None:
        rate_func = smooth
    start_time /= total_length
    length /= total_length
    def func(alpha):
        return rate_func(max(min((alpha - start_time) / length, 1), 0))
    return {"rate_func": func, "run_time": total_length}

def norm(arr):
    return arr / np.sqrt(np.dot(arr, arr))

def perp(arr):
    retval = arr.copy()
    temp = retval[1]
    retval[1] = retval[0]
    retval[0] = -temp
    return retval

def fancy(mob, length=1, animation=DrawBorderThenFill, rate_func=None, *args, **kwargs):
    return AnimationGroup(*[
        animation(mob[i], *args, **occur_at(i / len(mob) * length, (len(mob) - i) / len(mob) * length, length, rate_func=rate_func), introducer=False, **kwargs)
        # animation(mob[i], run_time=(len(mob) - i) / len(mob) * length, lag_ratio=i / len(mob))
        for i in range(len(mob))
    ])

def consecutive(mob, length, animation=DrawBorderThenFill, rate_func=None, *args, **kwargs):
    return AnimationGroup(*[
        animation(mob[i], *args, **occur_at(i / len(mob) * length, 1 / len(mob) * length, length, rate_func=rate_func), introducer=False, **kwargs)
        for i in range(len(mob))
    ])