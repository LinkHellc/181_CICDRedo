% 定义文件对话框的过滤器，以便只显示文本文件
[file, path] = uigetfile({'*.a2l'}, 'Select the input file');
 
% 检查用户是否取消了选择
if isequal(file, 0) || isequal(path, 0)
    disp('User selected Cancel');
    return; % 退出函数
end
 
% 构建完整的文件名
fullFileName = fullfile(path, file);

% 读取文件内容
fileID = fopen(fullFileName, 'r', 'n', 'UTF-8'); % 打开文件，指定编码（如果适用）
fileContents = fread(fileID, '*char')'; % 读取为字符数组
fclose(fileID);
 
% 定义要删除的代码段的起始和结束标记
startMarker = '/begin IF_DATA XCP';
endMarker = '/end IF_DATA';
 
% 初始化索引变量和结果字符串
currentIndex = 1;
result = '';
 
% 循环处理所有匹配项
while currentIndex <= length(fileContents)
    % 查找起始标记的位置
    startIndex = strfind(fileContents(currentIndex:end), startMarker);
    if isempty(startIndex)
        % 如果没有找到起始标记，则将剩余内容添加到结果中
        result = [result, fileContents(currentIndex:end)];
        break;
    else
        startIndex = currentIndex + startIndex(1) - 1; % 转换为全局索引
        
        % 添加起始标记之前的内容到结果中
        result = [result, fileContents(currentIndex:startIndex-1)];
        
        % 查找结束标记的位置
        endIndexSearch = strfind(fileContents(startIndex + length(startMarker):end), endMarker);
        if isempty(endIndexSearch)
            % 如果没有找到结束标记，则发出警告并停止处理（或根据需要处理）
            warning('在起始标记 %s 后未找到结束标记 %s', startMarker, endMarker);
            break;
        else
            endIndex = startIndex + length(startMarker) + endIndexSearch(1) - 1; % 计算实际的 endIndex
            
            % 更新 currentIndex 以跳过已处理的内容
            currentIndex = endIndex + length(endMarker);
        end
    end
end
 
% 将修改后的内容写回文件
fileID = fopen(fullFileName, 'w', 'n', 'UTF-8'); % 打开文件以写入，指定编码（如果适用）
fwrite(fileID, result, 'char');
fclose(fileID);
 
disp('处理完成，结果已保存');