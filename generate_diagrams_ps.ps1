# generate_diagrams_ps.ps1
# Generates all report diagram PNG images using System.Drawing (GDI+)
# Run: powershell -ExecutionPolicy Bypass -File generate_diagrams_ps.ps1

Add-Type -AssemblyName System.Drawing

$OUT = Join-Path $PSScriptRoot "report_images"
if (-not (Test-Path $OUT)) { New-Item -ItemType Directory -Path $OUT | Out-Null }

function HC($hex) {
    $hex = $hex.TrimStart('#')
    [System.Drawing.Color]::FromArgb(
        [Convert]::ToInt32($hex.Substring(0,2),16),
        [Convert]::ToInt32($hex.Substring(2,2),16),
        [Convert]::ToInt32($hex.Substring(4,2),16))
}

$BLUE   = HC "4f8ef7"; $GREEN  = HC "22c55e"; $AMBER  = HC "f59e0b"
$RED    = HC "ef4444"; $PURPLE = HC "8b5cf6"; $TEAL   = HC "14b8a6"
$ORANGE = HC "f97316"; $PINK   = HC "ec4899"; $DARK   = HC "1a1a2e"
$LIGHT  = HC "f8f9fb"; $MUTED  = HC "888888"; $WHITE  = HC "ffffff"
$BORDER = HC "e5e7eb"

function SaveBmp($bmp, $name) {
    $path = Join-Path $OUT $name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "  saved: $path"
}

function NewBmp($w, $h) {
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g   = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode    = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear($LIGHT)
    return $bmp, $g
}

function DrawTitle($g, $text, $w, $yPos=18) {
    $fnt = New-Object System.Drawing.Font("Segoe UI", 15, [System.Drawing.FontStyle]::Bold)
    $br  = New-Object System.Drawing.SolidBrush($DARK)
    $fmt = New-Object System.Drawing.StringFormat
    $fmt.Alignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($text, $fnt, $br, [float]($w/2), [float]$yPos, $fmt)
    $fnt.Dispose(); $br.Dispose()
}

function DrawBox($g, $x, $y, $w, $h, $label, $color, $fs=10) {
    $pen  = New-Object System.Drawing.Pen($color, 2)
    $fill = [System.Drawing.Color]::FromArgb(35, $color.R, $color.G, $color.B)
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($fill)), [float]$x,[float]$y,[float]$w,[float]$h)
    $g.DrawRectangle($pen, [float]$x,[float]$y,[float]$w,[float]$h)
    $fnt  = New-Object System.Drawing.Font("Segoe UI", $fs, [System.Drawing.FontStyle]::Bold)
    $br   = New-Object System.Drawing.SolidBrush($color)
    $rect = New-Object System.Drawing.RectangleF([float]$x,[float]$y,[float]$w,[float]$h)
    $fmt  = New-Object System.Drawing.StringFormat
    $fmt.Alignment     = [System.Drawing.StringAlignment]::Center
    $fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($label, $fnt, $br, $rect, $fmt)
    $pen.Dispose(); $fnt.Dispose(); $br.Dispose()
}

function DrawArrow($g, $x1, $y1, $x2, $y2) {
    $pen = New-Object System.Drawing.Pen($MUTED, 1.5)
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
    $g.DrawLine($pen,[float]$x1,[float]$y1,[float]$x2,[float]$y2)
    $pen.Dispose()
}

function DrawText($g, $text, $x, $y, $fs=10, $bold=$false, $color=$null, $align="Left") {
    if ($color -eq $null) { $color = $DARK }
    $style = if ($bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
    $fnt   = New-Object System.Drawing.Font("Segoe UI", $fs, $style)
    $br    = New-Object System.Drawing.SolidBrush($color)
    $fmt   = New-Object System.Drawing.StringFormat
    switch ($align) {
        "Center" { $fmt.Alignment = [System.Drawing.StringAlignment]::Center }
        "Right"  { $fmt.Alignment = [System.Drawing.StringAlignment]::Far }
        default  { $fmt.Alignment = [System.Drawing.StringAlignment]::Near }
    }
    $g.DrawString($text, $fnt, $br, [float]$x, [float]$y, $fmt)
    $fnt.Dispose(); $br.Dispose()
}

function DrawBar($g, $x, $y, $w, $h, $color) {
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($color)), [float]$x,[float]$y,[float]$w,[float]$h)
}

