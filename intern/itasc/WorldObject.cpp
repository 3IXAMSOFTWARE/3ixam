

/** \file
 * \ingroup intern_itasc
 */

#include "WorldObject.hpp"

namespace iTaSC{

/* special singleton to be used as base for uncontrolled object */
WorldObject Object::world;

WorldObject::WorldObject():UncontrolledObject()
{
	initialize(0,1);
	m_internalPose = Frame::Identity();
}

WorldObject::~WorldObject() 
{
}


}
