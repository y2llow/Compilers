struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    p.x = 4;
    p.y = 6;
    return p.x + p.y;
}