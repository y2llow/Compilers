void increment(int* ptr) {
    *ptr = *ptr + 1;
}

int main() {
    int x = 5;
    increment(&x);
    printf("%d", x);
    return 0;
}