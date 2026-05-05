#ifndef DERIVED_H__
#define DERIVED_H__

#include "base.h"

int quadruple(int x) {
    return double_val(double_val(x));
}

#endif