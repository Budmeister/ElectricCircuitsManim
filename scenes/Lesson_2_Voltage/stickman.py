from manim import *
from manim_extensions import *

class StickMan(VGroup):
    def get_coords(self):
        coords = {
            "leg_and_body_start" : (self._height / 2 - np.sqrt(2) * self._width / 2) * DOWN,
            "arm_start" : UP * self.shoulder_height,
            "body_end" : (self._height / 2 - 2 * self.head_radius) * UP,
            "head_center" : (self._height / 2 - self.head_radius) * UP
        }
        coords.update({
            "left_leg_end"  : coords["leg_and_body_start"] + polar2D(self.leg_length, -np.pi / 2 - self.left_leg_angle),
            "right_leg_end" : coords["leg_and_body_start"] + polar2D(self.leg_length, -np.pi / 2 + self.right_leg_angle),
            "left_arm_end"  : coords["arm_start"] + polar2D(self.arm_length, np.pi - self.left_arm_angle),
            "right_arm_end" : coords["arm_start"] + polar2D(self.arm_length, self.right_arm_angle),
        })
        for coord in coords.values():
            coord[:] = rotate_vector(coord, self._rotate)
            coord += self._center
        return coords
    
    def update_from_coords(self, coords=None):
        if coords is None:
            coords = self.get_coords()
        self.coords = coords
        self.left_leg.become(Line(coords["leg_and_body_start"], coords["left_leg_end"])).shift(ORIGIN)
        self.right_leg.become(Line(coords["leg_and_body_start"], coords["right_leg_end"])).shift(ORIGIN)
        self.body.become(Line(coords["leg_and_body_start"], coords["body_end"])).shift(ORIGIN)
        self.left_arm.become(Line(coords["arm_start"], coords["left_arm_end"])).shift(ORIGIN)
        self.right_arm.become(Line(coords["arm_start"], coords["right_arm_end"])).shift(ORIGIN)
        self.head.become(Circle(self.head_radius).shift(coords["head_center"]))
        self.set_color(self._color)
        
    
    def __init__(
            self,
            location=ORIGIN,
            width=1.5,
            height=3,
            leg_angle=np.pi / 4,
            arm_angle=np.pi / 6,
            shoulder_height=0.2,
            head_radius=0.35,
            color=WHITE
    ):
        super().__init__()
        leg_length = np.sqrt(2) * width / 2
        arm_length = width / np.sqrt(3)

        leg_and_body_start = (height / 2 - np.sqrt(2) * width / 2) * DOWN
        arm_start = UP * shoulder_height
        body_end = (height / 2 - 2 * head_radius) * UP
        head_center = (height / 2 - head_radius) * UP
        left_leg_end  = leg_and_body_start + polar2D(leg_length, -np.pi / 2 - leg_angle)
        right_leg_end = leg_and_body_start + polar2D(leg_length, -np.pi / 2 + leg_angle)
        left_arm_end  = arm_start + polar2D(arm_length, np.pi - arm_angle)
        right_arm_end = arm_start + polar2D(arm_length, arm_angle)
        
        self.left_leg = Line(leg_and_body_start, left_leg_end)
        self.right_leg = Line(leg_and_body_start, right_leg_end)
        self.body = Line(leg_and_body_start, body_end)
        self.left_arm = Line(arm_start, left_arm_end)
        self.right_arm = Line(arm_start, right_arm_end)
        self.head = Circle(head_radius).shift(head_center)

        self.arm_start = Dot(arm_start, fill_opacity=0, stroke_width=0)
        self.leg_start = Dot(leg_and_body_start, fill_opacity=0, stroke_width=0)

        self.add(
            self.left_leg,
            self.right_leg,
            self.body,
            self.left_arm,
            self.right_arm,
            self.head,
            self.arm_start,
            self.leg_start
        )
        self.indices = {
            "left_leg" : 0,
            "right_leg" : 1,
            "body" : 2,
            "left_arm" : 3,
            "right_arm" : 4,
            "head" : 5,
            "arm_start" : 6,
            "leg_start" : 7
        }
        self.set_color(color)
        self.shift(location)
        # self.add_updater(lambda m: None)
    
    def _get_submob_point(self, key, point):
        return getattr(self[self.indices[key]], "get_" + point)()

    def get_right_arm_end(self):
        return self._get_submob_point("right_arm", "end")

    def get_left_arm_end(self):
        return self._get_submob_point("left_arm", "end")

    def get_right_leg_end(self):
        return self._get_submob_point("right_leg", "end")

    def get_left_leg_end(self):
        return self._get_submob_point("left_leg", "end")

    def get_right_arm_start(self):
        return self._get_submob_point("right_arm", "start")

    def get_left_arm_start(self):
        return self._get_submob_point("left_arm", "start")

    def get_right_leg_start(self):
        return self._get_submob_point("right_leg", "start")

    def get_left_leg_start(self):
        return self._get_submob_point("left_leg", "start")
    
    def _wiggle_angle(self, angle, times, side, kind, *args, **kwargs):
        rate_func = kwargs.get("rate_func", there_and_back)
        kwargs["rate_func"] = lambda a: rate_func((a * times) % 1)

        submob = getattr(self, side + "_" + kind)
        pivot = getattr(self, kind + "_start").get_center()

        return Rotate(submob, angle=angle, about_point=pivot, *args, **kwargs)
    
    def wiggle_left_arm(self, angle=np.pi / 6, times=3, *args, **kwargs):
        return self._wiggle_angle(angle, times, "left", "arm", *args, **kwargs)
    
    def wiggle_right_arm(self, angle=-np.pi / 6, times=3, *args, **kwargs):
        return self._wiggle_angle(angle, times, "right", "arm", *args, **kwargs)

    def wiggle_left_leg(self, angle=np.pi / 6, times=3, *args, **kwargs):
        return self._wiggle_angle(angle, times, "left", "leg", *args, **kwargs)
        
    def wiggle_right_leg(self, angle=-np.pi / 6, times=3, *args, **kwargs):
        return self._wiggle_angle(angle, times, "right", "leg", *args, **kwargs)

class StickManTest(Scene):
    def construct(self):
        stickman = StickMan(leg_angle=np.pi / 6).scale(2/3).shift(LEFT).rotate(PI)
        self.play(Create(stickman))
        self.play(stickman.wiggle_right_arm())
        # rotated_stickman = stickman.copy().rotate(PI)
        # self.play(stickman.wiggle_right_arm())
        self.play(stickman.animate.rotate(PI))
        self.wait()