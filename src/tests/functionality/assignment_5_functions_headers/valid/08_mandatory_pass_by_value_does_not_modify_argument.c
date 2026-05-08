int change_copy(int x) {
    x = 99;
    return x;
}

int main() {
    int x = 6;
    int y = change_copy(x);
    return x;
}
