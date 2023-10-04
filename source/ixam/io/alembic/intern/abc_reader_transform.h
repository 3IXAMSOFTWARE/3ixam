#pragma once

/** \file
 * \ingroup balembic
 */

#include "abc_reader_object.h"

#include <Alembic/AbcGeom/All.h>

namespace ixam::io::alembic {

class AbcEmptyReader final : public AbcObjectReader {
  Alembic::AbcGeom::IXformSchema m_schema;

 public:
  AbcEmptyReader(const Alembic::Abc::IObject &object, ImportSettings &settings);

  bool valid() const override;
  bool accepts_object_type(const Alembic::AbcCoreAbstract::ObjectHeader &alembic_header,
                           const Object *const ob,
                           const char **err_str) const override;

  void readObjectData(Main *bmain, const Alembic::Abc::ISampleSelector &sample_sel) override;
};

}  // namespace ixam::io::alembic