# ===================================================================
# 1. ARCHITECTURE DIAGRAM
# ===================================================================
Write-Host "Generating 01_architecture.png..."
$bmp, $g = NewBmp 1300 500
DrawTitle $g "Project Architecture -- Employee Analytics Dashboard" 1300

$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(18,$TEAL.R,$TEAL.G,$TEAL.B))), 0,58,1300,105)
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(18,$BLUE.R,$BLUE.G,$BLUE.B))), 0,183,1300,145)
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(18,$PURPLE.R,$PURPLE.G,$PURPLE.B))), 0,348,1300,125)

DrawText $g "DATA LAYER"     15  98   8 $true $TEAL
DrawText $g "BACKEND LAYER"  15 235   8 $true $BLUE
DrawText $g "FRONTEND LAYER" 15 395   8 $true $PURPLE

DrawBox $g 200 68  280 85 "Employees_raw_Data.csv  (Raw CSV Dataset)" $TEAL 9
DrawBox $g  80 193 240 105 "data_loader.py  Load+Clean+Engineer" $BLUE 9
DrawBox $g 340 193 240 105 "analysis.py  KPIs+Aggregations+Stats" $GREEN 9
DrawBox $g 600 193 240 105 "predictions.py  Ridge+RF+Attrition" $AMBER 9
DrawBox $g 860 193 240 105 "chart_builder.py  8 Chart Types" $ORANGE 9

DrawBox $g 80 358 1140 92 "app.py -- Streamlit Dashboard (12 Pages): Overview | Quality | Dept | City | Salary | Performance | Remote | Tenure | Correlations | Explorer | Predictions | Chart Builder" $PURPLE 9

DrawArrow $g 340 153 200 193
DrawArrow $g 320 245 340 245
$penL = New-Object System.Drawing.Pen($MUTED,1.5)
$g.DrawLine($penL, [float]200, [float]298, [float]200, [float]358)
$g.DrawLine($penL, [float]460, [float]298, [float]460, [float]358)
$g.DrawLine($penL, [float]720, [float]298, [float]720, [float]358)
$g.DrawLine($penL, [float]980, [float]298, [float]980, [float]358)
$penL.Dispose()

SaveBmp $bmp "01_architecture.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 2. DATA PIPELINE
# ===================================================================
Write-Host "Generating 02_data_pipeline.png..."
$bmp, $g = NewBmp 1400 210
DrawTitle $g "Data Pipeline -- Raw CSV to Analysis-Ready DataFrame" 1400

$stepLabels = @("Raw CSV Load","Normalise Columns","Parse join_date","Fix remote_work","Impute Missing","Derive Features","Analysis Ready")
$stepColors = @($TEAL,$BLUE,$BLUE,$AMBER,$ORANGE,$GREEN,$GREEN)
$bw=152; $bh=80; $gap=18; $sx=30; $sy=65
for ($i=0; $i -lt $stepLabels.Count; $i++) {
    $x=$sx+$i*($bw+$gap)
    DrawBox $g $x $sy $bw $bh $stepLabels[$i] $stepColors[$i] 9
    if ($i -lt ($stepLabels.Count-1)) { DrawArrow $g ($x+$bw+2) ($sy+$bh/2) ($x+$bw+$gap-2) ($sy+$bh/2) }
}
DrawText $g "salary/age/rating -> dept median imputation" ($sx+4*($bw+$gap)+10) 155 8 $false $MUTED
DrawText $g "tenure_years, age_group, salary_band derived" ($sx+5*($bw+$gap)+5)  155 8 $false $MUTED

SaveBmp $bmp "02_data_pipeline.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 3. KPI CARDS OVERVIEW
# ===================================================================
Write-Host "Generating 03_overview_kpi.png..."
$bmp, $g = NewBmp 1300 310
$g.FillRectangle((New-Object System.Drawing.SolidBrush($DARK)), 0,0,1300,50)
DrawText $g "Overview Page -- 10 KPI Metric Cards" 650 13 13 $true $WHITE "Center"

