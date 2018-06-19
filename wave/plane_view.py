import vispy.gloo as gloo
import vispy.app as app


class PlaneView(app.Canvas):
    def __init__(self, program: gloo.Program):
        # If the program segfaults upon initializing canvas, using
        # wheels to install PyQt5, installing the following libraries
        # are likely to fix the issue:
        # libglu1-mesa-dev, mesa-common-dev
        super().__init__(size=(800, 600), keys='interactive')
        self.program = program

        self.apply_zoom()

        gloo.set_state(blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self._timer = app.Timer('auto', connect=self.on_timer_event,
                                start=True)

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *self.physical_size)

    def on_draw(self, event):
        gloo.clear('white')
        self.program.draw(mode='triangle_strip')

    def on_timer_event(self, event):
        if self._timer.running:
            self.program["u_global_time"] += event.dt
        # Fix weird floating point precision issues.
        # (Too large a value into OpenGL's sin function results
        #  in bad output)
        if self.program['u_global_time'] > 6e2:
            self.program['u_global_time'] = 0
        self.update()

    def apply_zoom(self):
        gloo.set_viewport(0, 0, *self.physical_size)
