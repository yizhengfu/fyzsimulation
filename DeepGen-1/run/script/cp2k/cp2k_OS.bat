@echo off
setlocal enabledelayedexpansion

:: 遍历当前目录中的所有 .cif 文件
for %%f in (*.cif) do (
    :: 获取基础文件名
    set "base=%%~nf"
    
    :: 原始代码保持不变-1，4，8，X,X,X(K点），1，-3，0
    set cifPath=%%f
    set inpPath=%%~dpnf.inp
    set inputFile=input_%%~nf.txt
    (
        echo !cifPath!
        echo cp2k
        echo !inpPath!
        echo -1
        echo 4
        echo 8
        echo 3,3,3
        echo 1
        echo -3
        echo 0
    ) > !inputFile!
    multiwfn.exe < !inputFile!
    del !inputFile!

    :: 重命名操作
    if exist "!inpPath!" (
        ren "!inpPath!" "!base!_OS.inp"
        set "newInp=!base!_OS.inp"
        
        :: 新增文件修改功能
        type nul > "!newInp!.tmp"
        for /f "tokens=* delims=" %%a in ('type "!newInp!"') do (
            set "line=%%a"
            :: 修改PRINT_LEVEL
            if "!line:PRINT_LEVEL LOW=!" neq "!line!" (
                set "line=!line:LOW=MEDIUM!"
            )
            :: 取消注释收敛设置
            if "!line:#     IGNORE_CONVERGENCE_FAILURE=!" neq "!line!" (
                set "line=!line:#     =!"
            )
            >> "!newInp!.tmp" echo.!line!
        )
        del "!newInp!"
        ren "!newInp!.tmp" "!newInp!"
        echo 已修改：!newInp!
    )
)

endlocal
pause