@echo off
setlocal enabledelayedexpansion

:: 遍历当前目录中的所有 .cif 文件
for %%f in (*.cif) do (
    :: 获取基础文件名
    set "base=%%~nf"
    
    :: 原始代码保持不变
    set cifPath=%%f
    set inpPath=%%~dpnf.inp
    set inputFile=input_%%~nf.txt
    (
        echo !cifPath!
        echo cp2k
        echo !inpPath!
        echo -1
        echo 6
        echo 10
        echo 4
        echo 0
    ) > !inputFile!
    multiwfn.exe < !inputFile!
    del !inputFile!

    :: 重命名操作
    if exist "!inpPath!" (
        ren "!inpPath!" "!base!_AIMD.inp"
        set "newInp=!base!_AIMD.inp"
        
        :: 新增文件修改功能（保留原有修改，仅添加MOTION替换）
        type nul > "!newInp!.tmp"
        set "inMotionBlock=0"
        for /f "tokens=* delims=" %%a in ('type "!newInp!"') do (
            set "line=%%a"
            
            :: 原有修改逻辑保持不变
            if "!line:PRINT_LEVEL LOW=!" neq "!line!" (
                set "line=!line:LOW=MEDIUM!"
            )
            if "!line:#     IGNORE_CONVERGENCE_FAILURE=!" neq "!line!" (
                set "line=!line:#     =!"
            )

            :: 新增MOTION块替换逻辑
            if "!line!"=="&MOTION" (
                set inMotionBlock=1
                >> "!newInp!.tmp" echo ^&MOTION
                >> "!newInp!.tmp" echo   ^&MD
                >> "!newInp!.tmp" echo     ENSEMBLE NVT
                >> "!newInp!.tmp" echo     STEPS 1000
                >> "!newInp!.tmp" echo     TIMESTEP 1.0
                >> "!newInp!.tmp" echo     TEMPERATURE 298.15
                >> "!newInp!.tmp" echo #   COMVEL_TOL 0
                >> "!newInp!.tmp" echo     ^&THERMOSTAT
                >> "!newInp!.tmp" echo       TYPE NOSE
                >> "!newInp!.tmp" echo     ^&END THERMOSTAT
                >> "!newInp!.tmp" echo     ^&PRINT
                >> "!newInp!.tmp" echo       ^&PROGRAM_RUN_INFO
                >> "!newInp!.tmp" echo         ^&EACH
                >> "!newInp!.tmp" echo           MD     1
                >> "!newInp!.tmp" echo         ^&END EACH
                >> "!newInp!.tmp" echo       ^&END PROGRAM_RUN_INFO
                >> "!newInp!.tmp" echo     ^&END PRINT
                >> "!newInp!.tmp" echo   ^&END MD
                >> "!newInp!.tmp" echo   ^&PRINT
                >> "!newInp!.tmp" echo       ^&CELL
                >> "!newInp!.tmp" echo          ^&EACH
                >> "!newInp!.tmp" echo             MD 1
                >> "!newInp!.tmp" echo          ^&END EACH
                >> "!newInp!.tmp" echo       ^&END CELL
                >> "!newInp!.tmp" echo     ^&TRAJECTORY
                >> "!newInp!.tmp" echo       ^&EACH
                >> "!newInp!.tmp" echo         MD   1
                >> "!newInp!.tmp" echo       ^&END EACH
                >> "!newInp!.tmp" echo       FORMAT xyz
                >> "!newInp!.tmp" echo     ^&END TRAJECTORY
                >> "!newInp!.tmp" echo     ^&VELOCITIES
                >> "!newInp!.tmp" echo       ^&EACH
                >> "!newInp!.tmp" echo         MD     1
                >> "!newInp!.tmp" echo       ^&END EACH
                >> "!newInp!.tmp" echo     ^&END VELOCITIES
                >> "!newInp!.tmp" echo     ^&FORCES
                >> "!newInp!.tmp" echo       ^&EACH
                >> "!newInp!.tmp" echo         MD     1
                >> "!newInp!.tmp" echo       ^&END EACH
                >> "!newInp!.tmp" echo     ^&END FORCES
                >> "!newInp!.tmp" echo     ^&RESTART
                >> "!newInp!.tmp" echo       BACKUP_COPIES 1
                >> "!newInp!.tmp" echo       ^&EACH
                >> "!newInp!.tmp" echo         MD  1
                >> "!newInp!.tmp" echo       ^&END EACH
                >> "!newInp!.tmp" echo     ^&END RESTART
                >> "!newInp!.tmp" echo     ^&RESTART_HISTORY OFF
                >> "!newInp!.tmp" echo     ^&END RESTART_HISTORY
                >> "!newInp!.tmp" echo   ^&END PRINT
                >> "!newInp!.tmp" echo ^&END MOTION
            ) else if "!inMotionBlock!"=="1" (
                :: 跳过原始MOTION块内容
                if "!line!"=="&END MOTION" set inMotionBlock=0
            ) else (
                :: 写入其他行
                >> "!newInp!.tmp" echo.!line!
            )
        )
        del "!newInp!"
        ren "!newInp!.tmp" "!newInp!"
        echo 已修改：!newInp!
    )
)

endlocal
pause