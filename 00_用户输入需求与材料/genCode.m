

function genCode(app)
% 自动设置路径、编译模型并打包代码文件
% 使用 Simulink.fileGenControl 管理编译文件夹

% ==================== 可配置参数 ====================
BACK_LEVELS = 1;  % 回溯级数：1表示回溯一级，2表示回溯两级
% ===================================================

% 获取当前模型信息
currentModel = bdroot;
if strcmp(currentModel, '')
    error('没有打开的Simulink模型');
end

fprintf('开始处理模型: %s\n', currentModel);

% 步骤1: 基于模型文件路径确定项目根目录
modelFullPath = get_param(currentModel, 'FileName');
if isempty(modelFullPath)
    error('无法确定模型文件位置');
end
fprintf('模型文件位置: %s\n', modelFullPath);

modelPath = fileparts(modelFullPath);
projectRoot = modelPath;
for i = 1:BACK_LEVELS
    projectRoot = fileparts(projectRoot);
    if isempty(projectRoot)
        error('回溯级数过多，已到达根目录');
    end
end
fprintf('项目根目录: %s\n', projectRoot);

% 步骤2: 定义并创建代码和缓存目录
codeDir = fullfile(projectRoot, '20-Code');
cacheDir = fullfile(projectRoot, '21-Cache');

if ~exist(codeDir, 'dir')
    mkdir(codeDir);
    fprintf('创建代码目录: %s\n', codeDir);
else
    fprintf('使用现有代码目录: %s\n', codeDir);
end

if ~exist(cacheDir, 'dir')
    mkdir(cacheDir);
    fprintf('创建缓存目录: %s\n', cacheDir);
else
    fprintf('使用现有缓存目录: %s\n', cacheDir);
end


% 步骤2.5: 清空文件夹所有目录和文件，只保留Code下的代码压缩包
fprintf('开始清空文件夹（只保留Code下的压缩包）...\n');

% 清空Code文件夹（保留.zip文件）
if exist(codeDir, 'dir')
    codeItems = dir(codeDir);
    for i = 1:length(codeItems)
        item = codeItems(i);
        if any(strcmp(item.name, {'.', '..'})) || strcmpi(item.name(end-3:end), '.zip')
            continue;
        end
        itemPath = fullfile(codeDir, item.name);
        if item.isdir
            rmdir(itemPath, 's');
        else
            delete(itemPath);
        end
    end
end

% 清空Cache文件夹（删除所有内容）
if exist(cacheDir, 'dir')
    rmdir(cacheDir, 's');
    mkdir(cacheDir);
end

fprintf('文件夹清空完成\n');



% 步骤3: 使用 Simulink.fileGenControl 统一设置编译过程文件夹:cite[2]
% 获取当前的文件夹生成配置
cfg = Simulink.fileGenControl('getConfig');
% 设置新的代码生成文件夹和缓存文件夹
cfg.CodeGenFolder = codeDir;       % 设置代码生成根文件夹:cite[1]:cite[2]
cfg.CacheFolder = cacheDir;        % 设置仿真缓存根文件夹:cite[1]:cite[2]
% 设置文件夹结构为“特定于模型”(ModelSpecific)，这是默认且常用的结构:cite[2]
cfg.CodeGenFolderStructure = Simulink.filegen.CodeGenFolderStructure.ModelSpecific;
% 应用配置，并创建目录（如果不存在）:cite[2]
Simulink.fileGenControl('setConfig', 'config', cfg, 'createDir', true);
fprintf('已使用 Simulink.fileGenControl 统一设置代码生成文件夹: %s\n', codeDir);
fprintf('已使用 Simulink.fileGenControl 统一设置仿真缓存文件夹: %s\n', cacheDir);
% 注意：通过 Simulink.fileGenControl 设置后，编译过程生成的文件将自动放置在指定根目录下相应的子结构中:cite[1]:cite[2]




% 步骤4: 编译生成代码
fprintf('开始编译模型: %s\n', currentModel);
save_system(currentModel); % 保存模型

originalDir = pwd; % 保存当前工作目录
cd(codeDir);   % 切换到项目根目录

try
    % 使用 rtwbuild 生成代码
    % 由于已通过 Simulink.fileGenControl 设置，代码将生成在指定目录
    rtwbuild(currentModel);
    fprintf('代码生成成功完成\n');
catch ME
    fprintf('代码生成失败: %s\n', ME.message);
    cd(originalDir); % 确保发生错误时也能切换回原目录
    rethrow(ME);
end
cd(originalDir); % 切换回原始工作目录

