#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

int main() {
    // 指定的目录路径
    std::string path = "E:\\video_picture_material";

    // 检查目录是否存在
    if (!fs::exists(path) || !fs::is_directory(path)) {
        std::cerr << "Error: Specified path does not exist or is not a directory." << std::endl;
        return 1;
    }

    try {
        // 遍历目录
        for (const auto& entry : fs::directory_iterator(path)) {
            if (entry.is_directory()) {  // 确保是目录
                std::cout << entry.path().filename() << std::endl;  // 输出目录名，不带引号
            }
        }
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
