#!perl
#####################################################################################
# Description: Generates coarse-grained interactions for a bead trajectory
#
# Authors: Reinier Akkermans (Accelrys)
# Version: 2.1 (February 2012)
# Modules: Materials Visualizer, Mesocite
#
# This scripts takes as input a bead trajectory (xtd) typically a coarse-grained
# atomistic trajectory obtained from a Molecular Dynamics simulation at constant 
# temperature using Forcite.
#
# The script creates a new force field with entries for each type in the trajectory. 
#
# For each bond/angle/nonbond between distinct types an interaction is introduced.
# The script calculates the distribution function for each interaction in the
# trajectory and converts this to a potential of mean force. The potential is
# fitted to a functional form provided.
#
# Required input:
# 1. Coarse-grained trajectory (coarse-grained atomistic trajectory)
# 2. Temperature
# 3. Functional form (e.g. Harmonic)
#
# Output documents:
# 1. Force field document containing the force field parameters
# 2. Study table containing all fitting data 
#####################################################################################
use strict;
use MaterialsScript qw(:all);
{
################################################################################
#  BEGIN USER INPUT                                                            #
################################################################################
# the trajectory to be analysed
my $doc = $Documents{"3+15C10 CG.xtd"};  # 轨迹的名称

# script settings
my $settings = Settings #设置
(
	UseBondStretch => "Yes", # 是否计算键拉伸
	FunctionalFormBondStretch => "Harmonic", # potential to use for bond stretch # 势函数
	LengthDistributionBinWidth => 0.01, # binwidth for length distribution (in A) 键长分布的间隔

	UseAngleBend => "Yes", # 是否计算键角
	FunctionalFormAngleBend => "Harmonic", # potential to use for angle bend
	AngleDistributionBinWidth => 1, #  binwidth for angle distribution (in deg)

	UseTorsion => "No", # unsupported as yet 计算扭转
	
	UseVanDerWaals => "Yes", # 是否计算范德华
	FunctionalFormVanDerWaals => "LJ_12_6", # potential to use for van der Waals 势函数
	RDFBinWidth => 0.1, #  bin width for radial distribution distribution (in A) 间隔
	RDFCutoff => 20, # maximum distance for the radial distribution distribution (in A) RDF最大的距离
	VanDerWaalsCombinationRule => "Arithmetic", # if "None" cross-terms are also evaluated 范德华组合规则 ，如果None，交叉项将被计算（我尝试改过，没有变化）
	
	Temperature => 353, # temperature at which the trajectory was created (in K) 轨迹的温度（单位K）
	
	DistributionCutoff => 0.02, # ignore points less than this fraction of maximum probability   RDF忽略低于这个值的点
	FitAccuracy => 0.1, # Stop fitting if deviations less than this fraction 如果偏差小于这个分数，停止拟合
);
################################################################################
#  END USER  INPUT                                                             #
################################################################################

Run($doc,$settings);
printf "Time taken: %d seconds", time()-$^T;
}

