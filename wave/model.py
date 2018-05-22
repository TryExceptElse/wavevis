"""
Module containing the visualization program and model for accessing and
modifying its parameters.
"""

import collections
import math
import vispy.gloo as gloo

import wave.shader as shader

N_SOURCES = 4

MODES = collections.OrderedDict((
    ('wave function', 0),
    ('amplitude', 1),
    ('relative phase', 2),
    ('instantaneous phase', 3),
))


class Model:
    """
    Stores OpenGL program and other information, along with means
    to manipulate simulated emitter sources.
    """
    def __init__(self):
        frag_shader = shader.expand_shader(
            shader.FRAG_SHADER, N_SOURCES=N_SOURCES)
        self.program = gloo.Program(shader.VERT_SHADER, frag_shader)
        self.program['u_global_time'] = 0
        self.program['a_position'] = [(-1, -1), (-1, +1),
                                      (+1, -1), (+1, +1)]
        self.contrast = 0.5  # Uses setter to change uniform.
        self.wavelength = 4  # Uses setter to change uniform.
        self.mode = 0

        self.sources = [SourceControl(self.program, i)
                        for i in range(N_SOURCES)]

    @property
    def contrast(self):
        return self.program['u_contrast']

    @contrast.setter
    def contrast(self, new_contrast: float):
        if not 0 <= new_contrast <= 1:
            raise ValueError('Passed contrast outside 0-1: {}'
                             .format(new_contrast))
        self.program['u_contrast'] = new_contrast

    @property
    def wavelength(self):
        return self.program['u_lambda']

    @wavelength.setter
    def wavelength(self, new_wavelength):
        if new_wavelength <= 0:
            raise ValueError('Wavelength must be > 0. Got: {}'
                             .format(new_wavelength))
        self.program['u_lambda'] = new_wavelength

    @property
    def mode(self):
        return self.program['u_mode']

    @mode.setter
    def mode(self, mode: str or int):
        if isinstance(mode, int):
            index = mode
        elif isinstance(mode, str):
            if mode not in MODES:
                raise ValueError('Unexpected mode: {}'.format(mode))
            index = MODES[mode]
        else:
            raise ValueError('Unexpected input: {}'.format(mode))
        self.program['u_mode'] = index


class SourceControl:
    """ Controls parameters of an emitter in the OpenGL program. """
    def __init__(self, program: gloo.Program, i: int):
        self.program = program
        self.i = i

        self.amp = 0
        self.phase = 0
        self.dir = 0

    @property
    def amp(self):
        return self.program['u_amp[{}]'.format(self.i)]

    @amp.setter
    def amp(self, new_amp: float):
        if new_amp < 0:
            raise ValueError('Passed new amp < 0. amp: {}'.format(new_amp))
        self.program['u_amp[{}]'.format(self.i)] = new_amp

    @property
    def phase(self):
        return self.program['u_phase[{}]'.format(self.i)]

    @phase.setter
    def phase(self, new_phase: float):
        self.program['u_phase[{}]'.format(self.i)] = new_phase % (2 * math.pi)

    @property
    def dir(self):
        return self.program['u_dir[{}]'.format(self.i)]

    @dir.setter
    def dir(self, new_dir: float):
        self.program['u_dir[{}]'.format(self.i)] = new_dir % (2 * math.pi)
