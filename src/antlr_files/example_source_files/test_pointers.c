int main() {
    int x = 5;
    int* ptr = &x;
    *ptr = 10;
    int y = *ptr;

    x++;
    ++x;

    int a = (int)3;
    char b = (char)65;

    return y;
}