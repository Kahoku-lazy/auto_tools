#include <iostream>
#include <filesystem>
#include <string>

namespace fs = std::filesystem;

int main() {

    // 获取目录路径
    std::string path = "E:\\video_picture_material\\Non\\repetition";

    // 检查目录是否存在
    if (!fs::exists(path) || !fs::is_directory(path)) {
        std::cerr << "Error: Directory does not exist." << std::endl;
        return 1;
    }

    try {
        // 遍历指定目录
        for (const auto& entry : fs::directory_iterator(path)) {
            const auto& p = entry.path();
            if (p.extension() == ".jpg" || p.extension() == ".png" || p.extension() == ".jpeg") {
                std::string filename = p.filename().string();
                
                // 查找并替换"uncleaned"为"repeat"
                size_t pos = filename.find("uncleaned");
                if (pos != std::string::npos) {
                    std::string new_filename = filename.replace(pos, std::string("uncleaned").length(), "repeat");
                    fs::rename(p, p.parent_path() / new_filename);
                    std::cout << "Renamed " << filename << " to " << new_filename << std::endl;
                }
            }
        }
    } catch (const fs::filesystem_error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