$kpis = @(
    @{label="Total Employees"; val="150";      color=$BLUE},
    @{label="Avg Salary";      val="Rs 58,420"; color=$GREEN},
    @{label="Avg Performance"; val="3.45 / 5"; color=$AMBER},
    @{label="Remote Workers";  val="38.7%";    color=$PURPLE},
    @{label="Avg Tenure";      val="5.2 yrs";  color=$RED},
    @{label="Departments";     val="5";        color=$TEAL},
    @{label="Cities";          val="5";        color=$GREEN},
    @{label="Total Spend";     val="Rs 87.6L"; color=$ORANGE},
    @{label="Median Salary";   val="Rs 55,450";color=$BLUE},
    @{label="Avg Age";         val="41.2 yrs"; color=$PINK}
)

for ($i=0; $i -lt $kpis.Count; $i++) {
    $row = [Math]::Floor($i/5); $col = $i % 5
    $cx = 22 + $col*256; $cy = 58 + $row*112
    $cw=244; $ch=100; $cc=$kpis[$i].color
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($WHITE)), [float]$cx,[float]$cy,[float]$cw,[float]$ch)
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($cc)),    [float]$cx,[float]$cy,[float]7,[float]$ch)
    $penB = New-Object System.Drawing.Pen($BORDER,1); $g.DrawRectangle($penB,[float]$cx,[float]$cy,[float]$cw,[float]$ch); $penB.Dispose()
    $fv = New-Object System.Drawing.Font("Segoe UI",15,[System.Drawing.FontStyle]::Bold)
    $bv = New-Object System.Drawing.SolidBrush($DARK)
    $fmt = New-Object System.Drawing.StringFormat; $fmt.Alignment=[System.Drawing.StringAlignment]::Center
    $g.DrawString($kpis[$i].val, $fv, $bv, [float]($cx+$cw/2), [float]($cy+20), $fmt)
    $fv.Dispose(); $bv.Dispose()
    $fl = New-Object System.Drawing.Font("Segoe UI",8); $bl = New-Object System.Drawing.SolidBrush($MUTED)
    $g.DrawString($kpis[$i].label, $fl, $bl, [float]($cx+$cw/2), [float]($cy+62), $fmt)
    $fl.Dispose(); $bl.Dispose()
}

SaveBmp $bmp "03_overview_kpi.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 4. DEPARTMENT CHARTS
# ===================================================================
Write-Host "Generating 04_dept_charts.png..."
$bmp, $g = NewBmp 1300 420
$g.Clear($LIGHT)
DrawTitle $g "Department Analysis -- Headcount & Average Salary" 1300

$depts  = @("Engineering","Sales","HR","Marketing","Finance")
$counts = @(42,38,24,27,19)
$sals   = @(68420,55800,62100,63900,61200)
$dc     = @($BLUE,$GREEN,$AMBER,$ORANGE,$TEAL)
$maxC=52; $maxS=82000; $cH=280; $cY=75; $bW=80; $bG=40

DrawText $g "Headcount by Department" 80 50 11 $true $DARK
for ($i=0; $i -lt $depts.Count; $i++) {
    $bh=[int]($counts[$i]/$maxC*$cH); $bx=60+$i*($bW+$bG); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $dc[$i]
    DrawText $g "$($counts[$i])" ($bx+$bW/2) ($by-22) 10 $true $dc[$i] "Center"
    DrawText $g $depts[$i] ($bx+$bW/2) ($cY+$cH+8) 8 $false $DARK "Center"
}

DrawText $g "Avg Salary by Department" 720 50 11 $true $DARK
for ($i=0; $i -lt $depts.Count; $i++) {
    $bh=[int]($sals[$i]/$maxS*$cH); $bx=660+$i*($bW+$bG); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $dc[$i]
    DrawText $g "Rs $([int]($sals[$i]/1000))k" ($bx+$bW/2) ($by-22) 9 $true $dc[$i] "Center"
    DrawText $g $depts[$i] ($bx+$bW/2) ($cY+$cH+8) 8 $false $DARK "Center"
}

