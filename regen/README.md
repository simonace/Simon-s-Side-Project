# Regen Project

Regen是Register Generator的缩写。该项目旨在通过读取固定格式的描述APB上寄存器的Excel表格来自动产生Verilog的regfile文件供IP设计者使用，
以及进一步生成.h文件以供验证和应用使用。后期可能会考虑自动生成一定格式寄存器列表供Datasheet中使用。

Regen也是德语中代表“雨”的单词。这正好反映了最近上海烦人的连续的雨天。也正好对应了作者近来郁闷的心情，喜欢的女生有了新欢，这种挫败感和失恋也差不了太多了。

## 文件列表
  - ___README.md___      说明文件(markdown)
  - ___regen_template.xlsx___      描述寄存器的Excel表格
  - ___regen.py___     Python程序