################################################################################
#  Main routine
################################################################################
sub Run
{
	my ($doc,$settings) = @_;

	# create a hash of the settings array for easy access
	my %s = Array2Hash($settings);
	
	# some constants   非键相互作用中KT的计算和单位
	my $kT = $s{Temperature}*8.314/4.184/1000; # kcal/mol
	my $analysis = Modules->Mesocite->Analysis;
	
	# prepare the structure for analysis         分析的结构
	my @types = PrepareStructure($doc);

	# create a new force field          创建一个新的力场
	my $off = Documents->New($doc->Name.".off");

	# set up the types in the force field          立场文件的内容或种类
	PrepareForcefield($off, \@types, $s{UseBondStretch},$s{UseAngleBend},$s{UseTorsion},$s{UseVanDerWaals});

	# the study table output document          输出文件
	my $std = Documents->New($doc->Name.".std");
	
	# prepare the columns, labels, and x-data
	PrepareStudytable($std);

	# fit the bonds, if used               计算键能参数
	if($off->UseBondStretch)
	{
		$analysis->ChangeSettings([LengthDistributionBinWidth => $s{LengthDistributionBinWidth}]);
	
		my %fitData = GetFitDataBondStretch($s{FunctionalFormBondStretch});
		my $formula = $fitData{"Formula"};
		
		my @typeSequences = PrepareBonds($doc);
		foreach my $typeSequence (@typeSequences)
		{			
			# analyze the trajectory and add the distribution to the table
			LengthDistribution($std, $doc, $typeSequence, $kT, $s{DistributionCutoff});	
	
			# estimate the parameters before the fit
			my %parameters = EstimateParametersBondStretch($std, $typeSequence, $kT, \%fitData);
			
			# fit the distribution data
			my $name = "bond " .  $typeSequence;
			FitParameters($std, $name, \%parameters, $formula, $s{FitAccuracy},100);
			
			# update force field
			UpdateForcefield($off, $typeSequence, \%parameters, \%fitData);
		}
	}

	# fit the angles, if used       计算键角参数
	if($off->UseAngleBend)
	{
		$analysis->ChangeSettings([AngleDistributionBinWidth => $s{AngleDistributionBinWidth}]);
	
		my %fitData = GetFitDataAngleBend($s{FunctionalFormAngleBend});
		my $formula = $fitData{"Formula"};
	
		my @typeSequences = PrepareAngles($doc);	
		foreach my $typeSequence (@typeSequences) 
		{			
			# analyze the trajectory and add the distribution to the table
			AngleDistribution($std, $doc, $typeSequence, $kT, $s{DistributionCutoff});	
	
			# estimate the parameters before the fit
			my %parameters = EstimateParametersAngleBend($std, $typeSequence, $kT, \%fitData);
			
			# fit the distribution data
			my $name = "angle " . $typeSequence;
			FitParameters($std, $name, \%parameters, $formula, $s{FitAccuracy}, 100);
	
			# update force field		
			UpdateForcefield($off, $typeSequence, \%parameters, \%fitData);
		}
	}
	
	# fit the non-bonds, if used       计算非键作用
	if($off->UseVanDerWaals)      力场中有范德华项
	{
		$analysis->ChangeSettings([
			RDFBinWidth => $s{RDFBinWidth},	RDFCutoff => $s{RDFCutoff},
			RDFComputeMolecularComponents => "Yes"]);          分析RDF
	
		my %fitData = GetFitDataVanDerWaals($s{FunctionalFormVanDerWaals});    拟合参数
		my $formula = $fitData{"Formula"};            拟合时使用的公式
		
		my $rule = $s{VanDerWaalsCombinationRule};        规则：范得华结合规则
		my $useCrossterms = $rule eq "None";                    计算交叉项等于none（不计算交叉项？？）
		$off->VanDerWaalsCombinationRule = $rule if $useCrossterms;

		my @typeSequences = PrepareNonBonds($doc,$useCrossterms);	
		foreach my $typeSequence (@typeSequences) 
		{	
			# analyze the trajectory and add the distribution to the table   统计RDF，计算势函数
			NonBondDistribution($std, $doc, $typeSequence, $kT, $s{DistributionCutoff});
	
			# estimate the parameters before the fit              势函数拟合
			my %parameters = EstimateParametersVanDerWaals($std, $typeSequence, $kT, \%fitData);

			# fit the distribution data             输出文件 谁和谁的非键作用，参数（势井深度，平衡距离）
			my $name = "non-bond " . $typeSequence;
			FitParameters($std, $name, \%parameters, $formula, $s{FitAccuracy},5);

			# update force field		  更新力场文件
			UpdateForcefield($off, $typeSequence, \%parameters, \%fitData);
		}
	}
	
	$doc->Discard;
}
#########################################################################
# Find all unique connectors and create sets
sub PrepareBonds
{
	my ($doc) = @_;
	
	my @names = ();
	my $connectors = $doc->UnitCell->BeadConnectors;
	foreach my $connector (@$connectors) 
	{
		my $bead1 = $connector->Bead1;
		my $bead2 = $connector->Bead2;
		# create a distance monitor for this connector
		my $distance = $doc->CreateDistance([$bead1,$bead2]);
		
		# name the monitor by sequence; use a fixed order
		my @types;
		push @types,$bead1->ForcefieldType;
		push @types,$bead2->ForcefieldType;
		my @typesSorted = sort(@types);
		my $name = $typesSorted[0].",".$typesSorted[1];
		$distance->Name = $name;
		push @names, $name;
	}

	# filter for unique ones
	my %hash = ();
	my @namesFiltered = grep(!$hash{$_}++, @names);

	my $distances = $doc->UnitCell->Distances;
	# create sets for each unique name
	foreach my $name (@namesFiltered) 
	{	 
		# filter all distance for the one we want
		my @distancesFiltered = ();
		foreach my $distance (@$distances)
		{
			if($distance->Name eq $name)
			{
				push @distancesFiltered, $distance;
			}
		}
		$doc->CreateSet($name, \@distancesFiltered); 
	}
	
	return @namesFiltered;	
}
#########################################################################
# Find all unique angles and create sets
sub PrepareAngles
{
	my ($doc) = @_;
	
	my @names = ();
	my $beads = $doc->UnitCell->Beads;
	foreach my $bead (@$beads) 
	{
		my $type2 = $bead->ForcefieldType;
	
		# loop over all pairs of neighbours
		my $attachedBeads = $bead->AttachedBeads;
		my $count = $attachedBeads->Count;
		for(my $i = 0; $i < $count-1; $i++)
		{
			my $bead1 = $attachedBeads->Item($i);
			my $type1 = $bead1->ForcefieldType;
			
			for(my $j = $i+1; $j < $count; $j++)
			{
				my $bead3 = $attachedBeads->Item($j);
				my $type3 = $bead3->ForcefieldType;

				# create an angle monitor for this angle
				my $angle = $doc->CreateAngle([$bead1,$bead,$bead3]);
				
				# name the monitor by sequence; use a fixed order
				my @types;
				push @types,$type1;
				push @types,$type3;
				my @typesSorted = sort(@types);
				my $name = $typesSorted[0].",".$type2.",".$typesSorted[1];
				$angle->Name = $name;
				push @names, $name
			}
		}
	}

	# filter for unique ones
	my %hash = ();
	my @namesFiltered = grep(!$hash{$_}++, @names);

	my $angles = $doc->UnitCell->Angles;
	# create sets for each unique name
	foreach my $name (@namesFiltered) 
	{	 

		# filter all distance for the one we want
		my @anglesFiltered = ();
		foreach my $angle (@$angles)
		{
			if($angle->Name eq $name)
			{
				push @anglesFiltered, $angle;
			}
		}
		
		$doc->CreateSet($name, \@anglesFiltered); 
	}

	return @namesFiltered;	
}
#########################################################################
# Create sets for each bead type                                          创建珠子的set
sub PrepareNonBonds               
{
	my ($doc,$useCrossTerms) = @_;
	
	# find all force field types                                                     
	my @types = ();
	my $beads = $doc->UnitCell->Beads;              找到文件中不同力场类型的珠子
	foreach my $bead (@$beads) 
	{
		my $type = $bead->ForcefieldType;
		push @types, $type;
	}
	# filter for unique ones                                     
	my %hash = ();
	my @typesFiltered = grep(!$hash{$_}++, @types);
	
	# create sets for each unique name                                创建名称
	foreach my $type (@typesFiltered) 
	{
		# filter all distance for the one we want
		my $set = $doc->CreateSet($type,[]);
		
		foreach my $bead (@$beads)
		{
			$set->Add($bead) if $bead->ForcefieldType eq $type
		}
	}

	# the self terms                                            同类珠子的计算
	my @typeSequences = ();
	my $count = scalar(@typesFiltered);	
	for(my $i = 0; $i < $count; $i++)
	{
		my $type = $typesFiltered[$i];
		push @typeSequences, $type . "," . $type;
	}

	# the cross terms, if used                                   交叉项的计算顺序
	if($useCrossTerms)
	{
		for(my $i = 0; $i < $count; $i++)
		{
			my $type1 = $typesFiltered[$i];
			for(my $j = $i+1; $j < $count; $j++)
			{
				push @typeSequences, $type1 . "," . $typesFiltered[$j];
			}
		}
	}
		
	return @typeSequences;	
}

