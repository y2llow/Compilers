void modify(int* x) {
    *x = 10;
}

int main() {
    const int value = 5;
    modify(&value);  // passing const int*, expects int*
    return 0;
}