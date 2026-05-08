union Value {
    int i;
    char* text;
};

int main() {
    union Value v;

    v.i = "hello";

    return 0;
}