################################################################################
# create new columns, add labels and x-data
sub PrepareStudytable
{
	my ($sheet) = @_;
	TrimSheet($sheet,0,5);
	$sheet->Title = "Summary";
	my $col = 0;
	$sheet->ColumnHeading($col++) = "Structure";
	$sheet->ColumnHeading($col++) = "Name";
	$sheet->ColumnHeading($col++) = "Distribution";
	$sheet->ColumnHeading($col++) = "a";
	$sheet->ColumnHeading($col++) = "b";
	$sheet->ColumnHeading($col++) = "c";	
}

####################################################################################
# Modifies the number of rows and columns of a sheet
sub TrimSheet
{
	my ($sheet,$nRow,$nCol) = @_;

	my $nRowDoc = $sheet->RowCount;
	if($nRowDoc > $nRow)
	{
		for(my $iRow = $nRowDoc-1; $iRow >= $nRow; $iRow--)
		{
			$sheet->DeleteRow($iRow);
		}
	}
	else
	{
		for (my $iRow = $nRowDoc; $iRow < $nRow; $iRow++)
		{
			$sheet->InsertRow($iRow);
		}		
	}

	my $nColDoc = $sheet->ColumnCount;
	if($nColDoc > $nCol)
	{
		for(my $iCol = $nColDoc-1; $iCol >= $nCol; $iCol--)
		{
			$sheet->DeleteColumn($iCol);
		}
	}
	else
	{
		for (my $iCol = $nColDoc; $iCol < $nCol; $iCol++)
		{
			$sheet->InsertColumn($iCol);
		}		
	}
}
#############################################################################
# set up the interactions, types and description    力场文件中包含的内容
sub PrepareForcefield
{
	my ($off,$types,$useBondStretch,$useAngleBend,$useTorsion,$useVanDerWaals) = @_;

	$off->Description .= "\nCoarse-grained force field for " . $off->Name ."\n\n";

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my $timeStamp = sprintf ("%4d-%02d-%02d %02d:%02d:%02d\n",$year+1900,$mon+1,$mday,$hour,$min,$sec);
	$off->Description .= "Created: $timeStamp\n\n";                         
	
	# create the types
	foreach my $type (@$types) 
	{
		$off->CreateType($type);
	}
	
	$off->UseBondStretch = $useBondStretch;
	$off->UseAngleBend = $useAngleBend;
	$off->UseTorsion = $useTorsion;
	$off->UseVanDerWaals = $useVanDerWaals;	
}
################################################################################
# ensures that each bead has a forcefield type assigned, creating new ones      保证所有珠子都有力场分配，如果没有创建一个新的力场
# if undefined; returns a list of unique forcefield types
sub PrepareStructure
{
	my ($doc) = @_;
	
	# collect names of all beads
	my $beads = $doc->UnitCell->Beads;
	my @names = ();
	foreach my $bead (@$beads) 
	{
		# if no force field types are defined, derive from bead type name
		my $name = $bead->ForcefieldType;
		if(length($name) <= 0)
		{
			my $beadTypeName = $bead->BeadTypeName;
					
			# the force field document restricts names to 5 characters
			$name = substr $beadTypeName, 0, 4;
			$bead->ForcefieldType = $name;
		}
	
		push @names, $name;
	}

	# filter for unique ones                     过滤独特的一个
	my %hash =();
	my @namesFiltered = grep(!$hash{$_}++, @names);
	
	return @namesFiltered;
}

