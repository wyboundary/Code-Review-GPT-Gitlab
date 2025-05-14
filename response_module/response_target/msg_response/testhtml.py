import markdown

def convert_markdown_to_html():
   
    markdown_text = """
# 总结
本次变更主要涉及Rokt环境配置和二分查找演示功能，新增了基于UserDefaults的环境切换逻辑和硬编码数组的二分查找实现，未修改现有接口和核心逻辑。
# 文件变更
| 文件 | 修改摘要 |
|---------|-------------|
| `RoktDemo/Resources/AppDelegate.swift` | 新增Rokt环境配置开关和二分查找演示功能 |

---
## 修改文件列表 <details><summary>📚<strong><code>RoktDemo/Resources/AppDelegate.swift</code></strong></summary>        <div>(752 tokens) AI review 意见如下:</div> 
#### 😀代码评分：75
#### ✅代码优点：
1. 使用了UserDefaults来存储环境配置，便于管理和切换环境
2. 使用了三元运算符简化条件判断
3. 实现了二分查找算法，提高了查找效率
#### 🤔问题点：
1. 硬编码了数组`[4,5,6]`，缺乏灵活性
2. 二分查找函数`binarySearch`未在代码中定义，可能导致编译错误
3. 环境切换逻辑没有错误处理机制
4. 打印语句使用中文，不符合国际化规范
5. 代码缩进不一致，影响可读性
#### 🎯修改建议：
1. 将硬编码数组改为参数传入
2. 确保`binarySearch`函数已正确定义
3. 添加环境切换的错误处理
4. 使用英文日志输出
5. 统一代码缩进风格
#### 💻修改后的代码：
```swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // Environment setup
    do {
        let useStage = UserDefaults.standard.bool(forKey: Constants.UserDefaults.useStageEnvironment)
        try Rokt.setEnvironment(environment: useStage ? .stage : .production)
    } catch {
        print("Failed to set environment: \(error)")
    }
    
    // Binary search example
    let sortedArray = [4, 5, 6]
    if let index = binarySearch(sortedArray, target: 5) {
        print("Found at index \(index)")
    } else {
        print("Not found")
    }
    
    return true
}
``` 
"""
    try:
        message_html = markdown.markdown(
                                            markdown_text,
                                            extensions=[
                                                'extra',         
                                                'tables',    
                                                'fenced_code',           
                                                'sane_lists',
                                                'toc'
                                            ]
                                        )
        print("转换成功！HTML输出：")
        print(message_html)
    except Exception as e:
        print(f"转换失败，错误信息: {e}")

if __name__ == "__main__":
    convert_markdown_to_html()