#Shanbay-Alfred2-Workflow

扇贝网的单词查询workflow，用于Alfred2


### 要求

此workflow需要本地python安装 [requests](http://docs.python-requests.org/en/latest/) 这个模块

	pip install requests[security]

### 安装
下载`Shanbay_Alfred2_Workflow.alfredworkflow`文件

双击文件导入即可。

如果要用添加到词库功能，需要修改文件配置，继续操作如下：

双击右侧的`sb`那个方块（`Script Filter`）,点击窗口内的`Open workflow folder`打开文件夹

修改`config.py`内的`username`和`pw`为你自己的扇贝网账号密码，保存即可。

### 使用
调出Alfred2，输入`sb love`
等待查询结果出现

如果要添加当前单词到词库，直接敲回车

如果要查看单词页面
按住`command`敲回车

### 其它
历史提交记录已清除（涉及到账号密码）

感谢 [iLeoDo](https://github.com/iLeoDo) 童鞋的更新。
