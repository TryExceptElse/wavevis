"""
Module containing the visualization program and model for accessing and
modifying its parameters.
"""

import collections
import math
import vispy.gloo as gloo

N_SOURCES = 4

MODES = collections.OrderedDict((
    ('wave_function', 0),
    ('amplitude', 1)
))

VERT_SHADER = """
attribute vec2 a_position;
void main (void)
{
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

FRAG_SHADER = """ 
#version 130

#define M_PI 3.1415926535897932384626433832795
#define C 40.0  // Rate of wave propagation in visualization.

#define WAVE_FUNCTION 0
#define AMPLITUDE 1

uniform float u_global_time;
uniform int u_mode = 0;

uniform float u_lambda = 4.0;       // Wavelength
uniform float u_contrast = 0.25;

uniform float u_phase[N_SOURCES];   // Source phases, in radians.
uniform float u_amp[N_SOURCES];     // Source amplitudes.
uniform float u_dir[N_SOURCES];     // Source directions, in radians.

/**
 * Finds value of wave at passed position.
 */
float f(vec2 uv, int src) {
    float theta = u_dir[src];
    float x = uv.x * cos(theta) - uv.y * sin(theta);
    float v = sin(
        x / u_lambda + 
        u_phase[src] +
        u_global_time * C / u_lambda
    ) * u_amp[src];
    return v;
}

/**
 * Finds phasor of a specified wave source at a specified position.
 */
vec2 find_phasor(vec2 uv, int src) {
    float relative_phase = u_dir[src];
    float x = uv.x * cos(relative_phase) - uv.y * sin(relative_phase);
    float phase = relative_phase + x / u_lambda;
    float amp = u_amp[src];
    return vec2(sin(phase) * amp, cos(phase) * amp);
}

/**
 * Finds maximum possible amplitude, if all waves were to 
 * mix constructively.
 * Used to determine displayed brightness value.
 */
float find_max_amp() {
    float r = 0.0;
    for (int i=0; i < N_SOURCES; ++i) {
        r += u_amp[i];
    }
    return r;
}

/**
 * Converts passed actual value and maximum value into an rgb value
 * to be displayed.
 */
vec3 value_to_rgb(float v, float max) {
    if (max == 0.0) {
        return vec3(0.0, 0.0, 0.0);
    }
    float display_v = (v / max / 2 + 0.5) * u_contrast + u_contrast / 2;
    return vec3(display_v, display_v, display_v);
}

/**
 * Finds sum of all wave function results.
 */
float wave_sum(vec2 uv) {
    float v = 0.0;
    for (int i = 0; i < N_SOURCES; ++i) {
        v += f(uv, i);
    }
    return v;
}

/**
 * Finds amplitude sum at a given position.
 */
float amplitude_sum(vec2 uv) {
    vec2 phasor_sum = vec2(0.0, 0.0);
    for (int i = 0; i < N_SOURCES; ++i) {
        phasor_sum += find_phasor(uv, i);
    }
    return length(phasor_sum);
}

void main(void) {
    float max = find_max_amp();
    float v;
    vec2 uv = gl_FragCoord.xy;
    switch(u_mode) {
        case WAVE_FUNCTION:
            v = wave_sum(uv);
            break;
        case AMPLITUDE:
            v = amplitude_sum(uv);
            break;
    }
    gl_FragColor = vec4(value_to_rgb(v, max), 1.000);
}
""".replace('N_SOURCES', str(N_SOURCES))  # .format() breaks the many brackets.


class Model:
    """
    Stores OpenGL program and other information, along with means
    to manipulate simulated emitter sources.
    """
    def __init__(self):
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['u_global_time'] = 0
        self.program['a_position'] = [(-1, -1), (-1, +1),
                                      (+1, -1), (+1, +1)]
        self.contrast = 0.5  # Uses setter to change uniform.
        self.wavelength = 4  # Uses setter to change uniform.
        self.mode = 'wave_function'

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
    def mode(self, mode: str):
        if mode not in ('amplitude', 'wave_function'):
            raise ValueError('Unexpected input: {}'.format(mode))
        self.program['u_mode'] = MODES[mode]


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
