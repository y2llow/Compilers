struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    struct Point* ptr = &p;

    ptr->x = 5;
    ptr->y = 6;

    return ptr->x + ptr->y;
}