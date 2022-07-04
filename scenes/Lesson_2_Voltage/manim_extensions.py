from manim import *
import cairo
import itertools as it

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

def polar2D(mag, angle):
    return np.array([mag * np.cos(angle), mag * np.sin(angle), 0])


def set_cairo_context_color(self, ctx, rgbas, vmobject):
    """Sets the color of the cairo context

    Parameters
    ----------
    ctx : cairo.Context
        The cairo context
    rgbas : np.ndarray
        The RGBA array with which to color the context.
    vmobject : VMobject
        The VMobject with which to set the color.

    Returns
    -------
    Camera
        The camera object
    """
    if len(rgbas) == 1:
        # Use reversed rgb because cairo surface is
        # encodes it in reverse order
        ctx.set_source_rgba(*rgbas[0][2::-1], rgbas[0][3])
    else:
        if hasattr(vmobject, "radial_gradient") and vmobject.radial_gradient:
            center = vmobject.get_center()
            center = self.transform_points_pre_display(vmobject, np.array([center]))[0]
            radius = np.array([
                np.dot(point - center, point - center) for point in vmobject.points
            ])
            radius = radius.max()
            radius = np.sqrt(radius)
            pat = cairo.RadialGradient(*center[:2], 0, *center[:2], radius)
            step = 1.0 / (len(rgbas) - 1)
            offsets = np.arange(0, 1 + step, step)
            for rgba, offset in zip(rgbas, offsets):
                pat.add_color_stop_rgba(offset, *rgba[2::-1], rgba[3])
            ctx.set_source(pat)
        else:
            points = vmobject.get_gradient_start_and_end_points()
            points = self.transform_points_pre_display(vmobject, points)
            pat = cairo.LinearGradient(*it.chain(*(point[:2] for point in points)))
            step = 1.0 / (len(rgbas) - 1)
            offsets = np.arange(0, 1 + step, step)
            for rgba, offset in zip(rgbas, offsets):
                pat.add_color_stop_rgba(offset, *rgba[2::-1], rgba[3])
            ctx.set_source(pat)
    return self
Camera.set_cairo_context_color = set_cairo_context_color
