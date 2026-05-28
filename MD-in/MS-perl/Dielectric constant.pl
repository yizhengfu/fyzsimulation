################################################################################
#!perl                                                                         #
#                                                                              #
# DIELECTRIC CONSTANT (EQUILIBRIUM)                                            #
#                                                                              #
# Author: Reinier Akkermans (Accelrys)                                         #
# Version: 1.0                                                                 #
# Tested on: Materials Studio 5.5                                              #
# Required modules: Materials Visualizer (and Forcite Plus for dynamics)       #
#                                                                              #
# This script calculates the dielectric constant from the fluctuations in the  #
# total dipole moment,     脚本原理：从总偶极矩的波动中计算介电常数。              #
#                                                                              #
#             <M^2> - <M>^2                                                    #
# eps = 1 + ----------------                                                   #
#           3 k <T> <V> eps0                                                   #
#                                                                              #
#  eps:  dielectric constant                                                   #
#  M:    total dipole moment                                                   #
#  V:    volume of the box                                                     #
#  T:    temperature                                                           #
#  eps0: vacuum permittivity                                                   #
#  k:    Boltzmann constant                                                    #
#  其中k、V、T、eps0均为常数值，可直接设定或通过轨迹文件中读取                      #
#  This equation assumes Ewald summation with conducting boundary conditions   #
#  这个方程假定 Ewald 求和带有导电边界条件                                        #
################################################################################
use strict;
use MaterialsScript qw(:all);

use constant SPEED_OF_LIGHT => 299792458; # m/s
use constant ELEMENTARY_CHARGE => 1.602176565E-19; # C
use constant ANGSTROM => 1E-10; # m
use constant EA => ELEMENTARY_CHARGE*ANGSTROM; # C*m
use constant DEBYE => 1E-21/SPEED_OF_LIGHT; # C*m
use constant PI => 3.14159265358979323846264338327950288419716939937510;
use constant MAGNETIC_CONSTANT => 4*PI*1E-7; # s^2*V/C/m
use constant VACUUM_PERMITTIVITY => 1/MAGNETIC_CONSTANT/SPEED_OF_LIGHT/SPEED_OF_LIGHT; # C/V/m
use constant BOLTZMANN => 1.3806488E-23; # J/K

# column indices for the results
use constant { DIPOLE => 0, PROBABILITY => 1, NORMAL => 2};
use constant { TIME => 0, DIPOLE_X => 1, DIPOLE_Y => 2, DIPOLE_Z => 3};
use constant { RESULT => 0, VALUE => 1, UNIT => 2};

{
################################################################################
#  BEGIN USER INPUT                                                            #
################################################################################

# the trajectory to be analysed
my $doc = $Documents{"01.xtd"};

# script settings
my $settings = Settings(
	NumBins => 20 # the number of bins in the histogram
);
################################################################################
#  END USER  INPUT                                                             #
################################################################################

Run($doc,$settings);
}
printf "Time taken: %d seconds", time()-$^T;

