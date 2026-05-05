#ifndef CONSTANTS_H__
#define CONSTANTS_H__

#define MAX_VAL 100
#define MIN_VAL 0

int in_range(int x) {
    return x >= MIN_VAL && x <= MAX_VAL;
}

#endif