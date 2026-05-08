union Value {
    int i;
    char c;
    float f;
};

int main() {
    union Value v;
    union Value* p;

    v.i = 5;
    v.c = 'A';
    v.f = 3.5;

    p = &v;
    p->i = 12;

    return p->i;
}