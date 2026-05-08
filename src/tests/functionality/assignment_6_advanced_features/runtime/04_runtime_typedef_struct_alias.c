struct Point {
    int x;
    int y;
};

typedef struct Point Point;

int main() {
    Point p;
    p.x = 9;
    p.y = 2;
    return p.x + p.y;
}