################################################################################
# Calcalute the distribution function for a given set                 长度分布
sub LengthDistribution                              
{
	my ($std,$doc,$type,$kT,$probCutoff) = @_;
	
	my $name = "bond " . $type;
	
	my $analysis = Modules->Mesocite->Analysis->LengthDistribution($doc,Settings(
		LengthDistributionSetA => $type));
	
	my $stdA = $analysis->LengthDistributionChartAsStudyTable;
	my $rowCount = $stdA->RowCount;
	
	# fid the maximum probability
	my $maxProb = $stdA->Cell(0,"P");;
	for(my $row = 1; $row < $rowCount; $row++)
	{
		my $Prob = $stdA->Cell($row,"P");
		$maxProb = $Prob if $Prob > $maxProb;
	}
	
	# strip zeros
	my $threshold = $probCutoff*$maxProb;
	for(my $row = $rowCount-1; $row >= 0; $row--)
	{
		my $Prob = $stdA->Cell($row,"P");
		$stdA->DeleteRow($row) if $Prob <= $threshold;
	}
	$rowCount = $stdA->RowCount;
	die "no data points left; decrease probability cut off" if $rowCount == 0;
		
	# copy the distribution data to the results table
	my $sheet = $std->InsertSheet;
	$sheet->Title = $name;
	TrimSheet($sheet,$rowCount,1);
	$sheet->ColumnHeading(0) = "r (A)";
	my $rdfCol = $sheet->InsertColumn($sheet->ColumnCount, "P");	
	my $pmfCol = $sheet->InsertColumn($sheet->ColumnCount, "PMF (target)");
	for(my $row = 0; $row < $rowCount; $row++)
	{
		my $r = $stdA->Cell($row,"Distance");
		$sheet->Cell($row,0) = $r;
			
		my $Prob = $stdA->Cell($row,"P");
		$sheet->Cell($row,$rdfCol) = $Prob;
		
		# apply Jacobian correction			
		$Prob /= $r*$r;
		$sheet->Cell($row,$pmfCol) = -$kT*log($Prob);
	}
	
	# revert to master sheet
	$std->ActiveSheetIndex = 0;
	
	my $row = $std->InsertRow;
	my $tmp = Documents->New($doc->Name.".xsd");
	$tmp->CopyFrom($doc);
	KeepSet($tmp,$type);
	$std->Cell($row,"Structure") = $tmp;
	$tmp->Discard;
	$std->Cell($row,"Name") = $name;
	$std->Cell($row,"Distribution") = $analysis->LengthDistributionChart;
	
	# clean up unused documents
	$analysis->LengthDistributionChart->Delete;
	$analysis->LengthDistributionChartAsStudyTable->Delete;
}
################################################################################
# Calcalute the distribution function for a given set
sub AngleDistribution
{
 	use Math::Trig;
	my ($std,$doc,$type,$kT,$probCutoff) = @_;
	
	my $name = "angle " . $type;
	
	my $analysis = Modules->Mesocite->Analysis->AngleDistribution($doc,
		Settings(AngleDistributionSetA => $type));
	
	my $stdA = $analysis->AngleDistributionChartAsStudyTable;
	my $rowCount = $stdA->RowCount;
	# fid the maximum probability
	my $maxProb = $stdA->Cell(0,"P");;
	for(my $row = 1; $row < $rowCount; $row++)
	{
		my $Prob = $stdA->Cell($row,"P");
		if($Prob > $maxProb)
		{
			$maxProb = $Prob;
		}
	}
	my $threshold = $probCutoff*$maxProb;
	# strip zeros
	for(my $row = $rowCount-1; $row >= 0; $row--)
	{
		my $Prob = $stdA->Cell($row,"P");
		if($Prob <= $threshold)
		{
			$stdA->DeleteRow($row);
		}
	}
	$rowCount = $stdA->RowCount;
	if($rowCount == 0){die "no data points left; decrease probability cut off";}
	
	# copy the distribution data to the results table
	my $sheet = $std->InsertSheet();
	$sheet->Title = $name;
	$sheet->ColumnHeading(0) = "angle (deg)";
	my $rdfCol = $sheet->InsertColumn($sheet->ColumnCount, "P");	
	my $pmfCol = $sheet->InsertColumn($sheet->ColumnCount, "PMF (target)");
	for(my $row = 0; $row < $rowCount; $row++)
	{
		my $angleDeg = $stdA->Cell($row,"Angle");
		$sheet->Cell($row,0) = $angleDeg;
	
		# skip data points with zero weight
		my $Prob = $stdA->Cell($row,"P");
		$sheet->Cell($row,$rdfCol) = $Prob;
				
		# apply Jacobian correction			
		$Prob /= sin($angleDeg*pi/180.);
		$sheet->Cell($row,$pmfCol) = -$kT*log($Prob);
	}
	
	# revert to master sheet
	$std->ActiveSheetIndex = 0;

	my $row = $std->InsertRow;
	my $tmp = Documents->New($doc->Name.".xsd");
	$tmp->CopyFrom($doc);
	KeepSet($tmp,$type);	
	$std->Cell($row,"Structure") = $tmp;
	$tmp->Discard;
	$std->Cell($row,"Name") = $name;
	$std->Cell($row,"Distribution") = $analysis->AngleDistributionChart;

	# clean up unused documents
	$analysis->AngleDistributionChart->Delete;
	$analysis->AngleDistributionChartAsStudyTable->Delete;
}
################################################################################
# Calcalute the distribution function for a given set                  非键相互作用
sub NonBondDistribution
{
	my ($std,$doc,$type,$kT,$probCutoff) = @_;

	my $name = "non-bond " . $type;                名称谁和谁的非键作用
	
	my @types = split(',', $type);        
	my $results = Modules->Mesocite->Analysis->RadialDistributionFunction($doc,
		Settings(RDFSetA => $types[0], RDFSetB => $types[1]));            分析RDF
	
	my $stdA = $results->RDFChartAsStudyTable->Sheets("Inter");        分析的RDF中的Inter
	my $rowCount = $stdA->RowCount;
	# fid the maximum probability                                
	my $maxProb = $stdA->Cell(0,"g(r)");;
	for(my $row = 1; $row < $rowCount; $row++)                    设置r，g（r）
	{
		my $Prob = $stdA->Cell($row,"g(r)");
		$maxProb = $Prob if $Prob > $maxProb;
	}
	my $threshold = $probCutoff*$maxProb;             阈值等于截断半径乘以最大概率
	# strip zeros
	for(my $row = $rowCount-1; $row >= 0; $row--)
	{
		my $Prob = $stdA->Cell($row,"g(r)");
		if($Prob <= $threshold)           如果概率小于阈值
		{
			$stdA->DeleteRow($row);   删除
		}
	}
	$rowCount = $stdA->RowCount;
	if($rowCount == 0){die "no data points left; decrease probability cut off";}   如果行数等于0，输出报错信息
	
	# copy the distribution data to the results table     std文件中的内容，r（A）， P, PMF
	my $sheet = $std->InsertSheet();
	$sheet->Title = $name;
	$sheet->ColumnHeading(0) = "r (A)";
	my $rdfCol = $sheet->InsertColumn($sheet->ColumnCount, "P");	
	my $pmfCol = $sheet->InsertColumn($sheet->ColumnCount, "PMF (target)");
	for(my $row = 0; $row < $rowCount; $row++)
	{
		my $r = $stdA->Cell($row,"r");
		$sheet->Cell($row,0) = $r;
	
		# skip data points with zero weight         跳过一些为0的点
		my $Prob = $stdA->Cell($row,"g(r)");
		$sheet->Cell($row,$rdfCol) = $Prob;
				
		# apply Jacobian correction	应用雅克比修正项		
		$sheet->Cell($row,$pmfCol) = -$kT*log($Prob); 
	}
	
	# revert to master sheet
	$std->ActiveSheetIndex = 0;

	my $row = $std->InsertRow;
	my $tmp = Documents->New($doc->Name.".xsd");
	$tmp->CopyFrom($doc);
	KeepSet($tmp,$type);	
	$std->Cell($row,"Structure") = $tmp;
	$tmp->Discard;
	$std->Cell($row,"Name") = $name;
	$std->Cell($row,"Distribution") = $results->RDFChart;

	# clean up unused documents
	$results->RDFChart->Delete;
	$results->RDFChartAsStudyTable->Delete;
}
################################################################################
sub KeepSet
{
	my ($doc,$type) = @_;
	my $sets = $doc->UnitCell->Sets;
	foreach my $set (@$sets) 
	{
		if ($set->Name ne $type)
		{
			$set->Items->Delete;
		}
	}
}
################################################################################
sub KeepSet2
{
	my ($doc,$type1,$type2) = @_;
	my $sets = $doc->UnitCell->Sets;
	foreach my $set (@$sets) 
	{
		if ($set->Name ne $type1 && $set->Name ne $type2)
		{
			$set->Items->Delete;
		}
	}
}
################################################################################
sub EstimateParametersBondStretch
{
	my ($std,$type,$kT,$fitData) = @_;

	use constant{ TINY => 1E-12 };

	# collect the data for fitting
	my $sheet = $std->Sheets("bond " . $type);
	
	# get the average bond length, and average squared bond length
	my $xSqrAverage = 0;
	my $xAverage = 0;
	my $Ptot;
	for(my $row = 0; $row < $sheet->RowCount; $row++)
	{
		my $x = $sheet->Cell($row,0);
		my $P = $sheet->Cell($row,"P");
		$xSqrAverage += $x*$x*$P;
		$xAverage += $x*$P;
		$Ptot += $P;
	}
	die "Total probability too small" if $Ptot < TINY;
	$xSqrAverage /= $Ptot;
	$xAverage /= $Ptot;
	
	# for a Harmonic function: R0 = <r>, K0 = kT/(<r^2>-<r>^2)
	my %estimatePars;
	$estimatePars{"R0"} = $xAverage;
	$estimatePars{"K0"} = $kT/($xSqrAverage-$xAverage*$xAverage);
	$estimatePars{"dummy"} = 0;

	my %parameters;
	foreach my $par (keys %$fitData) # a,b,c
	{
		my $value = $fitData->{$par}; # R0,K0
		if(exists $estimatePars{$value})
		{
			$parameters{$par} = $estimatePars{$value};
		}
	}	
	return %parameters;
}
################################################################################
sub EstimateParametersAngleBend
{
	my ($std,$type,$kT,$fitData) = @_;

 	use Math::Trig;
	use constant{ TINY => 1E-12 };
	
	# collect the data for fitting
	my $sheet = $std->Sheets("angle " . $type);
	
	# get the average angle, and average squared angle
	my $xSqrAverage = 0;
	my $xAverage = 0;
	my $Ptot = 0;
	for(my $row = 0; $row < $sheet->RowCount; $row++)
	{
		my $x = $sheet->Cell($row,0);
		my $P = $sheet->Cell($row,"P");
		$xSqrAverage += $x*$x*$P;
		$xAverage += $x*$P;
		$Ptot += $P;
	}
	die "Total probability too small" if $Ptot < TINY;
	$xSqrAverage /= $Ptot;
	$xAverage /= $Ptot;
	
	# for a Harmonic function: T0 = <T>, K0 = kT/(<T^2>-<T>^2)*(180/pi)^2
	my %estimatePars;
	$estimatePars{"T0"} = $xAverage;
	$estimatePars{"K0"} = $kT/($xSqrAverage-$xAverage*$xAverage)*(180/pi)**2;
	$estimatePars{"dummy"} = 0;
	
	my %parameters;
	foreach my $par (keys %$fitData) # a,b,c
	{
		my $value = $fitData->{$par}; # R0,K0
		if(exists $estimatePars{$value})
		{
			$parameters{$par} = $estimatePars{$value};
		}
	}	
	return %parameters;
}
################################################################################
sub EstimateParametersVanDerWaals        估算范得华作用参数
{
	my ($std,$type,$kT,$fitData) = @_;

	use constant{ TINY => 1E-12 };    常数（10的-12次方）

	# collect the data for fitting
	my $sheet = $std->Sheets("non-bond " . $type);
	
	# get the data point corresponding maximum of g(r)
	my $Rmax = $sheet->Cell(0,"r (A)");
	my $Pmax = $sheet->Cell(0,"P");
	for(my $row = 1; $row < $sheet->RowCount; $row++)
	{
		my $P = $sheet->Cell($row,"P");
		if($P > $Pmax)
		{
			$Rmax = $sheet->Cell($row,0);
			$Pmax = $P;		
		}
	}

	# for LJ, R0 is about the maximum
	my %estimatePars;
	$estimatePars{"R0"} = $Rmax;                  R0等于Rmax等于Cell(0,"r (A)")
	$estimatePars{"D0"} = $kT*log($Pmax);      D0等于KTlog（Pmax）
	$estimatePars{"dummy"} = 0;

	my %parameters;
	foreach my $par (keys %$fitData) # a,b,c
	{
		my $value = $fitData->{$par}; # R0,K0
		if(exists $estimatePars{$value})
		{
			$parameters{$par} = $estimatePars{$value};
		}
	}	
	return %parameters;
}

