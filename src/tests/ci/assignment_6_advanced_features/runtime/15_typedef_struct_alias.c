struct Point {
    int x;
    int y;
};

typedef struct Point Point;

int main() {
    Point p;

    p.x = 6;
    p.y = 7;

    return p.x + p.y;
}