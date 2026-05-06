void process(int x) {
    // expects scalar int
}

int main() {
    int arr[5] = {1, 2, 3, 4, 5};
    process(arr);  // Cannot pass array to scalar parameter
    return 0;
}