################################################################################
sub FitParameters
{
	my ($std,$type,$parameters,$formula,$relativeAccuracy,$maxIterations) = @_;
	
	# collect the data for fitting
	my $sheet = $std->Sheets($type);
	
	my @xData = ();
	my @yData = ();
	my @wData = ();
	for(my $row = 0; $row < $sheet->RowCount; $row++)
	{
		my $pmf = $sheet->Cell($row,"PMF (target)");
		if(defined($pmf))
		{		
			push @xData, $sheet->Cell($row,0);		
			push @yData, $pmf;
			
			# weight the data proportional to the target rdf.
			my $rdf = $sheet->Cell($row,"P");
			push @wData, $rdf;
		}			
	}
	
	# fit the data
	my @yDataFit = FitDataWeighted(\@xData,\@yData,\@wData,$formula,$parameters,$relativeAccuracy,$maxIterations);
	
	# add the fitted function to the study table
	my $fitCol = $sheet->InsertColumn($sheet->ColumnCount, "PMF (fit)");
	my $iData = 0;
	for(my $row = 0; $row < $sheet->RowCount; $row++)
	{
		my $pmf = $sheet->Cell($row,"PMF (target)");
		if(defined($pmf))
		{
			$sheet->Cell($row,$fitCol) = $yDataFit[$iData];
			$iData++;
		}
	}
	
	# find the row in the studytable for this type
	my $sheet = $std->Sheets("Summary");
	my $rowType;
	for(my $row = 0; $row < $sheet->RowCount; $row++)
	{
		if($sheet->Cell($row,"Name") eq $type)
		{
			$rowType = $row;
		}
	}
	
	if(!defined($rowType)){die;}
	
	# copy the parameters array to studytable
	foreach my $par (keys %$parameters) # a,b,c
	{
		$sheet->Cell($rowType,$par) = $parameters->{$par};
	}	
}
################################################################################
sub UpdateForcefield
{
	my ($off,$type,$parameters,$fitData) = @_;

	my $ffTerm = $off->CreateTerm($fitData->{"InteractionSet"}, $type, $fitData->{"FunctionalForm"});
   
	while ((my $key, my $value) = each(%$parameters))
	{
	     my $FFkey = $fitData->{$key};
	     $ffTerm->$FFkey = abs($value) if $FFkey ne "dummy";
	}
}
################################################################################
sub FitDataWeighted
{
	my ($xData,$yData,$wData,$formula,$parameters,$relativeAccuracy,$maxIterations) = @_;

	use Math::Symbolic;
	use Algorithm::CurveFit;
	use List::Util qw[max];
	
	# get the minimal weight
	my $wDataMax = $wData->[0];
	for(my $iData = 1; $iData < scalar(@$wData); ++$iData)
	{
		if(defined($yData->[$iData]))
		{
			my $w = $wData->[$iData];
			if( $w  > $wDataMax)
			{
				$wDataMax = $w;
			}			
		}
	}
	
	# duplicate data points proportional to weight; ignore data points below minimal weight
	my $duplMax = 100; # maximum number of duplication
	my @xDataW;
	my @yDataW;
	for(my $iData = 0; $iData < scalar(@$xData); ++$iData)
	{
		if(defined($yData->[$iData]))
		{
			my $dupl = int($wData->[$iData]/$wDataMax*$duplMax);
			if($dupl > 0)
			{
				for(my $i = 0; $i < $dupl; $i++)
				{
					push @xDataW, $xData->[$iData];
					push @yDataW, $yData->[$iData];
				}
			}
		}
	}

	# create the parameters table as expected by the library function	
	my @pars;
	foreach my $par (keys %$parameters) # a,b,c
	{
		my $value = $parameters->{$par};
		my $accuracy = max(0.001,$relativeAccuracy*$value);
		my $array = [$par,$value,$accuracy];
		push @pars,$array;
	}  
	
	my $func = Math::Symbolic->parse_from_string($formula);
	# do the fit
	my $variable = 'x';
	my $square_residual = Algorithm::CurveFit->curve_fit(
	    formula            => $formula, # may be a Math::Symbolic tree instead
	    params             => \@pars,
	    variable           => $variable,
	    xdata              => \@xDataW,
	    ydata              => \@yDataW,
	    maximum_iterations => $maxIterations,
	);

	# create the parameters table as expected by the library function	
	foreach my $row (@pars)
	{
		$parameters->{$row->[0]} = $row->[1];
	}

	# need to modify this if using function with more or less parameters
	my @yDataFit;
	for(my $iData = 0; $iData < scalar(@$xData); ++$iData)
	{
		my $x = $xData->[$iData];
		push @yDataFit, $func->value(
			a => $parameters->{"a"}, 
			b => $parameters->{"b"}, 
			c => $parameters->{"c"}, 
			x => $x);
	}
	
	return @yDataFit	
}


