int sum_array(int arr[], int size) {
    int total = 0;
    int i = 0;
    while (i < size) {
        total = total + arr[i];
        i = i + 1;
    }
    return total;
}

int main() {
    int nums[3] = {10, 20, 30};
    printf("%d", sum_array(nums, 3));
    return 0;
}