

#pragma once

struct ID;
struct IDProperty;

extern PyTypeObject BPy_IDPropertyUIManager_Type;

typedef struct BPy_IDPropertyUIManager {
  PyObject_VAR_HEAD
  struct IDProperty *property;
} BPy_IDPropertyUIManager;

void IDPropertyUIData_Init_Types(void);
