void add_three(int *p) { *p = *p + 3; return; }
int main() { int x = 5; add_three(&x); return x; }
