#pragma once

/** \file
 * \ingroup balembic
 */

#include "abc_reader_object.h"

namespace ixam::io::alembic {

class AbcCameraReader final : public AbcObjectReader {
  Alembic::AbcGeom::ICameraSchema m_schema;

 public:
  AbcCameraReader(const Alembic::Abc::IObject &object, ImportSettings &settings);

  bool valid() const override;
  bool accepts_object_type(const Alembic::AbcCoreAbstract::ObjectHeader &alembic_header,
                           const Object *const ob,
                           const char **err_str) const override;

  void readObjectData(Main *bmain, const Alembic::Abc::ISampleSelector &sample_sel) override;
};

}  // namespace ixam::io::alembic