################################################################################
#  creates a hash from an array with key-value elements
sub Array2Hash
{
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
#  returns fit parameters
sub GetFitDataBondStretch
{
	my ($functionalForm) = @_;
	
	my %fitData = ("InteractionSet","Bond Stretch");
	$fitData{"FunctionalForm"} = $functionalForm;	
	if($functionalForm == "Harmonic")
	{	
		$fitData{"Formula"} = "a*(x-b)^2+c";	
		$fitData{"a"} = "K0";
		$fitData{"b"} = "R0";
		$fitData{"c"} = "dummy";		
	}
	else
	{
		die "Functional form is not supported for bond stretch"
	}
	return %fitData;
}
################################################################################
#  returns fit parameters
sub GetFitDataAngleBend
{
	my ($functionalForm) = @_;
	
	my %fitData;
	my %fitData = ("InteractionSet","Angle Bend");
	$fitData{"FunctionalForm"} = $functionalForm;	
	if($functionalForm == "Harmonic")
	{
		$fitData{"Formula"} = "a*(x-b)^2/3282.81+c"; # 3282.81 = (180/pi)^2	
		$fitData{"a"} = "K0";
		$fitData{"b"} = "T0";
		$fitData{"c"} = "dummy";
	}
	else
	{
		die "Functional form is not supported for angle bend"
	}
	return %fitData;	
}
################################################################################
#  returns fit parameters
sub GetFitDataVanDerWaals     范得华作用公式  LJ_12_6，函数形式
{
	my ($functionalForm) = @_;
	
	my %fitData;
	my %fitData = ("InteractionSet","van der Waals");
	$fitData{"FunctionalForm"} = $functionalForm;	
	if($functionalForm == "LJ_12_6")
	{
		# to avoid negative energies, use absolute value of a
		$fitData{"Formula"} = "sqrt(a*a)*((b/x)^12-2*(b/x)^6)";
		$fitData{"a"} = "D0";
		$fitData{"b"} = "R0";
	}
	if($functionalForm == "LJ_12_4")
	{
		# to avoid negative energies, use absolute value of a
		$fitData{"Formula"} = "sqrt(a*a)*(0.5*(b/x)^12-1.5*(b/x)^4)";
		$fitData{"a"} = "D0";
		$fitData{"b"} = "R0";
	}
	if($functionalForm == "LJ_9_6")
	{
		# to avoid negative energies, use absolute value of a
		$fitData{"Formula"} = "sqrt(a*a)*(2*(b/x)^9-3*(b/x)^6)";
		$fitData{"a"} = "D0";
		$fitData{"b"} = "R0";
	}
	if($functionalForm == "LJ_9_4")
	{
		# to avoid negative energies, use absolute value of a
		$fitData{"Formula"} = "sqrt(a*a)*(0.8*(b/x)^9-1.8*(b/x)^4)";
		$fitData{"a"} = "D0";
		$fitData{"b"} = "R0";
	}
	else
	{
		die "Functional form is not supported for van der Waals"
	}
	return %fitData;	
}