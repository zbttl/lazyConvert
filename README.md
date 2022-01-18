# 视频批量一键转换
新脚本在实现了上一个一键限制视频到对应体积功能的基础上，增加了以下功能：

1. 通过修改参数使编解码均使用硬解，默认使用支持最为广泛 qsv 硬解（intel 家的硬解标准）。
2. 对子目录中的视频文件同样进行转换。
3. 默认的封装格式为 mp4，可更改。
4. 同时对帧数进行了更改。
5. 转换时对修改/无需进行修改的文件均进行备份，多次运行时无需不会对已转换的项目进行多次转换。