SaveBmp $bmp "04_dept_charts.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 5. PERFORMANCE CHART
# ===================================================================
Write-Host "Generating 05_performance_chart.png..."
$bmp, $g = NewBmp 1300 420
$g.Clear($LIGHT)
DrawTitle $g "Performance Analysis -- Rating Distribution & Avg by Department" 1300

$ratings = @(12,18,45,52,23)
$rlabels = @("1-Poor","2-Below","3-Average","4-Good","5-Excellent")
$rcolors = @($RED,$ORANGE,$AMBER,[System.Drawing.Color]::FromArgb(134,239,172),$GREEN)
$maxR=60; $cH=280; $cY=75; $bW=80; $bG=50

DrawText $g "Performance Rating Distribution" 80 50 11 $true $DARK
for ($i=0; $i -lt $ratings.Count; $i++) {
    $bh=[int]($ratings[$i]/$maxR*$cH); $bx=60+$i*($bW+$bG); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $rcolors[$i]
    DrawText $g "$($ratings[$i])" ($bx+$bW/2) ($by-22) 11 $true $rcolors[$i] "Center"
    DrawText $g $rlabels[$i] ($bx+$bW/2) ($cY+$cH+8) 9 $false $DARK "Center"
}

$depts  = @("Engineering","Sales","HR","Marketing","Finance")
$avgs   = @(3.8,3.5,3.6,3.9,3.4)
$dc2    = @($BLUE,$GREEN,$AMBER,$ORANGE,$TEAL)
DrawText $g "Avg Performance Rating by Department" 720 50 11 $true $DARK
for ($i=0; $i -lt $depts.Count; $i++) {
    $bh=[int]($avgs[$i]/5.0*$cH); $bx=660+$i*($bW+40); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $dc2[$i]
    DrawText $g "$($avgs[$i])" ($bx+$bW/2) ($by-22) 10 $true $dc2[$i] "Center"
    DrawText $g $depts[$i] ($bx+$bW/2) ($cY+$cH+8) 8 $false $DARK "Center"
}

SaveBmp $bmp "05_performance_chart.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 6. ML PIPELINE FLOWCHART
# ===================================================================
Write-Host "Generating 06_ml_flowchart.png..."
$bmp, $g = NewBmp 1300 480
$g.Clear($LIGHT)
DrawTitle $g "ML Models Pipeline Flowchart -- 3 Models" 1300 15

DrawBox $g 30 170 180 100 "Cleaned DataFrame" $TEAL 10
DrawArrow $g 210 220 280 220
DrawBox $g 280 160 220 120 "ColumnTransformer StandardScaler + OneHotEncoder" $BLUE 9

DrawArrow $g 500 200 580 105
DrawArrow $g 500 220 580 225
DrawArrow $g 500 240 580 345

DrawBox $g 580  62 200 90 "Model 1: Ridge Regression Salary Prediction" $GREEN 9
DrawArrow $g 780 107 870 107
DrawBox $g 870  62 200 90 "Output: Predicted Salary + Feature Importance" $GREEN 9

DrawBox $g 580 177 200 90 "Model 2: Random Forest Performance (1-5)" $AMBER 9
DrawArrow $g 780 222 870 222
DrawBox $g 870 177 200 90 "Output: Rating 1-5 + Probabilities Chart" $AMBER 9

DrawBox $g 580 302 200 90 "Model 3: Business Rules Attrition Risk Score" $RED 9
DrawArrow $g 780 347 870 347
DrawBox $g 870 302 200 90 "Output: Risk Score 0-100 High/Medium/Low" $RED 9

DrawBox $g 280 410 720 55 "5-Fold Cross-Validation | MAE / R2 / Accuracy | @st.cache_resource" $PURPLE 8

SaveBmp $bmp "06_ml_flowchart.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 7. ATTRITION RISK TABLE
# ===================================================================
Write-Host "Generating 07_attrition_table.png..."
$bmp, $g = NewBmp 1300 370
$g.Clear($LIGHT)
DrawTitle $g "Attrition Risk Table -- Employees Sorted by Risk Score" 1300 15

