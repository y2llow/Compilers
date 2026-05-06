#include <stdio.h>

struct Point {
    int x;
    int y;
};

void move(struct Point* p, int dx, int dy) {
    p->x = p->x + dx;
    p->y = p->y + dy;
}

int main() {
    struct Point p;
    p.x = 0;
    p.y = 0;
    move(&p, 3, 4);
    printf("%d\n", p.x);
    return 0;
}