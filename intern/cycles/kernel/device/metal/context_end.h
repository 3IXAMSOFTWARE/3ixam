
}
; /* end of MetalKernelContext class definition */

/* Silently redirect into the MetalKernelContext instance */
/* NOTE: These macros will need maintaining as entry-points change. */

#undef kernel_integrator_state
#define kernel_integrator_state context.launch_params_metal.integrator_state
