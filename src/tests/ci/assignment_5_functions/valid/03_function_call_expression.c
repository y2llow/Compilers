int get() {
    return 5;
}

int add(int a, int b) {
    return a + b;
}

int main() {
    int x = add(get(), 3);
    return 0;
}