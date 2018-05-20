from PyQt5 import uic
from PyQt5.Qt import *

import os
import math

from .plane_view import PlaneView
from .model import Model, SourceControl

import settings


class MainWindow(QMainWindow):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model
        uic.loadUi(os.path.join(settings.UI_DIR, 'mainwindow.ui'), self)
        self.set_up_main_view()
        self.show()

    def set_up_main_view(self):
        canvas = PlaneView(self.model.program)
        assert isinstance(self.mainViewVBox, QVBoxLayout)
        canvas.native.setParent(self)
        self.mainViewVBox.addWidget(canvas.native)

        self.model.sources[0].amp = 1

        [self.rightSideVBox.addWidget(EmitterControlWidget(source))
         for source in self.model.sources]

        # Give first source amp 1
        self.model.sources[0].amp = 1


class EmitterControlWidget(QWidget):
    def __init__(self, source_control: SourceControl):
        super().__init__()
        self.source_control = source_control
        uic.loadUi(
            os.path.join(settings.UI_DIR, 'emitter_controller.ui'), self)

        self.set_up_ui()

    def set_up_ui(self):
        self.nameLabel.setText('Emitter #{}'.format(self.source_control.i))

        amp_slider_ratio = 1 / 99  # Slider value / actual ratio.

        def on_amp_slider_changed(x):
            self.source_control.amp = x * amp_slider_ratio

        self.amplitudeSlider.valueChanged.connect(on_amp_slider_changed)
        self.amplitudeSlider.setValue(
            self.source_control.amp / amp_slider_ratio)

        phase_slider_ratio = 1 / 99 * 2 * math.pi  # Slider v / actual ratio.

        def on_phase_slider_changed(x):
            self.source_control.phase = x * phase_slider_ratio

        self.phaseSlider.valueChanged.connect(on_phase_slider_changed)
        self.phaseSlider.setValue(self.source_control.amp / phase_slider_ratio)

        def on_dir_slider_changed(x):
            self.source_control.dir = x / 99 * 2 * math.pi

        self.directionSlider.valueChanged.connect(on_dir_slider_changed)