% 步骤5: 检查生成的代码文件
fprintf('检查生成的代码文件...\n');
% 注意：由于使用了 Simulink.fileGenControl，代码文件位于指定的 codeDir 下，但其内部结构由系统目标文件等决定:cite[1]:cite[6]
targetFolder = fullfile(codeDir, [currentModel, '_grt_rtw']); % 例如，使用 grt.tlc 时常见的输出文件夹
if exist(targetFolder, 'dir')
    fprintf('主要代码生成文件夹: %s\n', targetFolder);
else
    % 如果默认的 _grt_rtw 文件夹不存在，列出 codeDir 下的内容
    fprintf('未找到默认 _grt_rtw 文件夹，检查根目录下的结构:\n');
    dirContents = dir(codeDir);
    for i = 1:length(dirContents)
        if dirContents(i).isdir && ~strcmp(dirContents(i).name, '.') && ~strcmp(dirContents(i).name, '..')
            fprintf('  发现目录: %s\n', fullfile(codeDir, dirContents(i).name));
        end
    end
    targetFolder = codeDir; % 将目标文件夹设置为代码根目录进行后续查找
end

fileTypes = {'*.c', '*.h', '*.a2l'};
fileCounts = zeros(1, length(fileTypes));
for i = 1:length(fileTypes)
    files = dir(fullfile(targetFolder, fileTypes{i}));
    fileCounts(i) = length(files);
    if ~isempty(files)
        fprintf('在 %s 中找到 %d 个 %s 文件\n', targetFolder, length(files), fileTypes{i});
        for j = 1:min(3, length(files))
            fprintf('  - %s\n', files(j).name);
        end
        if length(files) > 3
            fprintf('  - ... 和其他 %d 个文件\n', length(files) - 3);
        end
    end
end

% 检查 slprj 目录（模型引用或共享 utilities 可能在此）:cite[1]
slprjDir = fullfile(codeDir, 'slprj');
if exist(slprjDir, 'dir')
    slprjCFiles = dir(fullfile(slprjDir, '**/*.c'));
    slprjHFiles = dir(fullfile(slprjDir, '**/*.h'));
    fprintf('在 slprj 中找到 %d 个.c文件和 %d 个.h文件\n', length(slprjCFiles), length(slprjHFiles));
end

if sum(fileCounts) == 0
    warning('在代码目录中未找到任何.c或.h文件。请检查模型配置和代码生成设置。');
end

% 步骤6: 打包生成的代码文件
fprintf('开始打包代码文件...\n');
try
    info = Simulink.MDLInfo(currentModel);
    if isempty(info.ModelVersion) || strcmp(info.ModelVersion, '1.0')
        versionStr = '1.0';
    else
        versionStr = info.ModelVersion;
    end
catch
    versionStr = '1.0';
end

timestamp = datestr(now, 'yyyymmdd_HHMMSS');
zipFileName = [currentModel, '_APP_V', versionStr, '_', timestamp];

% 收集要压缩的文件 (递归查找 codeDir 下的所有 .c, .h, .a2l 文件)
allFiles = {};
for i = 1:length(fileTypes)
    foundFiles = dir(fullfile(codeDir, '**', fileTypes{i})); % 在 codeDir 及其子目录中递归查找
    for j = 1:length(foundFiles)
        if ~foundFiles(j).isdir
            allFiles{end+1} = fullfile(foundFiles(j).folder, foundFiles(j).name);
        end
    end
end

if isempty(allFiles)
    warning('在代码目录及其子目录中未找到任何.c、.h或.a2l文件可供压缩。');
else
    fprintf('找到 %d 个文件进行压缩\n', length(allFiles));
    for i = 1:min(5, length(allFiles))
        [~, name, ext] = fileparts(allFiles{i});
        fprintf('  %s%s\n', name, ext);
    end
    if length(allFiles) > 5
        fprintf('  ... 和其他 %d 个文件\n', length(allFiles) - 5);
    end

    zipPath = fullfile(codeDir, zipFileName);
    zip(zipPath, allFiles);
    fprintf('压缩包创建成功: %s.zip\n', zipFileName);
    zipFileInfo = dir([zipPath, '.zip']);
    if ~isempty(zipFileInfo)
        fileSizeMB = zipFileInfo.bytes / (1024 * 1024);
        fprintf('压缩包大小: %.2f MB\n', fileSizeMB);
    end
end

fprintf('代码生成和打包完成！\n');
fprintf('压缩包位置: %s.zip\n', fullfile(codeDir, zipFileName));

% 步骤7: (可选) 重置文件生成控制参数到 Simulink 预设值:cite[2]
% Simulink.fileGenControl('reset');
% fprintf('已重置文件生成控制参数到默认设置。\n');
end