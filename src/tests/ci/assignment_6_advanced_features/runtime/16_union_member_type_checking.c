union Value {
    int i;
    char c;
    float f;
};

int main() {
    union Value v;
    union Value* p;

    v.i = 5;

    p = &v;
    p->i = p->i + 7;

    return p->i;
}