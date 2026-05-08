int main() {
    int arr[5] = {10, 20, 30, 40, 50};

    int* p = &arr[1];
    int* q = &arr[3];

    int a = *(p + 1);
    int b = *(q - 1);
    int d = q - p;

    p++;
    q--;

    return a + b + d + *p + *q;
}
