import Vision
import AppKit
import Foundation
import ArgumentParser

/// macOS 原生 OCR 工具 —— 中文图片文字提取
/// 适用场景：当前模型不支持视觉识别时，提取截图/表格/命盘等中文文字
/// 要求：macOS 10.15+，无需额外依赖
/// 用法：swiftc ocr_chinese_image.swift -o ocr_chinese_image && ./ocr_chinese_image image.jpg

@main
struct OcrChineseImage: ParsableCommand {
    @Argument(help: "图片文件路径")
    var imagePath: String
    
    @Option(name: .long, help: "识别语言 (默认 zh-Hans,zh-Hant,en)")
    var lang: String = "zh-Hans,zh-Hant,en"
    
    mutating func run() throws {
        guard FileManager.default.fileExists(atPath: imagePath) else {
            print("文件不存在: \(imagePath)")
            Foundation.exit(1)
        }
        
        guard let image = NSImage(contentsOfFile: imagePath) else {
            print("无法加载图片: \(imagePath)")
            Foundation.exit(1)
        }
        
        guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            print("无法获取 CGImage")
            Foundation.exit(1)
        }
        
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = lang.components(separatedBy: ",")
        request.usesLanguageCorrection = true
        
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        do {
            try handler.perform([request])
            guard let observations = request.results else {
                print("无识别结果")
                Foundation.exit(0)
            }
            
            for observation in observations {
                if let topCandidate = observation.topCandidates(1).first {
                    let text = topCandidate.string.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !text.isEmpty {
                        print(text)
                    }
                }
            }
        } catch {
            print("OCR错误: \(error)")
            Foundation.exit(1)
        }
    }
}
