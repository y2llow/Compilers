struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    struct Point* ptr = &p;

    ptr->x = 8;
    ptr->y = 5;

    return ptr->x + ptr->y;
}