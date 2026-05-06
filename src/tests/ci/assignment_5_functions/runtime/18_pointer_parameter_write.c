void set_to_9(int* p) {
    *p = 9;
    return;
}

int main() {
    int x = 1;
    set_to_9(&x);
    return x;
}