################################################################################
sub Run
{
	my ($doc,$settings) = @_;
	
	# create a hash of the settings array for easy access
	my %settings = Array2Hash($settings);

	# output study table 输出表格文件
	my $std = Documents->New($doc->Name . ".std");
	ClearStudyTable($std);
	
	my $histogramSheet = $std->ActiveSheet;
	$histogramSheet->Title = "Histogram";
	$histogramSheet->ColumnHeading(DIPOLE) = "total dipole (D)";
	$histogramSheet->ColumnHeading(PROBABILITY) = "probability (1/D)";
	$histogramSheet->ColumnHeading(2) = "normal distribution (1/D)";
		
	my $dataSheet = $std->InsertSheet;
	$dataSheet->DeleteRow(0);	
	$dataSheet->Title = "Data";
	$dataSheet->ColumnHeading(TIME) = "time (ps)";
	$dataSheet->ColumnHeading(DIPOLE_X) = "total X dipole (D)";
	$dataSheet->ColumnHeading(DIPOLE_Y) = "total Y dipole (D)";
	$dataSheet->ColumnHeading(DIPOLE_Z) = "total Z dipole (D)";

	my $resultsSheet = $std->InsertSheet;
	$resultsSheet->DeleteRow(0);	
	$resultsSheet->Title = "Results";
	$resultsSheet->ColumnHeading(RESULT) = "result";
	$resultsSheet->ColumnHeading(VALUE) = "value";
	$resultsSheet->ColumnHeading(UNIT) = "unit";
	
	# the molecules 聚合物
	my $molecules = $doc->UnitCell->Molecules;
	my $numMolecules = $molecules->Count;
	die "no molecule objects found" if $numMolecules == 0 ;
	
	# the trajectory 轨迹文件
	my $trajectory = $doc->Trajectory;
	my $numFrames = $trajectory->NumFrames;
	
	# the average totale dipole vector 平均总偶极子矢量，初始设为零
	my $averageDipoleX = 0;
	my $averageDipoleY = 0;
	my $averageDipoleZ = 0;
	
	# the average totale dipole squared 总偶极子的平均值的平方，初始设为零
	my $averageDipoleXSquare = 0;
	my $averageDipoleYSquare = 0;
	my $averageDipoleZSquare = 0;
	
	# average temperature in the trajectory 轨迹文件平均温度，初始设为零
	my $temperature = 0;
	
	# average volume in the trajectory 轨迹文件平均体积，初始设为零
	my $volume = 0;
	my $lattice3D = $doc->Lattice3D;
	
	# run over all frames 运行所有帧文件
	for (my $i = 0; $i < $numFrames; $i++)
	{
		# set the current frame
		$trajectory->CurrentFrame = $i+1;
		
		# read of the temperature and volume from the document 输出文件中的温度和体积
		$temperature += $doc->Temperature; # K
		$volume += $lattice3D->CellVolume;# A^3
		
		# calculate the total dipole moment vector 计算文件里的总偶极子矢量
	 	my $totalDipoleMoment = TotalDipoleMoment($molecules); # D 单位，德拜
		my $totalDipoleX = $totalDipoleMoment->X;
		my $totalDipoleY = $totalDipoleMoment->Y;
		my $totalDipoleZ = $totalDipoleMoment->Z;
		
		# store the vector components in the study table 储存总偶极子矢量值
		$dataSheet->InsertRow if $i >= $dataSheet->RowCount;
		$dataSheet->Cell($i,TIME) = $trajectory->FrameTime;
		$dataSheet->Cell($i,DIPOLE_X) = $totalDipoleX;
		$dataSheet->Cell($i,DIPOLE_Y) = $totalDipoleY;
		$dataSheet->Cell($i,DIPOLE_Z) = $totalDipoleZ;
		
		# update the averages 更新原偶极子矢量值，证明偶极矩发生变化
		$averageDipoleX += $totalDipoleX;
		$averageDipoleY += $totalDipoleY;
		$averageDipoleZ += $totalDipoleZ;
	
		$averageDipoleXSquare += $totalDipoleX*$totalDipoleX;
		$averageDipoleYSquare += $totalDipoleY*$totalDipoleY;
		$averageDipoleZSquare += $totalDipoleZ*$totalDipoleZ;
	}
	
	# normalize 更新后的值
	$temperature /= $numFrames;
	$volume /= $numFrames;
	$averageDipoleX /= $numFrames;
	$averageDipoleY /= $numFrames;
	$averageDipoleZ /= $numFrames;
	$averageDipoleXSquare /= $numFrames;
	$averageDipoleYSquare /= $numFrames;
	$averageDipoleZSquare /= $numFrames;
	
	# determine the variances 确定差值，公式中的<M^2> - <M>^2 部分
	my $dipoleXVariance =  $averageDipoleXSquare - $averageDipoleX*$averageDipoleX;
	my $dipoleYVariance =  $averageDipoleYSquare - $averageDipoleY*$averageDipoleY;
	my $dipoleZVariance =  $averageDipoleZSquare - $averageDipoleZ*$averageDipoleZ;
	
	# the average mean and variance 平均值和方差
	my $mean = ($averageDipoleX+$averageDipoleY+$averageDipoleZ)/3;
	my $variance = ($dipoleXVariance+$dipoleYVariance+$dipoleZVariance)/3;
	
	# add the results to the study table 输出结果到表格中
	AddResult($resultsSheet,"Number of samples",$numFrames);
	AddResult($resultsSheet,"Number of molecules",$numMolecules);
	AddResult($resultsSheet,"Temperature",$temperature,"K");
	AddResult($resultsSheet,"Volume",$volume,"A^3");
	AddResult($resultsSheet,"Dipole mean X", $averageDipoleX,"D");
	AddResult($resultsSheet,"Dipole mean Y", $averageDipoleY,"D");
	AddResult($resultsSheet,"Dipole mean Z", $averageDipoleZ,"D");
	AddResult($resultsSheet,"Dipole deviation XX", sqrt($dipoleXVariance),"D");
	AddResult($resultsSheet,"Dipole deviation YY", sqrt($dipoleYVariance),"D");
	AddResult($resultsSheet,"Dipole deviation ZZ", sqrt($dipoleZVariance),"D");
	
	# some data to check convergence 输出各单位值
	CreateHistogram($histogramSheet,$dataSheet,$settings{NumBins});
	AddNormalDistribution($histogramSheet,$mean,$variance);
	
	# convert everything to SI units
	$volume *= ANGSTROM*ANGSTROM*ANGSTROM; # m^3
	$variance *= DEBYE*DEBYE; # C*m
	
	#             <M^2> - <M>^2        var(M_x)     1  
	# eps = 1 + ---------------- = 1 + -------- * ------
	#           3 k <T> <V> eps0       <T> <V>    k eps0   
	
	my $dielectricConstant = $variance/$volume/$temperature; # (C*m)^2/m^3/K = C^2/m/K
	$dielectricConstant /= VACUUM_PERMITTIVITY*BOLTZMANN; # dimensionless
	$dielectricConstant += 1; # conducting boundary conditions
	
	AddResult($resultsSheet,"Dielectric constant", $dielectricConstant);
}

