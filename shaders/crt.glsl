// Retro-Terminals CRT shader for Ghostty.
//
// Curvature + scanlines + aperture grille + chromatic aberration + soft
// phosphor bloom + faint mains flicker + an inset rounded BEZEL — the parts an
// iTerm2 profile could only fake with a static scanline PNG. Tuned to stay
// readable, not seasick.
//
// Ghostty attaches this automatically to the "tube" machines (the ones that
// got the iTerm2 scanline bezel) via build_ghostty.py. It follows the
// Shadertoy convention: iChannel0 is the rendered terminal, iResolution is the
// pixel size, iTime advances when `custom-shader-animation = true`.
//
// Tweak the constants, then either re-run build_ghostty.py or just edit the
// live copy at ~/.config/ghostty/shaders/crt.glsl and reopen the window —
// Ghostty hot-reloads shaders on ⌘⇧, (reload config). The Ghostty Studio
// (ghostty-studio.html) tunes all of these live and publishes them back.

const float CURVATURE  = 4.0;    // higher = flatter tube (4–8 subtle, 2–3 fishbowl)
const float SCANLINE   = 0.15;   // scanline darkness (0 = off)
const float GRILLE     = 0.05;   // aperture-grille column tint depth
const float ABERRATION = 0.0015; // RGB horizontal split amount
const float BLOOM      = 0.06;   // phosphor glow strength
const float FLICKER    = 0.02;   // mains flicker depth (0 = rock steady)
const float BRIGHTNESS = 1.35;   // gain to offset scanline/vignette dimming (1.0 = none)
const float BEZEL      = 0.06;   // screen inset from the window edge (0 = edge-to-edge)
const float CORNER     = 0.10;   // rounded-corner radius of the tube glass

// Barrel distortion — bulge the flat texture into a curved tube.
vec2 curve(vec2 uv) {
    uv = uv * 2.0 - 1.0;
    vec2 offset = abs(uv.yx) / vec2(CURVATURE + 2.0, CURVATURE);
    uv += uv * offset * offset;
    return uv * 0.5 + 0.5;
}

// Signed distance to a rounded box (negative inside). `b` is the half-extent,
// `r` the corner radius. (`half` is reserved on Metal — hence halfExt below.)
float roundedBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + r;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv  = fragCoord / iResolution.xy;
    vec2 cuv = curve(uv);

    // The tube occupies an inset, rounded rectangle; the margin is the bezel.
    vec2 p = cuv * 2.0 - 1.0;
    vec2 halfExt = vec2(1.0 - BEZEL);
    float d = roundedBox(p, halfExt, CORNER);

    if (d > 0.0) {
        // Bezel frame: dark plastic with a faint lit rim next to the glass.
        float rim = smoothstep(0.05, 0.0, d);
        fragColor = vec4(mix(vec3(0.015), vec3(0.07), rim), 1.0);
        return;
    }

    // Remap the inner screen region back to [0,1] texture space.
    vec2 suv = p / halfExt * 0.5 + 0.5;

    // Chromatic aberration: split R and B horizontally around G.
    vec3 col;
    col.r = texture(iChannel0, vec2(suv.x + ABERRATION, suv.y)).r;
    col.g = texture(iChannel0, suv).g;
    col.b = texture(iChannel0, vec2(suv.x - ABERRATION, suv.y)).b;

    // Soft phosphor bloom (4-tap cross blur of the bright areas).
    vec3 bloom = texture(iChannel0, suv + vec2( 0.0010, 0.0)).rgb
               + texture(iChannel0, suv + vec2(-0.0010, 0.0)).rgb
               + texture(iChannel0, suv + vec2(0.0,  0.0015)).rgb
               + texture(iChannel0, suv + vec2(0.0, -0.0015)).rgb;
    col += bloom * BLOOM;

    // Scanlines (horizontal) and aperture grille (vertical).
    float scan   = 0.5 + 0.5 * sin(suv.y * iResolution.y * 3.14159265);
    col *= 1.0 - SCANLINE * (1.0 - scan);
    float grille = 0.5 + 0.5 * sin(suv.x * iResolution.x * 1.57079633);
    col *= 1.0 - GRILLE * (1.0 - grille);

    // Vignette — darken the corners of the tube.
    float vig = 16.0 * suv.x * suv.y * (1.0 - suv.x) * (1.0 - suv.y);
    col *= pow(clamp(vig, 0.0, 1.0), 0.25);

    // Inner-glass shadow: darken just inside the bezel edge.
    col *= 0.85 + 0.15 * smoothstep(0.0, 0.05, -d);

    // Brightness gain — offset the dimming from scanlines/grille/vignette.
    col *= BRIGHTNESS;

    // Faint mains flicker.
    col *= 1.0 - FLICKER * (0.5 + 0.5 * sin(iTime * 6.28318 * 1.2)) * 0.5;

    fragColor = vec4(col, 1.0);
}
