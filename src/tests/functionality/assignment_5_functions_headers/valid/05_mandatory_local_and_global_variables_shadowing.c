int value = 5;

int read_global() {
    return value;
}

int main() {
    int value = 2;
    {
        int value = 3;
        value = value + 1;
    }
    return value + read_global();
}
