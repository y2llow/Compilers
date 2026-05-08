int overwrite_copy(int x) { x = 100; return x; }
int main() { int x = 6; int y = overwrite_copy(x); return x; }