$headers = @("Employee","Department","City","Salary","Age","Tenure","Rating","Remote","Score","Risk Level")
$rows    = @(
    @("Employee_14","Sales",      "Delhi",    "Rs 53,979","35","5.9 yr","1","Yes","65","HIGH RISK"),
    @("Employee_34","Finance",    "Chennai",  "Rs 37,540","58","6.4 yr","1","No", "62","HIGH RISK"),
    @("Employee_5", "Sales",      "Chennai",  "Rs 23,547","43","6.8 yr","4","Yes","50","MEDIUM"),
    @("Employee_54","Finance",    "Delhi",    "Rs 24,862","22","5.8 yr","4","No", "45","MEDIUM"),
    @("Employee_31","Marketing",  "Mumbai",   "Rs 1,657", "59","6.3 yr","5","Yes","45","MEDIUM"),
    @("Employee_1", "Engineering","Pune",     "Rs 60,820","51","6.9 yr","4","No", "10","LOW RISK"),
    @("Employee_18","Engineering","Delhi",    "Rs 67,290","30","5.8 yr","5","Yes","5", "LOW RISK")
)
$colW=@(115,105,90,90,45,65,55,58,55,100)
$sx=12; $rH=36; $hY=45; $dY=83

$hx=$sx
for ($c=0; $c -lt $headers.Count; $c++) {
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($DARK)),[float]$hx,[float]$hY,[float]$colW[$c],[float]$rH)
    DrawText $g $headers[$c] ($hx+4) ($hY+10) 8 $true $WHITE; $hx+=$colW[$c]+2
}
for ($r=0; $r -lt $rows.Count; $r++) {
    $ry=$dY+$r*($rH+2)
    $rc=if ($rows[$r][9] -like "*HIGH*") { [System.Drawing.Color]::FromArgb(255,252,213,213) }
        elseif ($rows[$r][9] -like "*MEDIUM*") { [System.Drawing.Color]::FromArgb(255,255,249,196) }
        else { [System.Drawing.Color]::FromArgb(255,209,250,229) }
    $rx=$sx
    for ($c=0; $c -lt $rows[$r].Count; $c++) {
        $g.FillRectangle((New-Object System.Drawing.SolidBrush($rc)),[float]$rx,[float]$ry,[float]$colW[$c],[float]$rH)
        $pb=New-Object System.Drawing.Pen($BORDER,1); $g.DrawRectangle($pb,[float]$rx,[float]$ry,[float]$colW[$c],[float]$rH); $pb.Dispose()
        $tc=if ($rows[$r][9] -like "*HIGH*" -and $c -eq $rows[$r].Count-1) { $RED }
            elseif ($rows[$r][9] -like "*MEDIUM*" -and $c -eq $rows[$r].Count-1) { $AMBER }
            elseif ($rows[$r][9] -like "*LOW*" -and $c -eq $rows[$r].Count-1) { $GREEN }
            else { $DARK }
        DrawText $g $rows[$r][$c] ($rx+3) ($ry+9) 8 ($c -eq $rows[$r].Count-1) $tc
        $rx+=$colW[$c]+2
    }
}

SaveBmp $bmp "07_attrition_table.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 8. CHART BUILDER MOCKUP
# ===================================================================
Write-Host "Generating 08_chart_builder.png..."
$bmp, $g = NewBmp 1300 500
$g.Clear($LIGHT)
$g.FillRectangle((New-Object System.Drawing.SolidBrush($DARK)),0,0,1300,50)
DrawText $g "Chart Builder -- Configuration Panel + Generated Chart Output" 650 13 12 $true $WHITE "Center"

$g.FillRectangle((New-Object System.Drawing.SolidBrush($WHITE)),20,58,420,430)
$pb=New-Object System.Drawing.Pen($BORDER,1.5); $g.DrawRectangle($pb,20,58,420,430); $pb.Dispose()
DrawText $g "Chart Configuration Panel" 230 65 11 $true $DARK "Center"

