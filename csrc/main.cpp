#include <iostream>
#include <memory>
#include <chrono>

#include "detector.h"
#include "utils.h"


std::vector<std::string> LoadLabels(const std::string& path) {
  // load class names
  std::vector<std::string> class_names;
  std::ifstream infile(path);
  if (infile.is_open()) {
    std::string line;
    while (getline (infile,line)) {
      class_names.emplace_back(line);
    }
    infile.close();
  }
  else {
    std::cerr << "Error loading the class names!\n";
  }

  return class_names;
}


void Demo(
    cv::Mat& img,
    const std::vector<std::tuple<cv::Rect, float, int>>& data_vec,
    const std::vector<std::string>& class_names,
    bool label = true) {
  for (const auto & data : data_vec) {
    cv::Rect box;
    float score;
    int class_idx;
    std::tie(box, score, class_idx) = data;

    cv::rectangle(img, box, cv::Scalar(0, 0, 255), 2);

    if (label) {
      std::stringstream ss;
      ss << std::fixed << std::setprecision(2) << score;
      std::string s = class_names[class_idx] + " " + ss.str();

      auto font_face = cv::FONT_HERSHEY_DUPLEX;
      auto font_scale = 1.0;
      int thickness = 1;
      int baseline=0;
      auto s_size = cv::getTextSize(s, font_face, font_scale, thickness, &baseline);
      cv::rectangle(img,
          cv::Point(box.tl().x, box.tl().y - s_size.height - 5),
          cv::Point(box.tl().x + s_size.width, box.tl().y),
          cv::Scalar(0, 0, 255), -1);
      cv::putText(img, s, cv::Point(box.tl().x, box.tl().y - 5),
            font_face, font_scale, cv::Scalar(255, 255, 255), thickness);
    }
  }

  cv::namedWindow("Result", cv::WINDOW_AUTOSIZE);
  cv::imshow("Result", img);
  cv::waitKey(0);
}


int main(int argc, const char* argv[]) {
  if (argc != 4) {
    std::cerr << "usage: app <path-to-exported-script-module> "
                 "<path-to-label> <path-to-image>" << std::endl;
    return -1;
  }

  // set device type - CPU/GPU
  torch::DeviceType device_type;
  if (torch::cuda::is_available()) {
    device_type = torch::kCUDA;
  }else{
    device_type = torch::kCPU;
  }

  // load class names from dataset for visualization
  std::vector<std::string> class_names = LoadLabels(argv[2]);
  if (class_names.empty()) {
    return -1;
  }

  // load input image
  cv::Mat img = cv::imread(argv[3]);
  if (img.empty()) {
    std::cerr << "Error loading the image!" << std::endl;
    return -1;
  }

  // load network
  auto detector = Detector(argv[1], device_type);

  // inference
  auto result = detector.Run(img, kConfThreshold, kIouThreshold);

  // visualize detections
  Demo(img, result, class_names);
}
