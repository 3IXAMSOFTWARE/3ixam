

#ifndef __GENERIC_HEAP_H__
#define __GENERIC_HEAP_H__

/** \file generic_heap.h
 *  \ingroup curve_fit
 */

struct Heap;
struct HeapNode;
typedef struct Heap Heap;
typedef struct HeapNode HeapNode;

typedef void (*HeapFreeFP)(void *ptr);

Heap        *HEAP_new(unsigned int tot_reserve);
bool         HEAP_is_empty(const Heap *heap);
void         HEAP_free(Heap *heap, HeapFreeFP ptrfreefp);
void        *HEAP_node_ptr(HeapNode *node);
void         HEAP_remove(Heap *heap, HeapNode *node);
HeapNode    *HEAP_insert(Heap *heap, double value, void *ptr);
void         HEAP_insert_or_update(Heap *heap, HeapNode **node_p, double value, void *ptr);
void        *HEAP_popmin(Heap *heap);
void         HEAP_clear(Heap *heap, HeapFreeFP ptrfreefp);
unsigned int HEAP_size(const Heap *heap);
HeapNode    *HEAP_top(Heap *heap);
double       HEAP_top_value(const Heap *heap);
void         HEAP_node_value_update(Heap *heap, HeapNode *node, double value);
void         HEAP_node_value_update_ptr(Heap *heap, HeapNode *node, double value, void *ptr);
double       HEAP_node_value(const HeapNode *node);

#endif  /* __GENERIC_HEAP_IMPL_H__ */
