int add(int x, int y) {
    return x + y;
}

int add(int x, int y, int z) {
    return x + y + z;
}

float add(float a, float b) {
    return a + b;
}

int main() {
    int   r1 = add(1, 2);
    int   r2 = add(1, 2, 3);
    float r3 = add(1.5, 2.5);
    return r1 + r2 + r3;
}