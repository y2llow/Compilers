int main() {
    int arr[5] = {10, 20, 30, 40, 50};

    int* p = &arr[1];
    int* q = &arr[3];

    int a = *(p + 1);   // 30
    int b = *(q - 1);   // 30
    int d = q - p;      // 2

    p++;
    q--;

    return a + b + d + *p + *q; // 30 + 30 + 2 + 30 + 30 = 122
}