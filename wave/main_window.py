from PyQt5 import uic
from PyQt5.Qt import *

import os
import math

from .plane_view import PlaneView
from .model import Model, SourceControl, MODES

import settings


class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        uic.loadUi(os.path.join(settings.UI_DIR, 'mainwindow.ui'), self)

        # Give first source amp 1
        self.model.sources[0].amp = 1

        self.set_up_main_view()
        self.show()

    def set_up_main_view(self):
        canvas = PlaneView(self.model.program)
        assert isinstance(self.mainViewVBox, QVBoxLayout)
        canvas.native.setParent(self)
        self.mainViewVBox.addWidget(canvas.native)

        [self.rightSideVBox.addWidget(EmitterControlWidget(source))
         for source in self.model.sources]

        def set_up_mode_selector():
            def on_mode_changed(index: int):
                self.model.mode = self.modeSelector.itemText(index)

            self.modeSelector.addItems(MODES)
            self.modeSelector.setCurrentIndex(0)
            self.modeSelector.currentIndexChanged.connect(on_mode_changed)

        set_up_mode_selector()


class EmitterControlWidget(QWidget):
    def __init__(self, source_control: SourceControl):
        super().__init__()
        self.source_control = source_control
        uic.loadUi(
            os.path.join(settings.UI_DIR, 'emitter_controller.ui'), self)

        self.set_up_ui()

    def set_up_ui(self):
        self.nameLabel.setText('Emitter #{}'.format(self.source_control.i))

        # Set up amplitude controls -----------------------------------

        amp_slider_ratio = 1 / 99  # Slider value / actual ratio.

        def on_amp_slider_changed(x):
            amp = x * amp_slider_ratio
            self.source_control.amp = amp
            self.amplitudeEdit.setText('{:.3}'.format(amp))

        def on_amp_edit_changed(s: str):
            try:
                amp = float(s)
            except ValueError:
                amp = 0
            self.source_control.amp = amp
            self.amplitudeSlider.blockSignals(True)
            self.amplitudeSlider.setValue(amp / amp_slider_ratio)
            self.amplitudeSlider.blockSignals(False)

        @with_blocked(self.amplitudeSlider, self.amplitudeEdit)
        def initialize_amp_widget_values():
            initial_amp = float(self.source_control.amp)
            self.amplitudeSlider.setValue(initial_amp / amp_slider_ratio)
            self.amplitudeEdit.setText('{:.3}'.format(initial_amp))

        self.amplitudeSlider.valueChanged.connect(on_amp_slider_changed)
        self.amplitudeEdit.textChanged.connect(on_amp_edit_changed)
        initialize_amp_widget_values()

        # Set up phase controls ---------------------------------------

        phase_slider_ratio = 1 / 99 * 2 * math.pi  # Slider v / actual ratio.

        def on_phase_slider_changed(x):
            phase = x * phase_slider_ratio
            self.source_control.phase = phase
            self.phaseEdit.setText(format_angle(phase))

        @with_blocked(self.phaseSlider)
        def on_phase_edit_changed(s: str):
            try:
                phase = parse_theta(s)
            except ValueError:
                phase = 0
            self.source_control.phase = phase
            self.phaseSlider.setValue(phase / phase_slider_ratio)

        @with_blocked(self.phaseSlider, self.phaseEdit)
        def initialize_phase_widget_values():
            phase = self.source_control.phase
            self.phaseSlider.setValue(phase / phase_slider_ratio)
            self.phaseEdit.setText(format_angle(phase))

        self.phaseSlider.valueChanged.connect(on_phase_slider_changed)
        self.phaseEdit.textChanged.connect(on_phase_edit_changed)
        initialize_phase_widget_values()

        # Set up direction controls -----------------------------------

        dir_slider_ratio = 1 / 99 * 2 * math.pi  # Slider v / actual ratio.

        def on_dir_slider_changed(x):
            direction = x * dir_slider_ratio
            self.source_control.dir = direction
            self.directionEdit.setText(format_angle(direction))

        @with_blocked(self.directionSlider)
        def on_dir_edit_changed(s: str):
            try:
                direction = parse_theta(s)
            except ValueError:
                direction = 0
            self.source_control.dir = direction
            self.directionSlider.setValue(direction / dir_slider_ratio)

        @with_blocked(self.phaseSlider, self.phaseEdit)
        def initialize_dir_widget_values():
            direction = self.source_control.dir / dir_slider_ratio
            self.directionSlider.setValue(direction / amp_slider_ratio)
            self.directionEdit.setText(format_angle(direction))

        self.directionSlider.valueChanged.connect(on_dir_slider_changed)
        self.directionEdit.textChanged.connect(on_dir_edit_changed)
        initialize_dir_widget_values()


def parse_theta(s: str):
    """
    Parses string for an angle in radians.
    :param s: str representing angle.
    :return: Angle in radians
    :raises: ValueError if str cannot be parsed.
    """
    suffix = ''
    for possible_suffix in 'pi', 'π', 'deg', 'd', '°':
        if s.endswith(possible_suffix):
            suffix = possible_suffix
    base_v = float(s[:-len(suffix)] if len(suffix) else s)
    if not suffix:
        theta = base_v
    elif suffix in ('pi', 'π'):
        theta = base_v * math.pi
    elif suffix in ('deg', 'd', '°'):
        theta = base_v / 180 * math.pi
    else:
        raise ValueError
    return theta


def format_angle(theta: float):
    return '{:.3}π'.format(float(theta) / math.pi)


def with_blocked(*widgets):
    def decorator(f):
        def wrapper(*args, **kwargs):
            [widget.blockSignals(True) for widget in widgets]
            f(*args, **kwargs)
            [widget.blockSignals(False) for widget in widgets]
        wrapper.__name__ = f.__name__ + '_wrapper'
        return wrapper
    return decorator
