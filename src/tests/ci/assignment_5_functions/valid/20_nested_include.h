#ifndef NESTED_H__
#define NESTED_H__

int clamp(int val, int lo, int hi) {
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}

#endif