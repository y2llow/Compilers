int value = 100;
int shared = 7;

int transform(int value, int extra) {
    int result = value + extra;

    {
        int value = result * 2;
        int local_only = value - shared;

        if (local_only > 20) {
            int shared = local_only;
            result = shared + value;
        } else {
            int fallback = shared + extra;
            result = fallback;
        }
    }

    return result;
}

int main() {
    int value = 3;
    int first = transform(value, shared);

    {
        int shared = 10;
        int second = transform(shared, value);
        first = first + second;
    }

    return first;
}