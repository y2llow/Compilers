int get(int* p) {
    return *p;
}

float get(float* p) {
    return *p;
}

int main() {
    int   x = 42;
    float y = 3.14;
    int   r1 = get(&x);
    float r2 = get(&y);
    return r1;
}