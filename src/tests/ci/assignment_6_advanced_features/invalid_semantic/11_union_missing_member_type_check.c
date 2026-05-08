union Value {
    int i;
    char c;
};

int main() {
    union Value v;

    v.missing = 5;

    return 0;
}