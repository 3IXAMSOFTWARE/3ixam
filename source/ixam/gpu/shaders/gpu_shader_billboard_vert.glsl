#pragma IXAM_REQUIRE(common_view_lib.glsl)

void main() {
    mat4 newModelView = ModelViewMatrix;
    // Remove rotations from MV matrix
    newModelView[0][0] = 1.0;
    newModelView[0][1] = 0.0;
    newModelView[0][2] = 0.0;

    newModelView[1][0] = 0.0;
    newModelView[1][1] = 1.0;
    newModelView[1][2] = 0.0;

    newModelView[2][0] = 0.0;
    newModelView[2][1] = 0.0;
    newModelView[2][2] = 1.0;

    vec4 newPos = ProjectionMatrix * newModelView * vec4(pos.xy * scale, 0.0, 1.0);

    gl_Position = newPos;
}
