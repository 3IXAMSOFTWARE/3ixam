
#ifndef __MANIFOLD_TABLE_H__
#define __MANIFOLD_TABLE_H__

typedef struct {
  int comps;
  int pairs[12][2];
} ManifoldIndices;

extern const ManifoldIndices manifold_table[256];

#endif /* __MANIFOLD_TABLE_H__ */
