int main() {
    int matrix[2][3];
    matrix[0][0] = 1;
    matrix[0][1] = 2;
    matrix[1][2] = matrix[0][0] + matrix[0][1];
    return matrix[1][2];
}