sub TotalDipoleMoment
{
	my ($molecules) = @_;
	
	my $dX = 0;
	my $dY = 0;
	my $dZ = 0;
	foreach my $molecule (@$molecules)
	{
		my $dipoleMoment = $molecule->DipoleMoment; # e*A
		$dX += $dipoleMoment->X;
		$dY += $dipoleMoment->Y;
		$dZ += $dipoleMoment->Z;
	}
	# convert from e*A to D
	$dX *= EA/DEBYE;
	$dY *= EA/DEBYE;
	$dZ *= EA/DEBYE;

	return Point(X => $dX, Y => $dY, Z => $dZ);
}

sub CreateHistogram
{
	my($histogramSheet,$dataSheet,$numBins) = @_;
	
	# the number of data points
	my $numData = $dataSheet->RowCount;
	
	# first determine the range
	my $maxValue = $dataSheet->Cell(0,DIPOLE_X);
	my $minValue = $maxValue;
	for(my $row = 0; $row < $numData; $row++)
	{
		my $value = $dataSheet->Cell($row,DIPOLE_X);
		$maxValue = $value if $value > $maxValue;
		$minValue = $value if $value < $minValue;
		my $value = $dataSheet->Cell($row,DIPOLE_Y);
		$maxValue = $value if $value > $maxValue;
		$minValue = $value if $value < $minValue;
		my $value = $dataSheet->Cell($row,DIPOLE_Z);
		$maxValue = $value if $value > $maxValue;
		$minValue = $value if $value < $minValue;	
	}
			
	# store the histogram in a Perl array initialized to zero 存储数据到初始化为零的 Perl 数组中
	my @array;
	for(my $bin = 0; $bin < $numBins; $bin++)
	{
		$array[$bin] = 0;
	}

	my $range = $maxValue-$minValue;
	my $binWidth = $range/($numBins-1);
	for(my $row = 0; $row < $numData; $row++)
	{
		my $value = $dataSheet->Cell($row,DIPOLE_X);
		my $bin = int(($value-$minValue)/$binWidth); # [0,$numBins[
		die "out of range" if $bin < 0 || $bin >= $numBins;
		$array[$bin]++;
		my $value = $dataSheet->Cell($row,DIPOLE_Y);
		my $bin = int(($value-$minValue)/$binWidth); # [0,$numBins[
		die "out of range" if $bin < 0 || $bin >= $numBins;
		$array[$bin]++;
		my $value = $dataSheet->Cell($row,DIPOLE_Z);
		my $bin = int(($value-$minValue)/$binWidth); # [0,$numBins[
		die "out of range" if $bin < 0 || $bin >= $numBins;
		$array[$bin]++;		
	}
	
	my $normalization = $numData*3*$binWidth;
	for(my $row = 0; $row < $numBins; $row++)
	{
		$histogramSheet->InsertRow if $row >= $histogramSheet->RowCount;
		$histogramSheet->Cell($row,DIPOLE) = ($row+0.5)*$binWidth+$minValue;
		$histogramSheet->Cell($row,PROBABILITY) = $array[$row]/$normalization;
	}
}

sub AddNormalDistribution
{
	my($histogramSheet,$mean,$variance) = @_;
	
	my $var2 = $variance*2;
	for(my $row = 0; $row < $histogramSheet->RowCount; $row++)
	{
		my $value = $histogramSheet->Cell($row,DIPOLE);
		my $diff = $value-$mean;
		$histogramSheet->Cell($row,NORMAL) = exp(-$diff*$diff/$var2)/sqrt(PI*$var2);
	}	
}

################################################################################
#  creates a hash from an array with key-value elements                        #
################################################################################
sub Array2Hash
{
	# make hash
	my ($settings) = @_;
	my @array = @$settings;
	my %hash;
	for(my $i = 0; $i < scalar(@array); $i +=2)
	{
		my $key = $array[$i];
		my $value = $array[$i+1];
		$hash{$key} = $value;
	}
	return %hash;
}

################################################################################
#  clear studytable from empty rows                                            #
################################################################################
sub ClearStudyTable
{
	my($std) = @_;
	
	# delete the rows and columns of the active sheet
	do
	{
		$std->DeleteRow(0);
	}
	while($std->RowCount > 0);
	
	do
	{
		$std->DeleteColumn(0);
	}
	while($std->ColumnCount > 1);	# need at least one column
}

sub AddResult
{
	my ($sheet,$result, $value, $unit) = @_;
	my $row = $sheet->InsertRow;
	$sheet->Cell($row,RESULT) = $result;
	$sheet->Cell($row,VALUE) = $value;
	$sheet->Cell($row,UNIT) = $unit;
}