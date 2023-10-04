
#pragma once

#include "usd_writer_mesh.h"

namespace ixam::io::usd {

class USDMetaballWriter : public USDGenericMeshWriter {
 public:
  USDMetaballWriter(const USDExporterContext &ctx);

 protected:
  virtual Mesh *get_export_mesh(Object *object_eval, bool &r_needsfree) override;
  virtual void free_export_mesh(Mesh *mesh) override;
  virtual bool is_supported(const HierarchyContext *context) const override;
  virtual bool check_is_animated(const HierarchyContext &context) const override;

 private:
  bool is_basis_ball(Scene *scene, Object *ob) const;
};

}  // namespace ixam::io::usd