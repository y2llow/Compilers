int* create_pointer(int* x) {
    return x;
}

int main() {
    int value = 42;
    int* ptr = create_pointer(&value);
    return *ptr;
}