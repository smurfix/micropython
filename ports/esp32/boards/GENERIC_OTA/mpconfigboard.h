#define MICROPY_HW_BOARD_NAME "4MB/OTA module"
#define MICROPY_HW_MCU_NAME "ESP32"

#undef MICROPY_VFS_FAT
#define MICROPY_VFS_FAT (0)

#undef mp_type_fileio
#define mp_type_fileio                      mp_type_vfs_lfs2_fileio
#undef mp_type_textio
#define mp_type_textio                      mp_type_vfs_lfs2_textio

