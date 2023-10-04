

#pragma once

#include "graph/node.h"

CCL_NAMESPACE_BEGIN

class Progress;
class Scene;

/* A Procedural is a Node which can create other Nodes before rendering starts.
 *
 * The Procedural is supposed to be the owner of any nodes that it creates. It can also create
 * Nodes directly in the Scene (through Scene.create_node), it should still be set as the owner of
 * those Nodes.
 */
class Procedural : public Node, public NodeOwner {
 public:
  NODE_ABSTRACT_DECLARE

  explicit Procedural(const NodeType *type);
  virtual ~Procedural();

  /* Called each time the ProceduralManager is tagged for an update, this function is the entry
   * point for the data generated by this Procedural. */
  virtual void generate(Scene *scene, Progress &progress) = 0;

  /* Create a node and set this Procedural as the owner. */
  template<typename T> T *create_node()
  {
    T *node = new T();
    node->set_owner(this);
    return node;
  }

  /* Delete a Node created and owned by this Procedural. */
  template<typename T> void delete_node(T *node)
  {
    assert(node->get_owner() == this);
    delete node;
  }
};

class ProceduralManager {
  bool need_update_;

 public:
  ProceduralManager();
  ~ProceduralManager();

  void update(Scene *scene, Progress &progress);

  void tag_update();

  bool need_update() const;
};

CCL_NAMESPACE_END