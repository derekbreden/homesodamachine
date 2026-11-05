/* Time one Rust worker to the microsecond: run HSM_WRAP_REAL with this process's arguments,
   wait for it, and write "<user s> <sys s> <max rss bytes>" to HSM_TIME_DIR/<pid>. */
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
    const char *real = getenv("HSM_WRAP_REAL"), *dir = getenv("HSM_TIME_DIR");
    if (!real || !dir) return 127;
    mkdir(dir, 0755);
    pid_t pid = fork();
    if (pid == 0) {
        argv[0] = (char *)real;
        execv(real, argv);
        _exit(127);
    }
    int status = 0;
    struct rusage ru;
    if (wait4(pid, &status, 0, &ru) < 0) return 126;
    char path[4096];
    snprintf(path, sizeof path, "%s/%d", dir, (int)getpid());
    FILE *f = fopen(path, "w");
    if (f) {
        fprintf(f, "%ld.%06d %ld.%06d %ld\n", (long)ru.ru_utime.tv_sec, (int)ru.ru_utime.tv_usec,
                (long)ru.ru_stime.tv_sec, (int)ru.ru_stime.tv_usec, (long)ru.ru_maxrss);
        fclose(f);
    }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}
