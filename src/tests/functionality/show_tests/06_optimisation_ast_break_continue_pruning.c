int loop_score(int limit) {
    int i = 0;
    int total = 0;

    while (i < limit) {
        int unused_each_round = i * 100;

        if (i == 2) {
            i = i + 1;
            continue;
            total = total + unused_each_round;
            i = i + 50;
        }

        if (i == 5) {
            break;
            total = total + 999;
            i = i + 999;
        }

        total = total + i;
        i = i + 1;
    }

    return total;
}

int main() {
    int result = loop_score(8);
    int unused_after_loop = result * 3;

    if (result > 5) {
        return result;
        result = result + 100;
    }

    return 0;
}