$ctrls=@(
    @{label="Chart Type";       val="Bar";          color=$BLUE},
    @{label="X-Axis/Category";  val="department";   color=$GREEN},
    @{label="Y-Axis/Value";     val="salary";       color=$AMBER},
    @{label="Colour Group";     val="city";         color=$PURPLE},
    @{label="Aggregation";      val="Mean";         color=$TEAL},
    @{label="Colour Palette";   val="Pastel";       color=$ORANGE},
    @{label="Chart Height";     val="450 px";       color=$PINK},
    @{label="Show Labels";      val="Yes";          color=$GREEN}
)
for ($i=0; $i -lt $ctrls.Count; $i++) {
    $cy2=92+$i*44; $cc=$ctrls[$i].color
    $g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(22,$cc.R,$cc.G,$cc.B))),30,[float]$cy2,400,38)
    $pb2=New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(70,$cc.R,$cc.G,$cc.B),1); $g.DrawRectangle($pb2,30,[float]$cy2,400,38); $pb2.Dispose()
    DrawText $g $ctrls[$i].label 40 ($cy2+10) 9 $false $MUTED
    DrawText $g $ctrls[$i].val 410 ($cy2+10) 10 $true $cc "Right"
}
$g.FillRectangle((New-Object System.Drawing.SolidBrush($BLUE)),30,460,400,20)
DrawText $g "Generate Chart" 230 462 10 $true $WHITE "Center"

# Chart output
DrawText $g "Generated Chart: Mean Salary by Department" 760 60 11 $true $DARK "Center"
$depts2=@("Engineering","Sales","HR","Marketing","Finance")
$sals2=@(68420,55800,62100,63900,61200)
$dc2=@($BLUE,$GREEN,$AMBER,$ORANGE,$TEAL)
$maxS=82000; $cH=300; $cY=80; $bW=100; $bG=55
for ($i=0; $i -lt $depts2.Count; $i++) {
    $bh=[int]($sals2[$i]/$maxS*$cH); $bx=480+$i*($bW+$bG); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $dc2[$i]
    DrawText $g "Rs $([int]($sals2[$i]/1000))k" ($bx+$bW/2) ($by-22) 9 $true $dc2[$i] "Center"
    DrawText $g $depts2[$i] ($bx+$bW/2) ($cY+$cH+10) 8 $false $DARK "Center"
}

SaveBmp $bmp "08_chart_builder.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 9. SALARY HISTOGRAM + BOX
# ===================================================================
Write-Host "Generating 09_salary_analysis.png..."
$bmp, $g = NewBmp 1300 420
$g.Clear($LIGHT)
DrawTitle $g "Salary Analysis -- Distribution Histogram + Box Plot by Department" 1300

$bins=@(4,6,10,16,22,28,24,20,14,10,7,5,3)
$maxBin=30; $cH=280; $cY=75; $bW=60; $bG=8
DrawText $g "Salary Distribution Histogram" 80 50 11 $true $DARK
for ($i=0; $i -lt $bins.Count; $i++) {
    $bh=[int]($bins[$i]/$maxBin*$cH); $bx=55+$i*($bW+$bG); $by=$cY+$cH-$bh
    DrawBar $g $bx $by $bW $bh $BLUE
}
DrawText $g "Low -->" 60 ($cY+$cH+8) 8 $false $MUTED
DrawText $g "<-- High" 620 ($cY+$cH+8) 8 $false $MUTED
DrawText $g "Salary Range (Rs)" 340 ($cY+$cH+8) 9 $true $DARK "Center"

