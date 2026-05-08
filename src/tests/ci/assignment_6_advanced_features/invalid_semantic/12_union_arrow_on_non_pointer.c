union Value {
    int i;
    char c;
};

int main() {
    union Value v;

    v->i = 5;

    return 0;
}