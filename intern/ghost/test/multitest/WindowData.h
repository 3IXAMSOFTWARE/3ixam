

typedef void (*WindowDataHandler)(void *priv, GHOST_EventHandle evt);
typedef struct _WindowData WindowData;

/***/

WindowData *windowdata_new(void *data, WindowDataHandler handler);
void windowdata_handle(WindowData *wb, GHOST_EventHandle evt);
void windowdata_free(WindowData *wb);
