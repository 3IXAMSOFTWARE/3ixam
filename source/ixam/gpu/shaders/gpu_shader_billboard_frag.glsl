
void main() {
    fragColor = color;
    if (lineSmooth) {
        fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(interp.smoothline), 0.0, 1.0);
    }
    fragColor = ixam_srgb_to_framebuffer_space(fragColor);
}
