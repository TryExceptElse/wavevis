
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
#define RELATIVE_PHASE 2
#define INSTANTANEOUS_PHASE 3

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
    float dir = u_dir[src];
    float x = uv.x * cos(dir) - uv.y * sin(dir);
    float phase = u_phase[src] + x / u_lambda;
    float amp = u_amp[src];
    return vec2(sin(phase) * amp, cos(phase) * amp);
}

/**
 * Finds phasor of a specified wave source at a specified position.
 */
vec2 find_instant_phasor(vec2 uv, int src) {
    float dir = u_dir[src];
    float x = uv.x * cos(dir) - uv.y * sin(dir);
    float phase = u_phase[src] + x / u_lambda + 
        mod(u_global_time * C, 2 * u_lambda * M_PI) / u_lambda;
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

vec3 hsv2rgb(vec3 hsv) {
    float      hh, p, q, t, ff;
    int        i;
    vec3       rgb;

    if(hsv.s <= 0.0) {
        rgb.x = hsv.x;
        rgb.y = hsv.x;
        rgb.z = hsv.x;
        return rgb;
    }
    hh = hsv.x;
    if(hh >= 360.0) hh = 0.0;
    hh /= 60.0;
    i = int(hh);
    ff = hh - i;
    p = hsv.z * (1.0 - hsv.y);
    q = hsv.z * (1.0 - (hsv.y * ff));
    t = hsv.z * (1.0 - (hsv.y * (1.0 - ff)));

    switch(i) {
        case 0:
            rgb.x = hsv.z;
            rgb.y = t;
            rgb.z = p;
            break;
        case 1:
            rgb.x = q;
            rgb.y = hsv.z;
            rgb.z = p;
            break;
        case 2:
            rgb.x = p;
            rgb.y = hsv.z;
            rgb.z = t;
            break;
        case 3:
            rgb.x = p;
            rgb.y = q;
            rgb.z = hsv.z;
            break;
        case 4:
            rgb.x = t;
            rgb.y = p;
            rgb.z = hsv.z;
            break;
        case 5:
        default:
            rgb.x = hsv.z;
            rgb.y = p;
            rgb.z = q;
            break;
    }
    return rgb;
}

/**
 * Converts a passed angle into an rgb value.
 */
vec3 theta2rgb(float theta) {
    if (theta < 0.0) {
        theta += M_PI * 2.0;
    }
    vec3 hsv = vec3(theta / M_PI * 180.0, u_contrast, u_contrast);
    return hsv2rgb(hsv);
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

/**
 * Finds amplitude sum at a given position.
 */
float phase_sum(vec2 uv) {
    vec2 phasor_sum = vec2(0.0, 0.0);
    for (int i = 0; i < N_SOURCES; ++i) {
        phasor_sum += find_phasor(uv, i);
    }
    float theta = atan(phasor_sum.y / phasor_sum.x);
    if (phasor_sum.x < 0.0) {
        theta += M_PI;
    }
    return theta;
}

/**
 * Finds amplitude sum at a given position.
 */
float instant_phase_sum(vec2 uv) {
    vec2 phasor_sum = vec2(0.0, 0.0);
    for (int i = 0; i < N_SOURCES; ++i) {
        phasor_sum += find_instant_phasor(uv, i);
    }
    float theta = atan(phasor_sum.y / phasor_sum.x);
    if (phasor_sum.x < 0.0) {
        theta += M_PI;
    }
    return theta;
}

void main(void) {
    float max, v;
    vec3 rgb;
    vec2 uv = gl_FragCoord.xy;
    switch(u_mode) {
        case WAVE_FUNCTION:
            v = wave_sum(uv);
            rgb = value_to_rgb(v, find_max_amp());
            break;
        case AMPLITUDE:
            v = amplitude_sum(uv);
            rgb = value_to_rgb(v, find_max_amp());
            break;
        case RELATIVE_PHASE:
            rgb = theta2rgb(phase_sum(uv));
            break;
        case INSTANTANEOUS_PHASE:
            rgb = theta2rgb(instant_phase_sum(uv));
            break;
    }
    gl_FragColor = vec4(rgb, 1.000);
}
"""


def expand_shader(shader: str, **kwargs) -> str:
    for k, v in kwargs.items():
        shader = shader.replace(k, str(v))
    return shader
