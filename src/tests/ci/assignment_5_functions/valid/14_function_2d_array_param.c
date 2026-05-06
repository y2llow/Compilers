int sum_matrix(int matrix[2][3]) {
    int total = 0;
    int i = 0;
    while (i < 2) {
        int j = 0;
        while (j < 3) {
            total = total + matrix[i][j];
            j = j + 1;
        }
        i = i + 1;
    }
    return total;
}

int main() {
    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
    return sum_matrix(m);
}