DrawText $g "Box Plot by Department" 800 50 11 $true $DARK
$depts3=@("Engineering","Sales","HR","Marketing","Finance")
$dc3=@($BLUE,$GREEN,$AMBER,$ORANGE,$TEAL)
$meds=@(200,160,185,175,170); $q1s=@(140,95,130,110,105); $q3s=@(265,225,245,235,240)
$scale=1.0; $bpX=730; $bpW=80; $bpG=45
for ($i=0; $i -lt $depts3.Count; $i++) {
    $bx5=$bpX+$i*($bpW+$bpG)
    $q1y=$cY+$cH-[int]($q3s[$i]*$scale); $q3y=$cY+$cH-[int]($q1s[$i]*$scale); $medy=$cY+$cH-[int]($meds[$i]*$scale)
    $g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,$dc3[$i].R,$dc3[$i].G,$dc3[$i].B))),[float]$bx5,[float]$q1y,[float]$bpW,[float]($q3y-$q1y))
    $pb=New-Object System.Drawing.Pen($dc3[$i],2); $g.DrawRectangle($pb,[float]$bx5,[float]$q1y,[float]$bpW,[float]($q3y-$q1y)); $pb.Dispose()
    $pm=New-Object System.Drawing.Pen($DARK,2.5); $g.DrawLine($pm,[float]$bx5,[float]$medy,[float]($bx5+$bpW),[float]$medy); $pm.Dispose()
    $pw=New-Object System.Drawing.Pen($dc3[$i],1.5)
    $g.DrawLine($pw,[float]($bx5+$bpW/2),[float]($q1y-35),[float]($bx5+$bpW/2),[float]$q1y)
    $g.DrawLine($pw,[float]($bx5+$bpW/2),[float]$q3y,[float]($bx5+$bpW/2),[float]($q3y+35))
    $pw.Dispose()
    DrawText $g $depts3[$i] ($bx5+$bpW/2) ($cY+$cH+10) 8 $false $DARK "Center"
}

SaveBmp $bmp "09_salary_analysis.png"; $g.Dispose(); $bmp.Dispose()

# ===================================================================
# 10. REMOTE WORK
# ===================================================================
Write-Host "Generating 10_remote_work.png..."
$bmp, $g = NewBmp 1300 400
$g.Clear($LIGHT)
DrawTitle $g "Remote Work Analysis -- Split, By Department, By City" 1300

$cH=280; $cY=75
DrawText $g "Remote vs On-Site" 110 50 11 $true $DARK
$g.FillRectangle((New-Object System.Drawing.SolidBrush($PURPLE)),40,$cY,170,[int](0.387*$cH))
$g.FillRectangle((New-Object System.Drawing.SolidBrush($BLUE)),40,($cY+[int](0.387*$cH)),170,[int](0.613*$cH))
DrawText $g "Remote" 70 ($cY+20) 10 $true $WHITE
DrawText $g "58 (38.7%)" 55 ($cY+40) 9 $false $WHITE
DrawText $g "On-Site" 70 ($cY+[int](0.387*$cH)+20) 10 $true $WHITE
DrawText $g "92 (61.3%)" 55 ($cY+[int](0.387*$cH)+40) 9 $false $WHITE

$depts4=@("Engineering","Sales","HR","Marketing","Finance")
$rpct=@(42.9,36.8,33.3,37.0,26.3)
$dc4=@($BLUE,$GREEN,$AMBER,$ORANGE,$TEAL)
DrawText $g "Remote Pct by Department" 400 50 11 $true $DARK
for ($i=0; $i -lt $depts4.Count; $i++) {
    $bh=[int]($rpct[$i]/55*$cH); $bx=260+$i*120; $by=$cY+$cH-$bh
    DrawBar $g $bx $by 80 $bh $dc4[$i]
    DrawText $g "$($rpct[$i])%" ($bx+40) ($by-22) 9 $true $dc4[$i] "Center"
    DrawText $g $depts4[$i] ($bx+40) ($cY+$cH+8) 8 $false $DARK "Center"
}

$cities=@("Pune","Bangalore","Delhi","Mumbai","Chennai")
$cpct=@(43.8,39.3,36.8,31.0,30.4)
$dc5=@($TEAL,$GREEN,$BLUE,$ORANGE,$PURPLE)
DrawText $g "Remote Pct by City" 920 50 11 $true $DARK
for ($i=0; $i -lt $cities.Count; $i++) {
    $bh=[int]($cpct[$i]/55*$cH); $bx=860+$i*84; $by=$cY+$cH-$bh
    DrawBar $g $bx $by 70 $bh $dc5[$i]
    DrawText $g "$($cpct[$i])%" ($bx+35) ($by-22) 9 $true $dc5[$i] "Center"
    DrawText $g $cities[$i] ($bx+35) ($cY+$cH+8) 8 $false $DARK "Center"
}

SaveBmp $bmp "10_remote_work.png"; $g.Dispose(); $bmp.Dispose()

Write-Host "`nDone. All images in: $OUT"
