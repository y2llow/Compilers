void swap_pointers(int** p1, int** p2) {
    int* temp = *p1;
    *p1 = *p2;
    *p2 = temp;
}

int main() {
    int a = 10;
    int b = 20;
    int* pa = &a;
    int* pb = &b;
    swap_pointers(&pa, &pb);
    return 0;
}