#include <stdio.h>

struct Point {
    int x;
    int y;
};

typedef int Point;

int main() {
    struct Point p;
    p.x = 10;

    p.z = 5;

    return 0;
}