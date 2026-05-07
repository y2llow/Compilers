#include <stdio.h>

struct Point {
    int x;
    int y;
};

struct Rectangle {
    int width;
    int height;
};

int main() {
    struct Point p;
    p.x = 10;
    p.y = 20;

    struct Rectangle r;
    r.width = 100;
    r.height = 50;

    int area;
    area = r.width * r.height;

    printf("%d\n", p.x);
    printf("%d\n", area);

    return 0;
}