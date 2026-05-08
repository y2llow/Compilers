int add(int x, int y) {
    return x + y;
}

int add(int x, int y, int z) {
    return x + y + z;
}

int main() {
    int a = add(1, 2);
    int b = add(1, 2, 3);
    return a + b;
}