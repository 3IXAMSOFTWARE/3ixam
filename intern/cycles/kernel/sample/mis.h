

#pragma once

CCL_NAMESPACE_BEGIN

/* Multiple importance sampling utilities. */

ccl_device float balance_heuristic(float a, float b)
{
  return (a) / (a + b);
}

ccl_device float balance_heuristic_3(float a, float b, float c)
{
  return (a) / (a + b + c);
}

ccl_device float power_heuristic(float a, float b)
{
  return (a * a) / (a * a + b * b);
}

ccl_device float power_heuristic_3(float a, float b, float c)
{
  return (a * a) / (a * a + b * b + c * c);
}

ccl_device float max_heuristic(float a, float b)
{
  return (a > b) ? 1.0f : 0.0f;
}

CCL_NAMESPACE_END